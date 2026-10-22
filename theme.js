(() => {
  const system = matchMedia("(prefers-color-scheme: dark)");
  const valid = value => ["system", "light", "dark"].includes(value);
  let choice = "system";
  function restore() {
    try {
      const saved = localStorage.getItem("theme");
      choice = valid(saved) ? saved : "system";
    } catch {}
    apply();
  }

  function apply() {
    const theme = choice === "system" ? (system.matches ? "dark" : "light") : choice;
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]').content = theme === "dark" ? "#181818" : "#ffffff";
    document.querySelectorAll("picture source[data-dark]").forEach(source => {
      source.media = theme === "dark" ? "all" : "not all";
      const picture = source.parentElement;
      const link = picture.closest("a");
      if (link) link.href = theme === "dark" ? source.srcset : picture.querySelector("img").getAttribute("src");
    });
    const select = document.querySelector("#theme");
    if (select) select.value = choice;
  }

  restore();
  document.addEventListener("DOMContentLoaded", () => {
    apply();
    document.querySelector(".theme-picker").hidden = false;
    document.querySelector("#theme").addEventListener("change", event => {
      if (!valid(event.target.value)) return;
      choice = event.target.value;
      try { localStorage.setItem("theme", choice); } catch {}
      apply();
    });
  });
  system.addEventListener("change", apply);
  window.addEventListener("pageshow", restore);
  window.addEventListener("storage", event => {
    if (event.key !== "theme" && event.key !== null) return;
    choice = valid(event.newValue) ? event.newValue : "system";
    apply();
  });
})();