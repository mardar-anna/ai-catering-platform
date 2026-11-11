// The accessibility menu (תפריט נגישות), on every page. A plain script loaded in <head>,
// not a module, so saved choices apply before the first paint. Choices live in this
// browser only (localStorage) and become classes on <html>; css/a11y.css does the rest.
// Our own code, no third-party widget: pages holding an order token load nothing else.
(() => {
  const KEY = "a11y";
  const root = document.documentElement;
  const SIZES = [["0", "רגיל"], ["1", "גדול"], ["2", "גדול מאוד"], ["3", "הכי גדול"]];
  const TOGGLES = [
    ["contrast", "ניגודיות גבוהה"],
    ["links", "הדגשת קישורים וכפתורים"],
    ["readable", "גופן קריא ומרווח"],
    ["motion", "עצירת אנימציות וסרטונים"],
    ["focus", "הדגשת המיקוד במקלדת"],
  ];

  const load = () => {
    try { return JSON.parse(localStorage.getItem(KEY)) ?? {}; } catch { return {}; }
  };
  const save = (prefs) => {
    try { localStorage.setItem(KEY, JSON.stringify(prefs)); } catch { /* private mode: this page only */ }
  };

  let prefs = load();

  function apply() {
    for (const [size] of SIZES) root.classList.toggle(`a11y-text-${size}`, size !== "0" && prefs.text === size);
    for (const [name] of TOGGLES) root.classList.toggle(`a11y-${name}`, prefs[name] === true);
    document.dispatchEvent(new CustomEvent("a11y:change", { detail: { ...prefs } }));
  }
  apply();

  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [name, value] of Object.entries(attrs)) {
      if (name.startsWith("on")) node.addEventListener(name.slice(2), value);
      else if (name in node) node[name] = value;
      else node.setAttribute(name, value);
    }
    node.append(...children);
    return node;
  }
  const icon = (name) => el("span", { className: `icon icon-${name}`, "aria-hidden": "true" });

  // The panel exists only while open, so it never mixes with the page's own dialogs.
  function openPanel(opener) {
    const sizeInputs = SIZES.map(([value, label]) => el("label", { className: "a11y-size" },
      el("input", { type: "radio", name: "a11y-text", value, checked: value === (prefs.text ?? "0"), onchange: () => update({ text: value }) }),
      el("span", {}, label)));
    const toggleInputs = TOGGLES.map(([name, label]) => el("label", { className: "a11y-toggle" },
      el("input", { type: "checkbox", name: `a11y-${name}`, checked: prefs[name] === true, onchange: (event) => update({ [name]: event.target.checked }) }),
      el("span", {}, label)));
    const status = el("p", { className: "visually-hidden", role: "status" });

    const panel = el("dialog", { className: "a11y-panel", "aria-labelledby": "a11y-title" },
      el("div", { className: "a11y-head" },
        el("h2", { id: "a11y-title" }, icon("accessibility"), "התאמות נגישות"),
        el("button", { type: "button", className: "icon-button", "aria-label": "סגירת תפריט הנגישות", onclick: () => panel.close() }, icon("close"))),
      el("fieldset", {}, el("legend", {}, "גודל הטקסט"), el("div", { className: "a11y-sizes" }, ...sizeInputs)),
      el("fieldset", {}, el("legend", { className: "visually-hidden" }, "התאמות תצוגה"), ...toggleInputs),
      el("div", { className: "a11y-foot" },
        el("button", { type: "button", className: "secondary", onclick: reset }, "איפוס ההתאמות"),
        el("a", { href: "/accessibility/" }, "הצהרת נגישות")),
      status);

    function update(change) {
      prefs = { ...prefs, ...change };
      save(prefs);
      apply();
    }
    function reset() {
      prefs = {};
      save(prefs);
      apply();
      for (const input of panel.querySelectorAll("input")) input.checked = input.value === "0";
      status.textContent = "ההתאמות אופסו";
    }

    panel.addEventListener("close", () => { panel.remove(); opener.focus(); });
    // A click on the backdrop (outside the panel's box) closes it.
    panel.addEventListener("click", (event) => {
      if (event.target !== panel) return;
      const box = panel.getBoundingClientRect();
      const inside = event.clientX >= box.left && event.clientX <= box.right && event.clientY >= box.top && event.clientY <= box.bottom;
      if (!inside) panel.close();
    });
    document.body.append(panel);
    panel.showModal();
  }

  function build() {
    const opener = el("button", {
      type: "button", className: "a11y-opener", "aria-label": "תפריט נגישות", "aria-haspopup": "dialog",
    }, icon("accessibility"));
    opener.addEventListener("click", () => openPanel(opener));
    // Early in the tab order: right after the skip link, before the page itself.
    const skip = document.querySelector(".skip-link");
    if (skip) skip.after(opener);
    else document.body.prepend(opener);
  }

  // A skip link with data-target moves focus there (the customer page wires its own).
  function wireSkipLink() {
    const skip = document.querySelector(".skip-link[data-target]");
    skip?.addEventListener("click", () => document.querySelector(skip.dataset.target)?.focus());
  }

  const ready = () => { build(); wireSkipLink(); };
  if (document.body) ready();
  else document.addEventListener("DOMContentLoaded", ready);
})();
