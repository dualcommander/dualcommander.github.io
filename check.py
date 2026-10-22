"""Check static page assets without installing dependencies: python3 check.py."""
from html.parser import HTMLParser
from pathlib import Path
import json
import struct
from urllib.parse import unquote, urlsplit

root = Path(__file__).resolve().parent


class PageCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.icons = set()
        self.screenshots = 0
        self.ids = set()
        self.links = []
        self.command = None
        self.commands = []
        self.hints = 0
        self.config = None
        self.configs = {}
        self.in_contents = False
        self.contents_depth = 0
        self.contents = []
        self.headings = []
        self.dark_screenshots = []
        self.theme_options = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "option":
            self.theme_options.append(attrs.get("value"))
        if tag == "source" and "data-dark" in attrs:
            self.dark_screenshots.append(attrs["srcset"])
        if tag == "nav" and "contents" in attrs.get("class", "").split():
            self.in_contents = True
        if self.in_contents:
            if tag == "ul":
                self.contents_depth += 1
            if tag == "a":
                self.contents.append((attrs["href"], self.contents_depth))
        if tag == "h3" and "id" in attrs:
            self.headings.append(("#" + attrs["id"], 2))
        if tag == "section" and "id" in attrs:
            self.headings.append(("#" + attrs["id"], 1))
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs["id"])
        if "href" in attrs:
            self.links.append(attrs["href"])
        if tag == "a" and "pin" in attrs.get("class", "").split():
            assert attrs.get("aria-label"), "Screenshot hint needs accessible label"
            self.hints += 1
        if tag == "code" and attrs.get("class") == "command-example":
            self.command = ""
        if tag == "code" and attrs.get("class") == "config-example":
            self.config = attrs["data-file"]
            self.config_text = ""
        for key in ("src", "href", "srcset"):
            url = urlsplit(attrs.get(key, ""))
            if not url.scheme and not url.netloc and url.path:
                assert (root / unquote(url.path)).exists(), f"Missing asset: {url.path}"
        if tag == "link" and attrs.get("rel") in ("icon", "apple-touch-icon"):
            self.icons.add(attrs["href"])
        if tag == "img":
            assert attrs.get("alt") or attrs.get("alt") == "", "Image needs alt attribute"
            data = (root / attrs["src"]).read_bytes()
            assert data[:8] == b"\x89PNG\r\n\x1a\n", "Expected PNG"
            width, height = struct.unpack(">II", data[16:24])
            if attrs["src"].startswith("screenshots/"):
                assert attrs["alt"], "Screenshot needs descriptive alt text"
                assert (width, height) == (int(attrs["width"]), int(attrs["height"]))
                self.screenshots += 1

    def handle_data(self, data):
        if self.config is not None:
            self.config_text += data
        if self.command is not None:
            self.command += data

    def handle_endtag(self, tag):
        if self.in_contents and tag == "ul":
            self.contents_depth -= 1
        if tag == "nav":
            self.in_contents = False
        if tag == "code" and self.config is not None:
            self.configs[self.config] = json.loads(self.config_text)
            self.config = None
        if tag == "code" and self.command is not None:
            args = json.loads(self.command)
            assert isinstance(args, list) and args, "Command needs executable"
            assert all(isinstance(arg, str) and arg and "\0" not in arg for arg in args)
            assert "{path}" in self.command or "{dir}" in self.command or args == ["powershell.exe", "-NoExit"]
            self.commands.append(args)
            self.command = None


pages = {}
for path in sorted(root.glob("*.html")):
    page = PageCheck()
    page.feed(path.read_text())
    assert {"dualcommander.png", "favicon.ico", "apple-touch-icon.png"} <= page.icons
    assert page.theme_options == ["system", "light", "dark"], "Missing theme choices"
    assert 'src="theme.js"' in path.read_text() and 'href="theme.css"' in path.read_text()
    assert len(page.dark_screenshots) == page.screenshots, "Each screenshot needs a dark capture"
    for screenshot in page.dark_screenshots:
        light = screenshot.replace("-dark", "-light" if screenshot.startswith("screenshots/dualcommander-") else "")
        assert (root / screenshot).read_bytes()[16:24] == (root / light).read_bytes()[16:24], "Theme captures need matching dimensions"
    pages[path.name] = page

for name, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc or not url.fragment:
            continue
        target = unquote(url.path) or name
        assert target in pages, f"Unknown fragment target page: {link}"
        assert unquote(url.fragment) in pages[target].ids, f"Broken fragment in {name}: {link}"

page = pages["index.html"]
html = (root / "index.html").read_text()
assert html.split("</h1>", 1)[1].lstrip().startswith('<figure id="screenshots">'), "Screenshot must immediately follow main heading"
assert page.screenshots == 1, "Expected one theme-matched screenshot"
assert "manual.html" in page.links, "Home page must link to manual"
manual = pages["manual.html"]
assert manual.contents == manual.headings, "TOC must match section order and subsection hierarchy"
assert manual.screenshots == 2, "Manual needs pane and settings screenshots"
assert manual.hints == 13, "Expected eight pane hints and five settings hints"
assert len(manual.commands) >= 12, "Missing editor/terminal examples"
assert ["open", "-na", "ITerm", "{dir}"] in manual.commands
assert set(manual.configs) == {"settings.json", "favourites.json", "state.json"}
settings = manual.configs["settings.json"]
assert settings["appearance"] == {"theme": "system", "density": "standard", "fontSize": "medium"}
assert isinstance(settings["views"]["left"]["brief"], bool)
assert isinstance(settings["views"]["right"]["brief"], bool)
assert isinstance(settings["views"]["showHidden"], bool)
assert isinstance(settings["deletion"]["moveToTrash"], bool)
assert isinstance(settings["archives"]["browse"], bool)
assert set(settings["externalApplications"]) == {"revealCommand", "terminalCommand", "editorCommand", "compareFilesCommand", "compareFoldersCommand"}
assert all(isinstance(value, str) for value in settings["externalApplications"].values())
assert all(isinstance(path, str) and path.startswith("/") for path in manual.configs["favourites.json"])
state = manual.configs["state.json"]
assert state["pane"]["active"] in ("left", "right")
assert all(isinstance(state["pane"][side]["path"], str) for side in ("left", "right"))
assert all(0 < state["window"][key] <= 100000 for key in ("width", "height"))
assert (root / "favicon.ico").read_bytes()[:4] == b"\x00\x00\x01\x00"
print("All pages: assets, screenshot dimensions, favicon links, anchors, hints, command JSON, and config samples passed")