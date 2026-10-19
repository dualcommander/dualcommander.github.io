"""Check static page assets without installing dependencies: python3 check.py."""
from html.parser import HTMLParser
from pathlib import Path
import struct
from urllib.parse import unquote, urlsplit

root = Path(__file__).resolve().parent


class PageCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.icons = set()
        self.screenshots = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("src", "href"):
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


page = PageCheck()
html = (root / "index.html").read_text()
page.feed(html)
assert html.split("</h1>", 1)[1].lstrip().startswith('<figure id="screenshots">'), "Screenshot must immediately follow main heading"
assert page.screenshots == 1, "Expected one composed screenshot"
assert {"dualcommander.png", "favicon.ico", "apple-touch-icon.png"} <= page.icons
assert (root / "favicon.ico").read_bytes()[:4] == b"\x00\x00\x01\x00"
print("Page assets, screenshot dimensions, and favicon links passed")