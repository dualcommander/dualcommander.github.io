// Run with: node theme.test.cjs
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

function page(saved, dark = false, blocked = false, storage = { value: saved }) {
  const events = {};
  const select = { addEventListener: (name, callback) => { events[name] = callback; } };
  const picker = { hidden: true };
  const meta = {};
  const link = {};
  const source = {
    srcset: "dark.png",
    parentElement: {
      closest: () => link,
      querySelector: () => ({ getAttribute: () => "light.png" }),
    },
  };
  const root = { dataset: {} };
  const system = { matches: dark, addEventListener: (name, callback) => { events.system = callback; } };
  vm.runInNewContext(fs.readFileSync(`${__dirname}/theme.js`, "utf8"), {
    matchMedia: () => system,
    localStorage: {
      getItem() { if (blocked) throw Error("blocked"); return storage.value; },
      setItem(key, value) { if (blocked) throw Error("blocked"); storage.value = value; },
    },
    document: {
      documentElement: root,
      querySelector: selector => selector === "#theme" ? select : selector === ".theme-picker" ? picker : meta,
      querySelectorAll: () => [source],
      addEventListener: (name, callback) => { events[name] = callback; },
    },
    window: { addEventListener: (name, callback) => { events[name] = callback; } },
  });
  events.DOMContentLoaded();
  return { events, root, select, picker, source, link, meta, system, saved: () => storage.value };
}

const p = page(null, true);
assert.equal(p.select.value, "system");
assert.equal(p.picker.hidden, false);
assert.equal(p.root.dataset.theme, "dark");
assert.equal(p.source.media, "all");
assert.equal(p.link.href, "dark.png");
p.events.change({ target: { value: "light" } });
assert.equal(p.saved(), "light");
assert.equal(p.root.dataset.theme, "light");
assert.equal(p.source.media, "not all");
assert.equal(p.link.href, "light.png");
assert.equal(p.meta.content, "#ffffff");
p.events.system();
assert.equal(p.root.dataset.theme, "light");
p.events.change({ target: { value: "dark" } });
assert.equal(p.root.dataset.theme, "dark");
p.events.change({ target: { value: "system" } });
p.system.matches = false;
p.events.system();
assert.equal(p.root.dataset.theme, "light");
p.events.storage({ key: "theme", newValue: "dark" });
assert.equal(p.root.dataset.theme, "dark");
p.events.storage({ key: null, newValue: null });
assert.equal(p.select.value, "system");
assert.equal(page("light", true).root.dataset.theme, "light");
assert.equal(page("dark").root.dataset.theme, "dark");
assert.equal(page("invalid", true).select.value, "system");
const blocked = page(null, false, true);
blocked.events.change({ target: { value: "dark" } });
assert.equal(blocked.root.dataset.theme, "dark");
blocked.events.pageshow();
assert.equal(blocked.root.dataset.theme, "dark");
for (const dark of [false, true]) {
  const storage = { value: null };
  const home = page(null, dark, false, storage);
  for (const choice of ["dark", "light", "system"]) {
    home.events.change({ target: { value: choice } });
    const manual = page(null, dark, false, storage);
    const theme = choice === "system" ? (dark ? "dark" : "light") : choice;
    assert.equal(manual.select.value, choice);
    assert.equal(manual.root.dataset.theme, theme);
    manual.events.change({ target: { value: choice === "dark" ? "light" : "dark" } });
    home.events.pageshow();
    assert.equal(home.select.value, manual.select.value);
    assert.equal(home.root.dataset.theme, manual.root.dataset.theme);
    assert.equal(home.source.media, manual.source.media);
    assert.equal(home.link.href, manual.link.href);
    storage.value = choice;
    home.events.pageshow();
    assert.equal(home.select.value, choice);
    assert.equal(home.root.dataset.theme, theme);
  }
}
console.log("Theme choices, cross-page navigation, cached-page restoration, OS changes, screenshots, cross-tab sync, and blocked storage passed");