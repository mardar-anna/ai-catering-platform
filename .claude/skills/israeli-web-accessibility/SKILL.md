---
name: israeli-web-accessibility
description: Use when building, reviewing or auditing a website or web app for Israeli users (Hebrew/RTL sites), writing a הצהרת נגישות (accessibility statement), adding an accessibility menu (תפריט נגישות), or answering questions about Israeli accessibility law (IS 5568 / ת"י 5568, Regulation 35).
---

# Israeli web accessibility

Not legal advice. Source and verification notes are at the end. Longer detail (Hebrew statement template, penalties, exemptions): [reference.md](reference.md).

## 1. Does the law apply

Check all of these (Kol Zchut, "הנגשת אתרי אינטרנט ואפליקציות"):

- The site or app gives a public service in Israel, or information about one (health, education, transport, banking, insurance, entertainment, and so on). Foreign-hosted sites that serve the Israeli public are covered. Sites serving only customers outside Israel are not.
- The operator can be a for-profit business (including a licensed dealer, עוסק מורשה), a public authority, or a non-profit (עמותה). Services to companies are covered too.
- The duty is on the operator or holder of the site (the caterer, the shop), not on the developer. Still, build it accessible by default.
- Exemptions (פטור): heavy economic burden (not for public bodies), technological impossibility, a site with few participants. The page gives no thresholds, so never assume an exemption applies. Ask the user.
- Apps: exempt only if an accessible, mobile-adapted site gives the same service (link to it from the app).
- Third-party content the operator did not create or commission (for example an embedded YouTube video) is exempt. Social media must be made accessible only as far as the platform allows.

If unsure whether the site is covered, assume it is.

## 2. The standard

- Legal floor: Israeli Standard IS 5568 (ת"י 5568) part 1, which adopts WCAG 2.0. Part 2 covers digital documents.
- Level AA comes from the regulations (Regulation 35 of the 2013 accessibility-adjustments regulations), not from the Kol Zchut page, which does not state a level. Treat AA as required.
- Target WCAG 2.2 AA. It adds focus, target size and mobile needs on top of 2.0.

## 3. Build checklist

Structure and semantics
- `<html lang="he" dir="rtl">`. Mark other-language runs with `lang="en"` etc.
- One `<h1>`, headings in order, never chosen for size. Use landmarks: `header`, `nav`, `main`, `footer`, labelled when repeated.
- First focusable element is a skip link (דלג לתוכן הראשי) to `main`. Avoid `#` links when the URL fragment is used for state.
- Unique, descriptive `<title>` per page and per route change. Links and buttons have meaningful names (no "לחץ כאן").
- Use native elements (`button`, `a`, `input`, `dialog`) before ARIA.

Keyboard
- Everything operable by keyboard, in a logical order, with no traps.
- Visible focus indicator (at least 2px, 3:1 contrast). Never `outline: none` without a replacement.
- Dialogs and menus: focus moves in, Esc closes, focus returns to the trigger, background inert.
- No single-character shortcuts without a way to turn them off.

Forms
- Every control has a visible `<label for>`. Use `autocomplete` tokens for name, phone, email, address.
- Errors: text (not color alone), linked with `aria-describedby`, `aria-invalid="true"` on the field, announced (live region or focus to an error summary). Say how to fix.
- Mark required fields in text. Do not clear user input on error.

Color and text
- Text contrast 4.5:1 (3:1 for large text and UI components/borders). Never use color alone to convey meaning (links in body text need an underline or other cue).
- Page works at 200% zoom and at 320 CSS px width with no horizontal scroll (reflow). No fixed-height text containers.
- Text spacing override (WCAG 1.4.12: line-height 1.5, paragraph spacing 2x, letter 0.12em, word 0.16em) loses no content.
- Use rem/em for text. Do not disable pinch zoom.

Media and motion
- Anything that moves, blinks or auto-updates for more than 5 seconds (carousels, background video, tickers) needs a pause/stop control (WCAG 2.2.2). Do not autoplay audio.
- Honor `prefers-reduced-motion`: no autoplay video, no parallax or large motion.
- Captions (כתוביות) for pre-recorded video are required only for public bodies and businesses with average turnover above 5M ILS, for video made after 25.10.2017. Live broadcasts do not need captions. Audio description is not required. Adding captions anyway is good practice.
- Images: meaningful `alt` in Hebrew; decorative images `alt=""` (or CSS backgrounds); icon-only buttons get an accessible name. No text baked into images.

Dynamic content
- Status messages (cart updated, saved, chat reply arrived) go in `aria-live="polite"` regions (`role="alert"` only for errors). The region exists in the DOM before it is filled.
- Loading and busy states are announced. View changes move focus or update the title.
- Chat/AI widgets: new messages announced, input labelled, usable by keyboard.

Touch targets
- Minimum 24x24 CSS px (WCAG 2.5.8), recommend 44x44. Provide a single-pointer alternative to drag gestures.

Documents
- PDFs created after 25.10.2017 must be accessible (tagged, reading order, alt text, language set, real headings and tables) per IS 5568 part 2. PDF forms and their guides must be accessible even if older. Prefer an HTML page over a PDF.
- Online forms are always in scope.

RTL specifics
- Use CSS logical properties only (`margin-inline-start`, `inset-inline-end`, `text-align: start`), never left/right.
- Wrap phone numbers, prices, emails, order numbers and Latin fragments in `<bdi>` (or `dir="ltr"` for phone/URL) so they do not reorder.
- Mirror directional icons (arrows, chevrons, back/forward, progress). Do not mirror logos, play icons, clocks or media controls.
- Check tab order matches visual right-to-left order, and that carousels and swipe directions flip.

## 4. Accessibility menu (תפריט נגישות)

Israeli users and plaintiffs expect one, though the page does not say the law requires it (unverified expectation). It never replaces real WCAG fixes.

- Build it yourself: a button in the same place on every page (early in tab order), opening a labelled dialog or panel.
- Options: text size up/down, high contrast, highlight links, readable font, stop animations, strong focus highlight, reset all, link to the accessibility statement.
- Persist choices in `localStorage` (wrapped in try/catch) and apply them before first paint to avoid a flash.
- Controls are real buttons or checkboxes with `aria-pressed`/state, keyboard operable, Esc closes, focus returns. The menu itself meets AA in every mode.
- Avoid third-party overlays and toolbar plugins: they add third-party scripts (privacy, CSP), the Kol Zchut page does not say they satisfy the duty, and compliance is judged on the site itself. Overlays do not fix missing labels, bad contrast or keyboard traps.

## 5. Accessibility statement (הצהרת נגישות)

Required content (from the page):
1. How the site was made accessible.
2. How to use the accessibility adjustments.
3. What is not accessible, and the alternative way to get that service or information.
4. How to contact the operator about accessibility problems.

Also include (common practice, not on the page; verify with a consultant): date of last update, the standard and level (IS 5568 / WCAG AA), and the accessibility coordinator's name, phone and email.

- Never invent contact details or dates. Use a clearly marked placeholder such as `[TODO: שם איש קשר לנגישות]` and ask the user for the real values.
- Link it from every page footer and from the accessibility menu. Plain HTML, itself accessible, in Hebrew.
- Only claim what was actually tested. List known gaps honestly.
- Hebrew skeleton (headings: איך הנגשנו את האתר / איך משתמשים בהתאמות הנגישות / מה עדיין לא נגיש / פניות בנושא נגישות): see [reference.md](reference.md).

## 6. Testing

Automated (every page and every state: dialogs, errors, empty and loaded lists, each menu mode):
- axe-core with tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`. Fail the build on `serious` and `critical`; review the rest. In Playwright, inject axe-core or use `@axe-core/playwright`.
- Lighthouse accessibility is a smoke check only.

Manual (automation finds only a part of the issues):
- Complete the whole user flow keyboard-only (Tab, Shift+Tab, Enter, Space, Esc, arrows).
- Screen reader spot check: NVDA on Windows, VoiceOver on iOS/macOS, with a Hebrew voice. Listen to forms, errors, dialogs and live updates.
- 200% zoom, 320px width, text-spacing override, high-contrast mode, reduced-motion on.
- Phone width with touch: target sizes and gestures.

## 7. Enforcement and honesty

- After a notice the operator has 60 days to fix. Otherwise: civil claim up to 50,000 ILS per claimant without proof of damage, class actions, a criminal fine of about 150,000 ILS, and Equal Rights Commission accessibility orders (צו נגישות) with fines of 7,500 ILS per day (double for corporations). Details: [reference.md](reference.md).
- This skill is not legal advice. Before launch, recommend review by a certified accessibility consultant (מורשה נגישות / מורשה נגישות שירות).
- Do not claim compliance in the statement, PR text or docs unless it was tested. Say "tested with X on date Y".

## 8. Source

Kol Zchut, "הנגשת אתרי אינטרנט ואפליקציות לאנשים עם מוגבלות" (page shows last update 1 November 2026), read 2026-11-09:
https://www.kolzchut.org.il/he/%D7%94%D7%A0%D7%92%D7%A9%D7%AA_%D7%90%D7%AA%D7%A8%D7%99_%D7%90%D7%99%D7%A0%D7%98%D7%A8%D7%A0%D7%98_%D7%95%D7%90%D7%A4%D7%9C%D7%99%D7%A7%D7%A6%D7%99%D7%95%D7%AA_%D7%9C%D7%90%D7%A0%D7%A9%D7%99%D7%9D_%D7%A2%D7%9D_%D7%9E%D7%95%D7%92%D7%91%D7%9C%D7%95%D7%AA

Unverified or from outside the page: level AA and Regulation 35, the extra statement fields, the accessibility-menu expectation, and all WCAG 2.2 / axe guidance.
