"""Accessibility: the accessibility menu, the statement page, the hero video's pause button,
and an axe-core scan of every page. Tests run in order on one browser session.

axe-core comes from the axe-playwright-python package and is injected by the test, never
served by the app: `uv run --with playwright --with axe-playwright-python pytest ../e2e`.
"""

import re

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

from conftest import PHONE, SHOTS, call

EVENT_DAY = "2031-01-07"  # A Tuesday.
TUESDAY = 2
# WCAG 2.0, 2.1 and 2.2 at levels A and AA. IS 5568 adopts WCAG 2.0 AA.
WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
AXE = Axe()


@pytest.fixture(scope="module", autouse=True)
def seeded_menu(base_url):
    token = call(base_url, "/auth/v1/token", {"password": "right"})["access_token"]

    def admin(path, body, method="POST"):
        return call(base_url, f"/api/admin{path}", body, token, method)

    mains = admin("/categories", {"name": "עיקריות", "category_type": "main"})
    body = {"category_id": mains["id"], "name": "עוף בתנור", "pricing_unit": "per_tray"}
    dish = admin("/dishes", body | {"unit_price": "200.00", "servings_per_unit": "10"})
    admin(f"/dishes/{dish['id']}/dietary", {"kashrut_class": "meat"}, "PUT")
    slot = {"weekday": TUESDAY, "start_time": "09:00", "end_time": "12:00"}
    admin("/time-slots", slot | {"fulfillment_type": "pickup"})
    admin("/profile", {"contact_phone": "03-5551234"}, "PATCH")


def assert_no_axe_violations(page: Page, where: str) -> None:
    """No serious or critical WCAG A/AA violation on what is on screen now."""
    results = AXE.run(page, options={"runOnly": {"type": "tag", "values": WCAG_TAGS}})
    found = [
        f"{v['id']} ({v['impact']}): {v['help']} -> "
        + ", ".join(str(node["target"]) for node in v["nodes"][:3])
        for v in results.response["violations"]
        if v["impact"] in ("serious", "critical")
    ]
    assert not found, f"axe on {where}:\n" + "\n".join(found)


def classes(page: Page) -> str:
    return page.locator("html").get_attribute("class") or ""


def open_menu(page: Page):
    page.get_by_role("button", name="תפריט נגישות").click()
    panel = page.get_by_role("dialog", name="התאמות נגישות")
    expect(panel).to_be_visible()
    return panel


# ---------- The accessibility menu ----------


def test_menu_is_reachable_by_keyboard_right_after_the_skip_link(page: Page):
    page.goto("/")
    expect(page.locator("#main")).to_be_visible()
    page.keyboard.press("Tab")
    expect(page.get_by_role("button", name="דילוג לתוכן")).to_be_focused()
    page.keyboard.press("Tab")
    opener = page.get_by_role("button", name="תפריט נגישות")
    expect(opener).to_be_focused()
    page.keyboard.press("Enter")
    panel = page.get_by_role("dialog", name="התאמות נגישות")
    expect(panel).to_be_visible()
    page.screenshot(path=SHOTS / "a11y-menu.png")
    # Esc closes it and focus goes back to the opener.
    page.keyboard.press("Escape")
    expect(panel).to_be_hidden()
    expect(opener).to_be_focused()


def test_options_work_with_the_keyboard_alone(page: Page):
    page.keyboard.press("Enter")
    panel = page.get_by_role("dialog", name="התאמות נגישות")
    expect(panel).to_be_visible()
    contrast = panel.get_by_label("ניגודיות גבוהה")
    contrast.focus()
    page.keyboard.press("Space")
    expect(contrast).to_be_checked()
    assert "a11y-contrast" in classes(page)
    page.keyboard.press("Space")
    expect(contrast).not_to_be_checked()
    assert "a11y-contrast" not in classes(page)
    page.keyboard.press("Escape")


def test_each_option_sets_its_class(page: Page):
    panel = open_menu(page)
    for label, name in [
        ("ניגודיות גבוהה", "a11y-contrast"),
        ("הדגשת קישורים וכפתורים", "a11y-links"),
        ("גופן קריא ומרווח", "a11y-readable"),
        ("עצירת אנימציות וסרטונים", "a11y-motion"),
        ("הדגשת המיקוד במקלדת", "a11y-focus"),
    ]:
        panel.get_by_label(label).check()
        assert name in classes(page), label
    panel.get_by_label("גדול מאוד").check()
    assert "a11y-text-2" in classes(page)
    font_size = page.evaluate("getComputedStyle(document.documentElement).fontSize")
    assert font_size == "20px"


def test_choices_survive_a_reload_and_other_pages(page: Page):
    page.reload()
    expect(page.locator("#main")).to_be_visible()
    for name in ["a11y-contrast", "a11y-links", "a11y-readable", "a11y-motion", "a11y-focus"]:
        assert name in classes(page)
    assert "a11y-text-2" in classes(page)
    panel = open_menu(page)
    expect(panel.get_by_label("ניגודיות גבוהה")).to_be_checked()
    expect(panel.get_by_label("גדול מאוד")).to_be_checked()
    page.keyboard.press("Escape")
    page.screenshot(path=SHOTS / "a11y-all-options.png")
    page.goto("/admin/")
    assert "a11y-contrast" in classes(page)
    page.goto("/")
    expect(page.locator("#main")).to_be_visible()


def test_reset_clears_every_choice(page: Page):
    panel = open_menu(page)
    panel.get_by_role("button", name="איפוס ההתאמות").click()
    expect(panel.get_by_role("status")).to_have_text("ההתאמות אופסו")
    assert "a11y-" not in classes(page)
    expect(panel.get_by_label("רגיל")).to_be_checked()
    expect(panel.get_by_label("ניגודיות גבוהה")).not_to_be_checked()
    page.keyboard.press("Escape")
    page.reload()
    assert "a11y-" not in classes(page)


@pytest.mark.parametrize("step", ["home", "menu"])
def test_largest_text_never_scrolls_sideways_on_a_phone(page: Page, step: str):
    page.goto("/")
    open_menu(page).get_by_label("הכי גדול").check()
    page.keyboard.press("Escape")
    if step == "menu":
        page.get_by_role("button", name="לצפייה בתפריט").click()
        expect(page.get_by_role("heading", name="התפריט שלנו")).to_be_visible()
    else:
        # The hero grows instead of clipping: its buttons stay fully on screen.
        hero = page.locator(".hero").bounding_box()
        pause = page.locator(".hero-pause").bounding_box()
        assert pause["y"] + pause["height"] <= hero["y"] + hero["height"]
    page.screenshot(path=SHOTS / f"a11y-large-text-{step}.png", full_page=True)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    open_menu(page).get_by_role("button", name="איפוס ההתאמות").click()
    page.keyboard.press("Escape")


@pytest.mark.parametrize("step", ["home", "menu", "statement"])
def test_reflows_at_320_pixels_wide(page: Page, step: str):
    # WCAG 1.4.10: 320 CSS px is a 1280px screen at 400% zoom. Nothing scrolls sideways.
    page.set_viewport_size({"width": 320, "height": 640})
    try:
        page.goto("/accessibility/" if step == "statement" else "/")
        expect(page.locator("#main")).to_be_visible()
        if step == "menu":
            page.get_by_role("button", name="לצפייה בתפריט").click()
            expect(page.get_by_role("heading", name="התפריט שלנו")).to_be_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    finally:
        page.set_viewport_size(PHONE)


# ---------- The homepage video ----------


def test_video_has_a_pause_button(page: Page):
    page.goto("/")
    pause = page.get_by_role("button", name="עצירת הסרטון")
    expect(pause).to_be_visible()
    expect(pause).to_have_attribute("aria-pressed", "false")
    pause.click()
    play = page.get_by_role("button", name="הפעלת הסרטון")
    expect(play).to_have_attribute("aria-pressed", "true")
    expect(page.locator(".hero-media")).not_to_have_class(re.compile("is-playing"))
    expect(page.locator(".hero-poster")).to_be_visible()
    assert page.evaluate("[...document.querySelectorAll('.hero-video')].every(v => v.paused)")
    play.click()
    expect(page.get_by_role("button", name="עצירת הסרטון")).to_be_visible()


def test_stop_motion_keeps_the_still_photo_and_hides_the_button(page: Page):
    open_menu(page).get_by_label("עצירת אנימציות וסרטונים").check()
    page.keyboard.press("Escape")
    expect(page.locator(".hero-poster")).to_be_visible()
    expect(page.locator(".hero-video").first).to_be_hidden()
    expect(page.locator(".hero-pause")).to_be_hidden()
    page.reload()
    expect(page.locator(".hero-pause")).to_be_hidden()
    assert page.evaluate("[...document.querySelectorAll('.hero-video')].every(v => v.paused)")
    open_menu(page).get_by_label("עצירת אנימציות וסרטונים").uncheck()
    page.keyboard.press("Escape")
    expect(page.get_by_role("button", name="עצירת הסרטון")).to_be_visible()


# ---------- The accessibility statement ----------


def test_footer_links_to_the_statement(page: Page):
    page.locator(".site-footer").get_by_role("link", name="הצהרת נגישות").click()
    expect(page).to_have_url(re.compile(r"/accessibility/$"))
    expect(page.get_by_role("heading", level=1, name="הצהרת נגישות")).to_be_visible()


def test_statement_has_the_required_sections(page: Page):
    # What the law asks for: how the site was made accessible, how to use it,
    # what isn't accessible and the alternative, and how to contact us.
    for heading in [
        "איך הנגשנו את האתר",
        "איך משתמשים בהתאמות הנגישות",
        "מה עדיין לא נגיש",
        "פניות בנושא נגישות",
    ]:
        expect(page.get_by_role("heading", level=2, name=heading)).to_be_visible()
    expect(page.locator("main")).to_contain_text('ת"י 5568')
    expect(page.locator("main")).to_contain_text("תאריך עדכון ההצהרה")


def test_statement_shows_the_caterer_and_the_contact_placeholder(page: Page):
    expect(page).to_have_title("הצהרת נגישות | טעמים קייטרינג")
    expect(page.locator("main")).to_contain_text("אנחנו בטעמים קייטרינג")
    placeholder = page.locator('[data-placeholder="accessibility-contact"]')
    expect(placeholder).to_contain_text("יפורסמו כאן בקרוב")
    expect(placeholder.get_by_role("link", name="03-5551234")).to_have_attribute(
        "href", "tel:03-5551234"
    )
    page.screenshot(path=SHOTS / "a11y-statement.png", full_page=True)


def test_statement_page_has_the_menu_and_a_way_back(page: Page):
    open_menu(page)
    page.keyboard.press("Escape")
    page.get_by_role("link", name=re.compile("חזרה לאתר")).click()
    expect(page.locator("#main")).to_be_visible()


# ---------- The dashboard ----------


def test_dashboard_skip_link_and_menu(page: Page):
    page.goto("/admin/")
    expect(page.get_by_label("אימייל", exact=True)).to_be_focused()
    page.locator(".skip-link").focus()
    page.keyboard.press("Enter")
    expect(page.locator("main")).to_be_focused()
    expect(page.get_by_role("button", name="תפריט נגישות")).to_be_visible()


# ---------- axe-core on every page ----------


def test_axe_statement(page: Page):
    page.goto("/accessibility/")
    expect(page.locator("main")).to_contain_text("טעמים קייטרינג")
    assert_no_axe_violations(page, "the statement page")


def test_axe_dashboard_login(page: Page):
    page.goto("/admin/")
    expect(page.get_by_role("button", name="כניסה")).to_be_visible()
    assert_no_axe_violations(page, "the dashboard login")


def test_axe_dashboard_screens(page: Page):
    page.get_by_label("אימייל", exact=True).fill("owner@example.com")
    page.get_by_label("סיסמה", exact=True).fill("right")
    page.get_by_role("button", name="כניסה").click()
    expect(page.get_by_role("link", name="תפריט", exact=True)).to_be_visible()
    for key, label in [
        ("orders", "הזמנות"),
        ("menu", "תפריט"),
        ("availability", "זמינות"),
        ("delivery", "משלוחים"),
        ("quantities", "כמויות"),
        ("profile", "פרופיל העסק"),
    ]:
        page.get_by_role("link", name=label, exact=True).click()
        expect(page.locator(f"#nav-{key}")).to_have_attribute("aria-current", "page")
        page.wait_for_load_state("networkidle")
        assert_no_axe_violations(page, f"the dashboard's {label}")


def test_axe_homepage(page: Page):
    page.goto("/")
    expect(page.locator("#main")).to_be_visible()
    assert_no_axe_violations(page, "the homepage")


def test_axe_menu_panel_and_high_contrast(page: Page):
    panel = open_menu(page)
    assert_no_axe_violations(page, "the open accessibility menu")
    panel.get_by_label("ניגודיות גבוהה").check()
    page.keyboard.press("Escape")
    assert_no_axe_violations(page, "the homepage in high contrast")
    open_menu(page).get_by_role("button", name="איפוס ההתאמות").click()
    page.keyboard.press("Escape")


def test_axe_menu_before_details(page: Page):
    page.get_by_role("button", name="לצפייה בתפריט").click()
    expect(page.get_by_role("heading", name="התפריט שלנו")).to_be_visible()
    assert_no_axe_violations(page, "the menu")


def test_axe_details_form_with_errors(page: Page):
    page.get_by_role("button", name="פרטי האירוע").first.click()
    expect(page.get_by_role("heading", name="פרטי האירוע")).to_be_visible()
    assert_no_axe_violations(page, "the event details form")
    page.get_by_role("button", name="המשך לבחירת תפריט").click()
    expect(page.get_by_text("כתבו שם מלא")).to_be_visible()
    assert_no_axe_violations(page, "the event details form with errors")


def test_axe_menu_with_an_order_and_the_summary(page: Page):
    page.get_by_label("שם מלא", exact=True).fill("דנה לוי")
    page.get_by_label("טלפון ליצירת קשר", exact=True).fill("050-1234567")
    page.get_by_label("מבוגרים", exact=True).fill("10")
    page.get_by_label("תאריך האירוע", exact=True).fill(EVENT_DAY)
    page.get_by_label("שעת איסוף או הגשה", exact=True).select_option(label="09:00–12:00")
    page.get_by_role("button", name="המשך לבחירת תפריט").click()
    expect(page.get_by_role("button", name="הוספת עוף בתנור")).to_be_visible()
    page.get_by_role("button", name="הוספת עוף בתנור").click()
    expect(page.get_by_role("button", name="עוד עוף בתנור").first).to_be_visible()
    assert_no_axe_violations(page, "the menu with an order")
    page.locator(".total-bar").get_by_role("button", name="לסיכום ההזמנה").click()
    expect(page.get_by_role("button", name="שליחת בקשה להצעת מחיר")).to_be_visible()
    assert_no_axe_violations(page, "the order summary")


def test_axe_order_status(page: Page):
    page.get_by_role("button", name="שליחת בקשה להצעת מחיר").click()
    expect(page.get_by_text("ממתין לאישור הקייטרינג").first).to_be_visible()
    assert_no_axe_violations(page, "the order status")


def test_axe_on_a_computer_screen(page: Page):
    page.set_viewport_size({"width": 1366, "height": 800})
    try:
        page.goto("/")
        expect(page.locator("#main")).to_be_visible()
        assert_no_axe_violations(page, "the homepage on a computer")
        page.get_by_role("button", name="לצפייה בתפריט").click()
        expect(page.get_by_role("heading", name="התפריט שלנו")).to_be_visible()
        assert_no_axe_violations(page, "the menu on a computer")
        page.goto("/accessibility/")
        assert_no_axe_violations(page, "the statement on a computer")
    finally:
        page.set_viewport_size(PHONE)


def test_no_javascript_or_policy_errors(page: Page):
    assert page.errors == []
