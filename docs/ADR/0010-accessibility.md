# ADR 0010 — Accessibility: real WCAG AA fixes, our own accessibility menu, and a statement

## Status
Accepted (2026-11-09, product owner).

## Context
Israeli law requires sites that give a public service to be accessible: the Equal Rights for Persons with Disabilities Act, Regulation 35 of the 2013 service-accessibility regulations, and Israeli Standard IS 5568 (WCAG 2.0, level AA). The site must also publish an accessibility statement covering how it was made accessible, how to use its accessibility features, what isn't accessible and the alternative, and how to report a problem (Kol Zchut, read 2026-11-09). Israeli visitors also expect an accessibility menu (תפריט נגישות). The duty falls on the caterer as the site's operator.

## Decision
- **Compliance is the site itself.** Target WCAG 2.2 AA (above the legal 2.0 AA floor). Every page and state is scanned with axe-core in the E2E tests (`e2e/test_accessibility.py`, tags wcag2a/aa, wcag21a/aa, wcag22aa); serious or critical violations fail the build. Keyboard use and reflow at 320 px are tested too.
- **Our own accessibility menu, no overlay service.** `frontend/js/a11y.js` is a plain script in `<head>` on every page, so saved choices apply before the first paint. It offers text size in 3 steps, high contrast, highlighted links and buttons, a readable font with wider spacing, stop motion, a strong focus ring, and reset. Choices are classes on `<html>` styled by `css/a11y.css`, and are kept in `localStorage` in this browser only. The panel is a modal `<dialog>` created on open and removed on close. Third-party widgets (UserWay, accessiBe and similar) are out: the security policy allows only our own scripts, pages holding an order token must load no third-party code (ADR 0006), and overlays don't make a site compliant.
- **The homepage video can be paused** (WCAG 2.2.2), and it stays still under the system "reduce motion" setting or the menu's "stop motion".
- **A statement page at `/accessibility/`**, linked from the customer footer and from the menu. It claims only what was tested. The accessibility contact is a marked placeholder until the caterer provides one (`OPEN_DECISIONS.md` #24); it shows the caterer's public phone meanwhile.
- **Test-only dependency:** `axe-playwright-python`, which bundles axe-core. It is injected by the tests and never served by the app.

## Consequences
- A review by a certified accessibility consultant (מורשה נגישות) is still recommended before the pilot; automated checks find only part of the issues.
- The statement's date must be updated whenever accessibility changes.
- New pages need the two `<head>` lines (`css/a11y.css`, `js/a11y.js`) and an axe check in `e2e/test_accessibility.py`.
- The project skill `.claude/skills/israeli-web-accessibility/` holds the legal checklist for future work.
