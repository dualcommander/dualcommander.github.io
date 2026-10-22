# DualCommander website

Static site for https://dualcommander.github.io/. No build tools, tracking, or
external fonts. A small local script remembers System / Light / Dark in browser
storage and matches screenshots to the active theme. Without JavaScript, pages
and screenshots follow the system theme. `dualcommander.png` is copied from the app's assets.
`manual.html` is the online user manual, linked from the home page. It includes
numbered, linked screenshot hints and shell-free JSON editor/terminal examples.
`favicon.ico` (16, 32, and 48 pixels) and `apple-touch-icon.png` (180 pixels)
use the same app icon. `screenshots/dualcommander.png` overlaps full app-rendered
dark and light previews with document sample files, brief view left and detailed view right.
The home page uses `screenshots/dualcommander-light.png` or
`screenshots/dualcommander-dark.png`; the overlapping composition is retained as
`screenshots/dualcommander.png`. Top controls and bottom bars are included;
native OS decorations are not.
Regenerate from the app repository with:

```sh
WEBSITE_SCREENSHOT="$PWD/../dualcommander.github.io/screenshots/dualcommander.png" go test ./internal/commander -run '^TestWebsiteScreenshot$' -count=1
```

Refresh icons from the same app checkout (ImageMagick required):

```sh
cp assets/dualcommander.png ../dualcommander.github.io/dualcommander.png
magick assets/dualcommander.png -define icon:auto-resize=48,32,16 ../dualcommander.github.io/favicon.ico
magick assets/dualcommander.png -resize 180x180 ../dualcommander.github.io/apple-touch-icon.png
```

Keep image dimensions in `index.html` in sync when replacing screenshots.
Regenerate the manual's pane/settings captures from the app repository:

```sh
MANUAL_SCREENSHOTS="$PWD/../dualcommander.github.io/screenshots" go test ./internal/commander -run '^TestManualScreenshots$' -count=1
```

Keep `manual.html` image dimensions and percentage-positioned hints aligned with
the captures. Both commands also generate matching `-dark.png` variants (and
`-light.png` for the home preview). Captures use isolated sample files and in-memory preferences;
they do not change your settings. The settings capture shows the complete form.
Keep feature copy and shortcuts aligned with the app README; archive browsing
remains read-only. The Pages workflow runs `check.py` before deployment.

## Preview

From this repository root, run `python3 -m http.server 8000`, then open
http://localhost:8000/.

Run `python3 check.py` to check every page's local assets, screenshot dimensions,
favicon links, fragment targets, numbered hints, and example command JSON.
Run `node theme.test.cjs` to check theme selection, storage, system changes, and
screenshot switching without installing dependencies.

## Publish

1. In `dualcommander/dualcommander.github.io` on GitHub, open **Settings > Pages**
   and set **Source** to **GitHub Actions**.
2. Push these files to `main`. The Pages workflow deploys the site, or run
   **Deploy GitHub Pages** manually from Actions.

The repository, organization, and executable are named `dualcommander`;
the application display name is **DualCommander**.