// The accessibility statement page: fills in the site caterer's name and phone.
// Without them (or without JS) the page still reads correctly, with "העסק" as the name.
import { api } from "/js/api.js";

async function fillCaterer() {
  try {
    const { site_caterer: slug } = await api("/api/config");
    if (!slug) return;
    const caterer = await api(`/api/c/${encodeURIComponent(slug)}`);
    document.title = `הצהרת נגישות | ${caterer.name}`;
    for (const node of document.querySelectorAll("[data-caterer-name]")) node.textContent = caterer.name;
    if (caterer.contact_phone) {
      const link = document.querySelector("[data-phone]");
      link.href = `tel:${caterer.contact_phone.replace(/\s/g, "")}`;
      link.querySelector("bdi").textContent = caterer.contact_phone;
      document.querySelector("[data-phone-line]").hidden = false;
    }
  } catch {
    // The statement itself is static; a failed lookup only leaves the generic name.
  }
}

fillCaterer();
