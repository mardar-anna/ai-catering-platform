# Reference: Israeli web accessibility

Source: Kol Zchut page read 2026-11-09 (see SKILL.md). Anything not on that page is marked (unverified).

## Exemptions (פטור)
- Heavy economic burden (נטל כלכלי כבד): not available to public authorities.
- Technological impossibility (אי התכנות טכנולוגית).
- Site with few participants (אתר עם מעט משתתפים).
- The page gives no thresholds or procedure and points to a separate guide. Do not decide on the user's behalf.
- Apps: exempt if the same service is on an accessible mobile-adapted site.

## Video, documents
- Video duty: public authority, or average turnover above 5M ILS; content prepared after 25.10.2017; captions for pre-recorded only; no audio description; lectures and discussions may offer an accessible transcript instead. How turnover is calculated is not stated.
- PDFs: accessible if created after 25.10.2017; PDF service forms and their guides always.
- Personal documents behind login (statements, reports): accessible on request (automatic until 01.01.2021).

## Penalties
- Notice, then 60 days to fix.
- Criminal: fine of about 150,000 ILS.
- Civil: compensation up to 50,000 ILS without proof of damage; class actions possible.
- Administrative: the Equal Rights Commission may issue an accessibility order (צו נגישות); violating it costs 7,500 ILS per day after the deadline, doubled for corporations.
- Who can sue: a person with a disability, the Commission, or an organization promoting disability rights.

## Hebrew statement template
Replace every `[...]`. Ask the user for real values; never invent them.

```html
<main>
  <h1>הצהרת נגישות</h1>
  <p>עודכן לאחרונה: [תאריך]</p>
  <p>אנו ב-[שם העסק] רואים חשיבות בשירות שוויוני ונגיש לכלל הלקוחות, ובהם אנשים עם מוגבלות.</p>

  <h2>איך הנגשנו את האתר</h2>
  <p>האתר הונגש בהתאם לתקן הישראלי ת"י 5568 (מבוסס WCAG, רמה AA). [פירוט: מבנה כותרות, ניווט במקלדת, ניגודיות, תוויות בטפסים, טקסט חלופי לתמונות]. הבדיקות נערכו ב-[תאריך] באמצעות [כלים וקוראי מסך].</p>

  <h2>איך משתמשים בהתאמות הנגישות</h2>
  <p>בכל עמוד יש כפתור "תפריט נגישות" [מיקום]. בתפריט אפשר [הגדלת טקסט, ניגודיות גבוהה, הדגשת קישורים, פונט קריא, עצירת אנימציות, סימון מיקוד, איפוס]. ההגדרות נשמרות בדפדפן. האתר ניתן להפעלה גם במקלדת בלבד.</p>

  <h2>מה עדיין לא נגיש</h2>
  <p>[רשימת רכיבים או תכנים שאינם נגישים], ולהם חלופה: [דרך חלופית לקבלת השירות או המידע, למשל טלפון או דוא"ל]. אם אין חלקים כאלה, ציינו זאת רק לאחר בדיקה.</p>

  <h2>פניות בנושא נגישות</h2>
  <p>נתקלתם בבעיית נגישות? פנו אל [שם רכז/ת הנגישות]: טלפון <bdi>[מספר]</bdi>, דוא"ל <bdi>[כתובת]</bdi>. נשתדל להשיב תוך [X] ימי עבודה.</p>
</main>
```
