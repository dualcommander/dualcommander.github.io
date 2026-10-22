# DualCommander website

Static site and user manual: https://dualcommander.github.io/.

Preview: `python3 -m http.server 8000`, then open http://localhost:8000/.

Checks:

```sh
python3 check.py
node theme.test.cjs
```

Deploys on push to `main`. GitHub **Settings → Pages → Source** must be **GitHub Actions**.
