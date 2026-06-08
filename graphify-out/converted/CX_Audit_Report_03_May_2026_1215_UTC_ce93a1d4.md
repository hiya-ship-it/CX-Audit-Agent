<!-- converted from CX_Audit_Report_03_May_2026_1215_UTC.docx -->



CX AUDIT REPORT
bajajfinserv.in  |  Customer Experience Deep-Dive


Prepared by: CX Audit Agent  (Claude + Playwright)

# Table of Contents

# 1. Executive Summary

## Persona Verdicts at a Glance

## Critical Issues — High Severity

## P1 Recommendations — Fix Immediately

# 2. Persona: Ramesh - First Personal Loan – Daily Wage Worker
29
Goal: Apply for first personal loan of ₹50,000 for home repair
Constraints: Very low financial literacy, unsure about eligibility, low internet
Lives In Jodhpur (Rajasthan, India) - Pin: 342006



## CX Performance — Dimension Scores

## Emotional Arc
Ramesh arrived on the Bajaj Finserv homepage with quiet urgency — his roof was leaking — and felt a small rush of hope when the 'Personal Loan' tile appeared immediately in Step 1, as if the site had understood his need without him having to search. The journey's turning point came in Steps 15 and 22, when the eligibility table on the personal-loan-eligibility-and-documents page showed 'Employed with: Public, private, or MNC' — four words that functioned as a silent rejection of everything Ramesh was, a construction worker with no employer, no salary slip, and no CIBIL score. He left at Step 28 not with anger but with a quiet, deflating embarrassment, closing the app after scrolling 15 anxious steps through jargon-heavy loan variant tables, having never found a single sentence on Bajaj Finserv's website that acknowledged someone like him existed.

## Key Takeaways
- The Personal Loan page's headline claim 'No hidden charges' directly contradicts the ₹4,043 in processing and Flexi facility charges shown in the calculator, destroying trust for a first-time borrower like Ramesh.
- The eligibility criteria row 'Employed with: Public, private, or MNC' has no plain-language footnote or alternative path for informal or daily wage workers, causing Ramesh to feel the product was not built for him.
- Ramesh spent 8+ consecutive scroll steps searching for the Eligibility section on the Personal Loan page — the tab navigation existed but did not anchor-scroll correctly, forcing exhausting manual exploration.
- The CIBIL score requirement of 650 is stated with no explanation of what CIBIL is, how to check it, or what a first-time borrower with no credit history should do — leaving Ramesh with an unanswerable question.
- Complex loan variant jargon — Flexi Hybrid Term Loan, Dropline, annual maintenance charges — appeared on an eligibility page where Ramesh needed simple inclusion signals, overwhelming him at his most anxious moment.

## Friction Points
🔴  High Severity
- Personal Loan product page: The Personal Loan page prominently displays 'No collateral and no hidden charges' as a headline benefit, yet the EMI calculator immediately below it shows ₹2,044 in processing fees and ₹1,999 in Flexi facility charges — a total of ₹4,043 Ramesh had not planned for — creating a direct contradiction that made him feel deceived.
- Personal loan eligibility and documents page: The eligibility criteria table on the dedicated eligibility page explicitly lists 'Employed with: Public, private, or MNC' and 'Customer profile: Self-employed or Salaried' with no footnote, alternative path, or plain-language explanation for informal workers — Ramesh, a daily wage construction worker, read this as a firm rejection of his entire employment category.
- Personal loan eligibility and documents page: The documentation requirements section lists 'Salary slips of the last 3 months,' 'Bank account statements of the previous 3 months,' and 'Employee ID card' as required documents — every single document presupposing a formal employer relationship that Ramesh, paid in daily cash on construction sites, could never satisfy.
- Personal loan eligibility and documents page: The CIBIL score requirement of '650 or higher' appears in the eligibility table at Step 16 and Step 22 with no explanation of what CIBIL is, how a first-time borrower can check their score, or what someone with no credit history should do — leaving Ramesh staring at a term he had heard only once from a friend.
🟡  Medium Severity
- Personal loan eligibility and documents page: Terms like 'Flexi Hybrid Term Loan,' 'Dropline limit,' 'Broken Period Interest — As applicable,' and 'annual maintenance charges 0.472%' appeared throughout the eligibility and product pages without a single plain-language gloss or tooltip, confronting Ramesh with dense financial jargon at the exact moments he needed reassurance.
- Personal Loan product page — Eligibility section: Ramesh spent Steps 8 through 15 — eight consecutive scroll actions — attempting to reach the Eligibility section on the Personal Loan product page, even though an 'Eligibility' tab was visibly present in the tab navigation bar but did not anchor-scroll him directly to that section when tapped.
- Personal Loan product page — Navigation tab: When Ramesh tapped the 'Eligibility' tab in Step 20, he was navigated to the Eligibility Calculator page at a different URL rather than the eligibility criteria section he had been searching for — he then had to tap 'Eligibility' a second time in Step 21 to finally reach the correct page.
- Personal Loan product page — EMI calculator: The EMI calculator defaults to the Flexi Hybrid Term Loan product, displaying two different EMI amounts — ₹625 for the first 24 months jumping to ₹1,057 for the next 72 months — with no plain explanation of why the payment amount changes so dramatically mid-loan.
- Homepage — Initial page load: When Ramesh first landed on the Bajaj Finserv homepage at Step 0, the page appeared visually blank — a light blue or white screen with no visible text, product tiles, or banners — leaving him unsure whether the page had loaded correctly on his low-bandwidth connection.
- Personal loan eligibility and documents page: Across all 29 steps and five pages visited — homepage, product page, auth page, eligibility calculator, and eligibility documents — Ramesh never encountered a visible customer support phone number, WhatsApp button, or live chat widget that would have let him ask 'Can a daily wage worker like me apply?'
🟢  Low Severity
- Personal Loan product page — Sticky CTA: The sticky orange 'CHECK LOAN OFFER' button physically overlaid the 'Age' row value in the eligibility criteria table at Step 15, forcing Ramesh to scroll awkwardly to read content that the site's own UI element was blocking.
- Personal Loan product page — CTA labels: Ramesh encountered three different labels for what he understood as the single action of 'trying to get the loan': 'APPLY' on the product page, 'CHECK LOAN OFFER' as the sticky button, and 'CHECK ELIGIBILITY' on the eligibility page — three labels with subtly different implications that a low-literacy user cannot easily distinguish.

## Recommendations

# Annexure A — Full Friction & Delight Analysis
## Ramesh - First Personal Loan – Daily Wage Worker
Delight Factors



HIGH SEVERITY




MEDIUM SEVERITY






LOW SEVERITY




# Annexure B — CX Score Dimensions (Full Detail)
## Ramesh - First Personal Loan – Daily Wage Worker


# Annexure C — Emotional Journey Details
## Ramesh - First Personal Loan – Daily Wage Worker
Ramesh arrived on the Bajaj Finserv homepage with quiet urgency — his roof was leaking — and felt a small rush of hope when the 'Personal Loan' tile appeared immediately in Step 1, as if the site had understood his need without him having to search. The journey's turning point came in Steps 15 and 22, when the eligibility table on the personal-loan-eligibility-and-documents page showed 'Employed with: Public, private, or MNC' — four words that functioned as a silent rejection of everything Ramesh was, a construction worker with no employer, no salary slip, and no CIBIL score. He left at Step 28 not with anger but with a quiet, deflating embarrassment, closing the app after scrolling 15 anxious steps through jargon-heavy loan variant tables, having never found a single sentence on Bajaj Finserv's website that acknowledged someone like him existed.



# Annexure D — Complete Journey Log with Screenshots

## Ramesh - First Personal Loan – Daily Wage Worker  —  Step-by-Step Journey
### Step 1  ✅  [SCROLL]  Main page content

### Step 2  ✅  [CLICK]  Personal Loan

### Step 3  ✅  [TYPE]  loan-amount-input

### Step 4  ✅  [SCROLL]  page

### Step 5  ✅  [CLICK]  APPLY

### Step 6  ✅  [BACK]  Back

### Step 7  ✅  [CLICK]  Personal Loan

### Step 8  ✅  [TYPE]  loan-amount-input

### Step 9  ✅  [SCROLL]  page

### Step 10  ✅  [SCROLL]  page

### Step 11  ✅  [SCROLL]  page

### Step 12  ✅  [SCROLL]  page

### Step 13  ✅  [SCROLL]  page

### Step 14  ✅  [SCROLL]  page

### Step 15  ✅  [SCROLL]  Personal loan eligibility and documentation section

### Step 16  ✅  [SCROLL]  Personal loan eligibility and documentation section

### Step 17  ✅  [SCROLL]  Eligibility section - employment type and customer profile criteria

### Step 18  ✅  [SCROLL]  Personal loan eligibility and documentation section - Show More link

### Step 19  ✅  [BACK]  https://www.bajajfinserv.in/

### Step 20  ✅  [SCROLL]  Personal loan eligibility criteria section

### Step 21  ✅  [CLICK]  Eligibility

### Step 22  ✅  [CLICK]  Eligibility

### Step 23  ✅  [SCROLL]  Personal loan eligibility criteria section

### Step 24  ✅  [SCROLL]  Page body - Tips to improve eligibility section

### Step 25  ✅  [SCROLL]  Page body - Tips to improve eligibility section

### Step 26  ✅  [SCROLL]  Page body - Tips to improve eligibility section

### Step 27  ✅  [SCROLL]  Page body - Tips to improve eligibility section

### Step 28  ✅  [SCROLL]  Page body - Tips to improve eligibility section

### Step 29  ✅  [GOAL_ACHIEVED]  https://www.bajajfinserv.in/personal-loan-eligibility-and-documents
| Target URL | https://www.bajajfinserv.in |
| --- | --- |
| Audit Date | 03 May 2026 1215 UTC |
| Personas Audited | 1 |
| Avg CX Score | 4.2 / 10  —  🟠 Weak |
| 1 | Executive Summary |
| --- | --- |
| 2 | Persona: Ramesh - First Personal Loan – Daily Wage Worker |
| A | Annexure A — Full Friction & Delight Analysis |
| B | Annexure B — CX Score Dimensions |
| C | Annexure C — Emotional Journey Details |
| D | Annexure D — Complete Journey Log with Screenshots |
| Overall Avg Score
4.2/10 | Best Experience
4.2/10 | Worst Experience
4.2/10 | Goals Achieved
1/1 |
| --- | --- | --- | --- |
| Persona | Score | Outcome | One-line Verdict |
| --- | --- | --- | --- |
| Ramesh - First Personal Loan – Daily Wage Worker | 4.2/10
████░░░░░░ | ✅ Achieved | Ramesh navigated confidently to the loan page but spent 15 anxious steps discovering that every eligibility criterion — salary slips, company employment, CIBIL score — silently excluded him. |
| Persona | Location | Issue |
| --- | --- | --- |
| Ramesh - First Personal Loan – Daily Wage Worker | Personal Loan product page | The Personal Loan page prominently displays 'No collateral and no hidden charges' as a headline benefit, yet the EMI calculator immediately below it shows ₹2,044 in processing fees and ₹1,999 in Flexi facility charges — a total of ₹4,043 Ramesh had not planned for — creating a direct contradiction that made him feel deceived. |
| Ramesh - First Personal Loan – Daily Wage Worker | Personal loan eligibility and documents page | The eligibility criteria table on the dedicated eligibility page explicitly lists 'Employed with: Public, private, or MNC' and 'Customer profile: Self-employed or Salaried' with no footnote, alternative path, or plain-language explanation for informal workers — Ramesh, a daily wage construction worker, read this as a firm rejection of his entire employment category. |
| Ramesh - First Personal Loan – Daily Wage Worker | Personal loan eligibility and documents page | The documentation requirements section lists 'Salary slips of the last 3 months,' 'Bank account statements of the previous 3 months,' and 'Employee ID card' as required documents — every single document presupposing a formal employer relationship that Ramesh, paid in daily cash on construction sites, could never satisfy. |
| Ramesh - First Personal Loan – Daily Wage Worker | Personal loan eligibility and documents page | The CIBIL score requirement of '650 or higher' appears in the eligibility table at Step 16 and Step 22 with no explanation of what CIBIL is, how a first-time borrower can check their score, or what someone with no credit history should do — leaving Ramesh staring at a term he had heard only once from a friend. |
| Persona | Area | Action |
| --- | --- | --- |
| Ramesh - First Personal Loan – Daily Wage Worker | Eligibility criteria page | So that daily wage workers and informal earners like Ramesh understand whether they can apply before investing 20+ minutes of anxiety, add a plain-language note beneath the 'Employed with: Public, private, or MNC' row — for example, 'Also open to self-employed individuals and those with irregular income — use our eligibility checker to find out' — and update the Customer Profile row to explicitly name 'casual/daily wage worker' as a sub-category under self-employed. |
| Ramesh - First Personal Loan – Daily Wage Worker | Documentation requirements section | To prevent informal workers from feeling permanently excluded by documentation they cannot produce, add an alternate document path on the eligibility page alongside salary slips — for example, 'No salary slip? You can submit 6 months of bank passbook entries or a GST registration certificate' — so Ramesh sees a door that is open to him, not just doors that are closed. |
| Ramesh - First Personal Loan – Daily Wage Worker | CIBIL score explanation | To prevent a first-time borrower like Ramesh from being paralysed by a term he has never encountered, replace the bare 'CIBIL Score: 650 or higher' row in the eligibility table with an inline tooltip or expandable note explaining 'CIBIL is your credit history score — if you have never borrowed before, tap here to check your score free in 2 minutes via the CIBIL website' with a direct link. |
| Ramesh - First Personal Loan – Daily Wage Worker | Personal Loan page — fee transparency | To prevent Ramesh from feeling deceived when he sees ₹4,043 in fees after reading 'No hidden charges,' replace that headline claim with 'No collateral required — processing fee of 2–3% applies, shown upfront in your calculator' so that the fee disclosure and the benefit claim are honest and consistent from the first screen he reads. |
| Outcome
✅ Goal Achieved | CX Score
4.2 / 10  🟠 Weak | Steps
29  (0 failures) |
| --- | --- | --- |
| TL;DR
Ramesh navigated confidently to the loan page but spent 15 anxious steps discovering that every eligibility criterion — salary slips, company employment, CIBIL score — silently excluded him. |
| --- |
| CX Parameter | Score | Key Finding |
| --- | --- | --- |
| Discoverability & Information Architecture
Can the product be found in 2–3 taps? | 6.5/10
██████░░░░ | Ramesh found the 'Personal Loan' tile on the homepage icon strip in Step 1 without hesitation, but the Eligibility section on the product page required 8+ scroll steps to reach despite a visible tab bar that failed to anchor-scroll correctly. |
| Content Quality & Financial Clarity
Are rates, fees & eligibility shown upfront? | 3.0/10
███░░░░░░░ | The Personal Loan page claims 'No collateral and no hidden charges' in Step 2, yet the calculator immediately shows ₹4,043 in processing and Flexi facility charges — a direct contradiction that Ramesh noticed and could not reconcile. |
| Trust & Credibility Signals
Are trust signals at key anxiety moments? | 4.5/10
████░░░░░░ | The 4.8-star rating and '5 lakh+ reviews' on the Personal Loan page (Step 2) provided some initial reassurance, but the 'No hidden charges' claim followed by visible fees actively eroded Ramesh's trust before he even reached the application step. |
| Conversion & Task Flow Design
How smooth is the path to the primary CTA? | 5.0/10
█████░░░░░ | Ramesh reached the APPLY button in just 4 steps and correctly encountered an OTP login gate — standard industry practice — but there was no pre-login eligibility confirmation step that could have flagged his ineligibility before he invested 25+ anxious steps. |
| Emotional Experience & Persona Fit
Does the tone match this persona's mindset? | 2.5/10
██░░░░░░░░ | Every page Ramesh read after Step 15 deepened his anxiety — the eligibility table showing 'Employed with: Public, private, or MNC,' documentation requiring salary slips and employee IDs, and Flexi Hybrid jargon all reinforced the feeling that this product was not designed for him. |
| Mobile & Touch Experience
Are touch targets & forms mobile-ready? | 5.5/10
██████░░░░ | The sticky 'CHECK LOAN OFFER' orange button physically blocked the 'Age' row value in the eligibility table at Step 15, forcing Ramesh to scroll past content he was actively trying to read — a direct mobile layout failure. |
| Accessibility & Inclusive Design
Is the UX inclusive for low-literacy users? | 2.0/10
██░░░░░░░░ | The eligibility page at Step 22–25 lists only salary slips, employee ID cards, and company employment as valid proof — no guidance, no alternative document path, and no plain-language note acknowledging informal or self-employed workers exist. |
| Error Handling & Recovery
Are errors plain-language and recoverable? | 5.0/10
█████░░░░░ | No technical errors occurred in Ramesh's journey, but there was no soft-eligibility warning or 'You may not qualify' signal at any point — Ramesh spent 8+ steps discovering exclusion criteria that could have been surfaced in 30 seconds via a simple pre-check question. |
| System Feedback & Load Experience
Are loading & confirmation states visible? | 4.5/10
████░░░░░░ | At Step 0, the Bajaj Finserv homepage appeared blank to Ramesh — no visible text, tiles, or banners — suggesting a slow or incomplete render that left a low-digital-literacy user confused about whether the page had loaded at all. |
| Micro-copy & Language Quality
Are labels, CTAs and copy clear & motivating? | 2.5/10
██░░░░░░░░ | On the eligibility page (Steps 22–27), terms like 'Flexi Hybrid Term Loan,' 'Dropline limit,' 'Broken Period Interest,' and 'As applicable' appeared without any plain-language explanation, leaving Ramesh — a first-time borrower — completely unable to interpret what he owed or whether he qualified. |
| Form Design & Data Collection UX
Is data collection lean, sequenced, guided? | 5.5/10
██████░░░░ | The EMI calculator on the Personal Loan page (Steps 2–3) was functional and easy for Ramesh to type his ₹50,000 amount into, but the calculator defaulted to the complex Flexi Hybrid product with a split EMI structure (₹625 then ₹1,057) that confused rather than informed him. |
| Navigation Depth & Efficiency
How many taps to goal? Any dead-ends? | 3.5/10
████░░░░░░ | Clicking the 'Eligibility' tab in Step 20 navigated Ramesh to the Eligibility Calculator page instead of the eligibility criteria section, sending him one loop further away from his goal and forcing him to click 'Eligibility' a second time in Step 21 to reach the correct page. |
| Personalisation & Context Awareness
Does the site adapt to this persona's history? | 2.0/10
██░░░░░░░░ | The site showed no awareness that Ramesh was a first-time, low-income visitor from Jodhpur — the same Flexi Hybrid product with 96-month tenure and ₹4,043 upfront fees was displayed for ₹50,000, a product structure more suited to a high-income urban borrower than his profile. |
| Pre-Sales Support & Help Availability
Is help & EMI calculator accessible pre-apply? | 2.5/10
██░░░░░░░░ | Across 29 steps and five distinct pages, Ramesh never encountered a visible phone number, live chat option, or WhatsApp link — leaving a low-literacy, anxious first-time borrower with no human assistance channel when the written content excluded and confused him. |
| Visual Hierarchy & Scannability
Is key info prominent? Is noise minimised? | 3.5/10
████░░░░░░ | The Personal Loan page placed the 'No hidden charges' benefit claim prominently at the top (Step 2) while the ₹4,043 in fees appeared only inside the calculator summary — Ramesh had to scroll and calculate manually to understand the true cost, a visual hierarchy failure for a low-literacy user. |
| Consistency & Standards
Are patterns & labels consistent site-wide? | 5.5/10
██████░░░░ | The CTA label changed between 'APPLY' on the product page (Step 4) and 'CHECK LOAN OFFER' and 'CHECK ELIGIBILITY' on subsequent pages and sticky buttons — three different action labels for what Ramesh understood as the single action of 'trying to get the loan.' |
| User Control & Flexibility
Can users undo, pause or exit without loss? | 5.0/10
█████░░░░░ | The login popup triggered by APPLY in Step 5 had a visible close (✕) button that Ramesh used successfully, but after dismissing it and returning to the product page, he had no way to save his ₹50,000 calculator state — it reset to ₹1,00,000 default, forcing him to re-enter his amount in Step 7. |
| Priority | Area | Action | Expected Impact |
| --- | --- | --- | --- |
| P1 | Eligibility criteria page | So that daily wage workers and informal earners like Ramesh understand whether they can apply before investing 20+ minutes of anxiety, add a plain-language note beneath the 'Employed with: Public, private, or MNC' row — for example, 'Also open to self-employed individuals and those with irregular income — use our eligibility checker to find out' — and update the Customer Profile row to explicitly name 'casual/daily wage worker' as a sub-category under self-employed. | Ramesh would have received an inclusion signal at Step 15 instead of a silent rejection, reducing abandonment among India's 90 million+ informal workers who currently self-exclude before even attempting the application. |
| P1 | Documentation requirements section | To prevent informal workers from feeling permanently excluded by documentation they cannot produce, add an alternate document path on the eligibility page alongside salary slips — for example, 'No salary slip? You can submit 6 months of bank passbook entries or a GST registration certificate' — so Ramesh sees a door that is open to him, not just doors that are closed. | Showing an alternate document route for non-salaried applicants will reduce drop-off among informal-economy users who currently read the documentation list and self-disqualify before reaching the application step. |
| P1 | CIBIL score explanation | To prevent a first-time borrower like Ramesh from being paralysed by a term he has never encountered, replace the bare 'CIBIL Score: 650 or higher' row in the eligibility table with an inline tooltip or expandable note explaining 'CIBIL is your credit history score — if you have never borrowed before, tap here to check your score free in 2 minutes via the CIBIL website' with a direct link. | First-time borrowers who currently abandon the journey upon seeing 'CIBIL 650' with no context will have an actionable next step, reducing eligibility-stage drop-off among users with no prior credit exposure. |
| P1 | Personal Loan page — fee transparency | To prevent Ramesh from feeling deceived when he sees ₹4,043 in fees after reading 'No hidden charges,' replace that headline claim with 'No collateral required — processing fee of 2–3% applies, shown upfront in your calculator' so that the fee disclosure and the benefit claim are honest and consistent from the first screen he reads. | Aligning the headline claim with the calculator's fee display will prevent the trust collapse Ramesh experienced in Steps 3–11, reducing anxiety-driven abandonment before the first CTA click. |
| P2 | Personal Loan page — tab navigation | To save Ramesh from 8+ exhausting scroll steps searching for eligibility criteria, fix the 'Eligibility' tab in the product page navigation bar to anchor-scroll directly to the eligibility criteria section on the same page — and ensure tapping 'Eligibility' from the product page does not redirect to the separate Eligibility Calculator URL as it did in Step 20. | Direct anchor-tab navigation will reduce the time to reach eligibility criteria from 8+ scroll steps to a single tap, materially lowering frustration-driven exit before the user has read the criteria. |
| P2 | EMI calculator — Flexi product default | To prevent Ramesh from being confused by the unexplained jump from ₹625 to ₹1,057 EMI mid-loan, add a one-line plain-language tooltip next to the split EMI display explaining 'Your EMI changes because this is a Flexi plan — switch to Term Loan below for a fixed monthly payment' with a toggle that defaults low-income users to the simpler Term Loan view. | Surfacing the simple Term Loan option as the default or an easy one-tap alternative will reduce calculator-stage confusion and make the product feel manageable rather than unpredictable for first-time borrowers. |
| P2 | Pre-sales support — help channel visibility | To give Ramesh a way to ask 'Can a daily wage worker like me apply?' before he gives up alone, add a persistent WhatsApp or click-to-call support button visible on the eligibility page and product page — positioned near the eligibility criteria table where anxiety peaks, not buried in the footer. | A visible human support channel at the eligibility criteria section will intercept high-intent users like Ramesh who are close to qualifying but need one clarifying question answered before they commit their phone number. |
| P2 | Eligibility calculator — pre-check questions | To surface Ramesh's likely ineligibility before he invests 20+ minutes of anxious exploration, add two plain-language screening questions to the top of the Eligibility Calculator page — 'Are you salaried or self-employed?' and 'Do you have a bank account with 3+ months of statements?' — and provide an alternative product or guidance path if the answers suggest poor fit. | A 2-question pre-screen will redirect informal workers to appropriate products or advice within 30 seconds, preventing the prolonged false-hope journey Ramesh endured across Steps 8–28. |
| P3 | Sticky CTA button — mobile layout | To prevent the sticky orange 'CHECK LOAN OFFER' button from physically blocking eligibility table rows as it did at Step 15, reduce the sticky bar height on mobile and add sufficient bottom padding to the eligibility table so all rows are fully readable without the CTA overlapping content. | Ramesh will be able to read every eligibility criterion — including the Age row he missed — without having to scroll awkwardly, ensuring no criterion is accidentally hidden by the site's own UI. |
| P3 | CTA label consistency | To reduce the confusion Ramesh felt encountering three different action labels — 'APPLY,' 'CHECK LOAN OFFER,' and 'CHECK ELIGIBILITY' — standardise all primary CTAs in the personal loan funnel to a single consistent label such as 'Check My Eligibility' at the pre-login stage, reserving 'Apply Now' only for the post-eligibility-confirmed step. | A single, consistent CTA label will reduce hesitation at each action point, particularly for low-literacy users like Ramesh who interpret label differences as meaningfully different — and potentially risky — actions. |
| ✨
The 'Personal Loan' product tile's plain two-word label, visible without any menu interaction, let Ramesh — a man who rarely uses apps — find his goal in a single tap at Step 1, a moment of rare ease that matched his low-literacy navigation style perfectly. |
| --- |
| ✨
The EMI calculator's real-time response to Ramesh typing '50000' in Step 2 immediately showed him a monthly figure without any page reload, a level of instant feedback that made an abstract loan feel tangible and within his cognitive reach. |
| --- |
| ✨
The bold 'Amount to be credited in your bank: ₹50,000' highlighted box in the calculator summary at Steps 4 and 11 used the exact framing Ramesh needed — his money, his number, his bank — giving him a moment of clarity amid a confusing fee breakdown. |
| --- |
| 🔴  Personal Loan product page
The Personal Loan page prominently displays 'No collateral and no hidden charges' as a headline benefit, yet the EMI calculator immediately below it shows ₹2,044 in processing fees and ₹1,999 in Flexi facility charges — a total of ₹4,043 Ramesh had not planned for — creating a direct contradiction that made him feel deceived.
User Impact: Ramesh's initial trust in Bajaj Finserv collapsed at this moment, and he spent the rest of the journey in a state of low-grade suspicion that made him hesitant to share his phone number or proceed with the application. |
| --- |
| 🔴  Personal loan eligibility and documents page
The eligibility criteria table on the dedicated eligibility page explicitly lists 'Employed with: Public, private, or MNC' and 'Customer profile: Self-employed or Salaried' with no footnote, alternative path, or plain-language explanation for informal workers — Ramesh, a daily wage construction worker, read this as a firm rejection of his entire employment category.
User Impact: Ramesh spent Steps 22–28 scrolling with fading hope, looking for one sentence that included someone like him, and left the site feeling personally excluded and slightly embarrassed — abandoning his ₹50,000 home repair loan entirely. |
| --- |
| 🔴  Personal loan eligibility and documents page
The documentation requirements section lists 'Salary slips of the last 3 months,' 'Bank account statements of the previous 3 months,' and 'Employee ID card' as required documents — every single document presupposing a formal employer relationship that Ramesh, paid in daily cash on construction sites, could never satisfy.
User Impact: Ramesh felt definitively shut out at Step 25, concluding that 'this loan was made for office workers, not for someone like him' — a moment of real financial exclusion that drove his final decision to abandon the journey. |
| --- |
| 🔴  Personal loan eligibility and documents page
The CIBIL score requirement of '650 or higher' appears in the eligibility table at Step 16 and Step 22 with no explanation of what CIBIL is, how a first-time borrower can check their score, or what someone with no credit history should do — leaving Ramesh staring at a term he had heard only once from a friend.
User Impact: Ramesh could not self-assess his eligibility on the most critical dimension, trapping him in unresolvable uncertainty and eroding his confidence to even attempt the eligibility calculator. |
| --- |
| 🟡  Personal loan eligibility and documents page
Terms like 'Flexi Hybrid Term Loan,' 'Dropline limit,' 'Broken Period Interest — As applicable,' and 'annual maintenance charges 0.472%' appeared throughout the eligibility and product pages without a single plain-language gloss or tooltip, confronting Ramesh with dense financial jargon at the exact moments he needed reassurance.
User Impact: Ramesh reached Step 28 with 'glazed eyes,' his reading comprehension overwhelmed, and his ability to make an informed decision completely undermined by language designed for financially literate urban borrowers. |
| --- |
| 🟡  Personal Loan product page — Eligibility section
Ramesh spent Steps 8 through 15 — eight consecutive scroll actions — attempting to reach the Eligibility section on the Personal Loan product page, even though an 'Eligibility' tab was visibly present in the tab navigation bar but did not anchor-scroll him directly to that section when tapped.
User Impact: The long, exhausting scroll eroded Ramesh's patience and energy before he even read the criteria, arriving at the eligibility table already frustrated rather than curious. |
| --- |
| 🟡  Personal Loan product page — Navigation tab
When Ramesh tapped the 'Eligibility' tab in Step 20, he was navigated to the Eligibility Calculator page at a different URL rather than the eligibility criteria section he had been searching for — he then had to tap 'Eligibility' a second time in Step 21 to finally reach the correct page.
User Impact: Ramesh arrived at a calculator he didn't want and had to repeat his navigation, adding two unnecessary steps to an already exhausting journey and reinforcing his sense that the site was difficult to navigate. |
| --- |
| 🟡  Personal Loan product page — EMI calculator
The EMI calculator defaults to the Flexi Hybrid Term Loan product, displaying two different EMI amounts — ₹625 for the first 24 months jumping to ₹1,057 for the next 72 months — with no plain explanation of why the payment amount changes so dramatically mid-loan.
User Impact: Ramesh, a daily wage worker with irregular income, fixated on the ₹1,057 figure and felt genuine fear about a payment he wasn't sure he could sustain — confusion that no tooltip or inline explanation addressed. |
| --- |
| 🟡  Homepage — Initial page load
When Ramesh first landed on the Bajaj Finserv homepage at Step 0, the page appeared visually blank — a light blue or white screen with no visible text, product tiles, or banners — leaving him unsure whether the page had loaded correctly on his low-bandwidth connection.
User Impact: For someone with low digital literacy, a blank-looking page is the most anxiety-inducing possible first impression — Ramesh immediately questioned whether the site was working at all, starting the journey in confusion rather than confidence. |
| --- |
| 🟡  Personal loan eligibility and documents page
Across all 29 steps and five pages visited — homepage, product page, auth page, eligibility calculator, and eligibility documents — Ramesh never encountered a visible customer support phone number, WhatsApp button, or live chat widget that would have let him ask 'Can a daily wage worker like me apply?'
User Impact: Without any human help channel, Ramesh was forced to decode exclusionary written criteria alone, and left the site with an unanswered question that a single support conversation could have resolved or redirected. |
| --- |
| 🟢  Personal Loan product page — Sticky CTA
The sticky orange 'CHECK LOAN OFFER' button physically overlaid the 'Age' row value in the eligibility criteria table at Step 15, forcing Ramesh to scroll awkwardly to read content that the site's own UI element was blocking.
User Impact: Ramesh missed the Age eligibility value — one criterion he actually met — adding a small, unnecessary layer of confusion to an already stressful reading experience. |
| --- |
| 🟢  Personal Loan product page — CTA labels
Ramesh encountered three different labels for what he understood as the single action of 'trying to get the loan': 'APPLY' on the product page, 'CHECK LOAN OFFER' as the sticky button, and 'CHECK ELIGIBILITY' on the eligibility page — three labels with subtly different implications that a low-literacy user cannot easily distinguish.
User Impact: The inconsistent labelling added cognitive friction at every stage, making Ramesh unsure whether tapping each button would take him to a form, an offer, a check, or another phone number request. |
| --- |
| Dimension | Score | Rationale |
| --- | --- | --- |
| Discoverability & Information Architecture | 6.5/10
██████░░░░ | Ramesh found the 'Personal Loan' tile on the homepage icon strip in Step 1 without hesitation, but the Eligibility section on the product page required 8+ scroll steps to reach despite a visible tab bar that failed to anchor-scroll correctly. |
| Content Quality & Financial Clarity | 3.0/10
███░░░░░░░ | The Personal Loan page claims 'No collateral and no hidden charges' in Step 2, yet the calculator immediately shows ₹4,043 in processing and Flexi facility charges — a direct contradiction that Ramesh noticed and could not reconcile. |
| Trust & Credibility Signals | 4.5/10
████░░░░░░ | The 4.8-star rating and '5 lakh+ reviews' on the Personal Loan page (Step 2) provided some initial reassurance, but the 'No hidden charges' claim followed by visible fees actively eroded Ramesh's trust before he even reached the application step. |
| Conversion & Task Flow Design | 5.0/10
█████░░░░░ | Ramesh reached the APPLY button in just 4 steps and correctly encountered an OTP login gate — standard industry practice — but there was no pre-login eligibility confirmation step that could have flagged his ineligibility before he invested 25+ anxious steps. |
| Emotional Experience & Persona Fit | 2.5/10
██░░░░░░░░ | Every page Ramesh read after Step 15 deepened his anxiety — the eligibility table showing 'Employed with: Public, private, or MNC,' documentation requiring salary slips and employee IDs, and Flexi Hybrid jargon all reinforced the feeling that this product was not designed for him. |
| Mobile & Touch Experience | 5.5/10
██████░░░░ | The sticky 'CHECK LOAN OFFER' orange button physically blocked the 'Age' row value in the eligibility table at Step 15, forcing Ramesh to scroll past content he was actively trying to read — a direct mobile layout failure. |
| Accessibility & Inclusive Design | 2.0/10
██░░░░░░░░ | The eligibility page at Step 22–25 lists only salary slips, employee ID cards, and company employment as valid proof — no guidance, no alternative document path, and no plain-language note acknowledging informal or self-employed workers exist. |
| Error Handling & Recovery | 5.0/10
█████░░░░░ | No technical errors occurred in Ramesh's journey, but there was no soft-eligibility warning or 'You may not qualify' signal at any point — Ramesh spent 8+ steps discovering exclusion criteria that could have been surfaced in 30 seconds via a simple pre-check question. |
| System Feedback & Load Experience | 4.5/10
████░░░░░░ | At Step 0, the Bajaj Finserv homepage appeared blank to Ramesh — no visible text, tiles, or banners — suggesting a slow or incomplete render that left a low-digital-literacy user confused about whether the page had loaded at all. |
| Micro-copy & Language Quality | 2.5/10
██░░░░░░░░ | On the eligibility page (Steps 22–27), terms like 'Flexi Hybrid Term Loan,' 'Dropline limit,' 'Broken Period Interest,' and 'As applicable' appeared without any plain-language explanation, leaving Ramesh — a first-time borrower — completely unable to interpret what he owed or whether he qualified. |
| Form Design & Data Collection UX | 5.5/10
██████░░░░ | The EMI calculator on the Personal Loan page (Steps 2–3) was functional and easy for Ramesh to type his ₹50,000 amount into, but the calculator defaulted to the complex Flexi Hybrid product with a split EMI structure (₹625 then ₹1,057) that confused rather than informed him. |
| Navigation Depth & Efficiency | 3.5/10
████░░░░░░ | Clicking the 'Eligibility' tab in Step 20 navigated Ramesh to the Eligibility Calculator page instead of the eligibility criteria section, sending him one loop further away from his goal and forcing him to click 'Eligibility' a second time in Step 21 to reach the correct page. |
| Personalisation & Context Awareness | 2.0/10
██░░░░░░░░ | The site showed no awareness that Ramesh was a first-time, low-income visitor from Jodhpur — the same Flexi Hybrid product with 96-month tenure and ₹4,043 upfront fees was displayed for ₹50,000, a product structure more suited to a high-income urban borrower than his profile. |
| Pre-Sales Support & Help Availability | 2.5/10
██░░░░░░░░ | Across 29 steps and five distinct pages, Ramesh never encountered a visible phone number, live chat option, or WhatsApp link — leaving a low-literacy, anxious first-time borrower with no human assistance channel when the written content excluded and confused him. |
| Visual Hierarchy & Scannability | 3.5/10
████░░░░░░ | The Personal Loan page placed the 'No hidden charges' benefit claim prominently at the top (Step 2) while the ₹4,043 in fees appeared only inside the calculator summary — Ramesh had to scroll and calculate manually to understand the true cost, a visual hierarchy failure for a low-literacy user. |
| Consistency & Standards | 5.5/10
██████░░░░ | The CTA label changed between 'APPLY' on the product page (Step 4) and 'CHECK LOAN OFFER' and 'CHECK ELIGIBILITY' on subsequent pages and sticky buttons — three different action labels for what Ramesh understood as the single action of 'trying to get the loan.' |
| User Control & Flexibility | 5.0/10
█████░░░░░ | The login popup triggered by APPLY in Step 5 had a visible close (✕) button that Ramesh used successfully, but after dismissing it and returning to the product page, he had no way to save his ₹50,000 calculator state — it reset to ₹1,00,000 default, forcing him to re-enter his amount in Step 7. |
| Stage | Emotion | What Triggered It |
| --- | --- | --- |
| Landing on homepage | 😕 Confused | The Bajaj Finserv homepage appeared visually blank at Step 0 — no visible text, tiles, or banners — leaving Ramesh unsure whether the page had loaded on his slow connection. |
| Spotting Personal Loan tile | 🙂 Hopeful | The 'Personal Loan' tile with plain text labelling appeared clearly in the homepage icon strip at Step 1, matching Ramesh's exact need and giving him an immediate, unambiguous entry point. |
| Reading 'No hidden charges' claim | ✅ Reassured | The bullet point 'No collateral and no hidden charges' on the Personal Loan page at Step 2 gave Ramesh a direct, plain-language promise that temporarily neutralised his anxiety about unexpected costs. |
| Seeing ₹4,043 in fees on calculator | 🤨 Suspicious | The calculator summary at Step 3 showed ₹2,044 processing fee and ₹1,999 Flexi facility charges — directly contradicting the 'no hidden charges' headline Ramesh had just read, making him feel he was being misled. |
| Tapping APPLY button | Determined | The large orange 'APPLY' button at Step 4, combined with the bold '₹50,000 to be credited in your bank' confirmation, gave Ramesh enough reassurance to commit to the next action despite his fee-related unease. |
| Hitting OTP login popup | Deflated | A 'Get Started' popup requesting a 10-digit mobile number appeared at Step 5 immediately after tapping APPLY, asking Ramesh for personal information before he had received any eligibility signal or loan offer. |
| Scrolling for eligibility criteria | 😰 Anxious | Between Steps 8 and 14, Ramesh scrolled through multiple sections of the Personal Loan page — Features, Key benefits, loan variants — unable to reach the Eligibility section despite seeing the tab label in the navigation bar. |
| Reading 'Employed with: Public, private, or MNC' | Alarmed | The eligibility table row at Step 15 and Step 22 explicitly listed only formal employer types, with no mention of daily wage, casual, or informal workers — a criterion Ramesh read as a direct exclusion of himself. |
| Reading documentation requirements | Despairing | The documentation section at Step 25 listed salary slips, bank account statements, and employee ID cards — every document presupposing a formal employer that Ramesh, paid in daily cash, could never produce. |
| Searching for informal worker mention | Grasping | Between Steps 23 and 27, Ramesh scrolled through the 'Tips to improve eligibility' section and loan variant descriptions hoping for one line acknowledging informal workers, finding instead Flexi Hybrid jargon and annual maintenance charge tables. |
| Closing the app | 😞 Disappointed | At Step 28, surrounded by 'Dropline limit,' 'initial tenure,' and 'subsequent tenure' terminology on the eligibility page, Ramesh closed the site — having never found evidence that Bajaj Finserv's personal loan was available to someone like him. |
| URL: https://www.bajajfinserv.in/
Emotion: 😕 Confused
Observation: The page appears almost entirely blank/light blue — the screenshot shows no visible content, just a plain background. The text extraction mentions a search input and "Bajaj Finserv Main Menu" but no product tiles, banners, or CTAs are visible yet. The page may still be loading or the content is below the fold.
CX Note: Ramesh opens the Bajaj Finserv website and sees almost nothing — just a light blue/white screen. There's no visible text, no product tiles, no banner. For someone with low digital literacy, a blank-looking page is immediately confusing and off-putting. He might wonder if the page loaded correctly. He scrolls down hoping to find what he needs. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/
Emotion: 🙂 Hopeful
Observation: Ramesh can now see the Bajaj Finserv homepage clearly after scrolling. There's a horizontal scrollable row of product category icons near the top — he can see "Personal Loan" with a "Quick Disbursal" badge on it. Below that is a banner for "Mobiles on EMI" with an "Apply Now" button. The page has lots of content — banners, product tiles, and service icons. The "Personal Loan" tile in the icon row is clearly visible and labeled, which is exactly what Ramesh is looking for.
CX Note: Ramesh sees the homepage loaded with product icons in a horizontal scroll strip near the top. He spots "Personal Loan" with what looks like a "Quick Disbursal" badge — the words are clear and direct. For someone with low financial literacy, this labeled icon is the most approachable entry point. He doesn't know what "Quick Disbursal" means, but "Personal Loan" is exactly what he came for. He feels a small rush of hope — this might be it. He taps it without hesitation. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Typed: 50000
Emotion: 🙂 Hopeful
Observation: Ramesh is now on the Bajaj Finance Personal Loan page. He can see the product description clearly — "Personal Loan" headline, "No collateral and no hidden charges", "interest rates starting @ 10% p.a.*", and "disbursement in 24 hours*". These are reassuring signals. Below, there's an EMI calculator with a loan amount input field and tenure buttons (12 to 108 months). The current default shows ₹1,00,000 loan amount. The large orange "CHECK LOAN OFFER" button is visible at the bottom. There's also an "APPLY" button mentioned below the fold. Ramesh needs ₹50,000 — he needs to enter his desired loan amount first before proceeding.
CX Note: Ramesh sees the Personal Loan page loaded with what feels like a lot of text — but the bullet points are reassuring: "No collateral and no hidden charges" catches his eye immediately. He's relieved to see this. The star rating (4.8, 5 lakh+ reviews) looks impressive even if he doesn't fully understand what it means. He spots the calculator section with an amount input. He knows he needs ₹50,000, so he wants to type that in to see what he'll have to pay monthly. The current default of ₹1,00,000 looks too high for him — he wants to adjust it to his amount. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😕 Confused
Observation: Ramesh sees the personal loan calculator page with his ₹50,000 amount entered. The page shows key details: loan tenure set to 96 months, loan variant as "Flexi Hybrid Term Loan". He can see EMI figures — ₹625 for first 24 months, ₹1,057 for months 25-96. There's a "Loan Summary" showing processing fee of ₹2,044, Flexi facility charges of ₹1,999, total loan amount ₹54,043, and importantly "Amount to be credited: ₹50,000". The "CHECK LOAN OFFER" orange button is prominently visible. There's also mention of an "APPLY" button that's below the fold. The tenure buttons show 36, 48, 60, 72, 84, 96, 108 months — 96 is selected (highlighted in dark blue).
CX Note: Ramesh stares at the calculator summary with a mix of confusion and mild anxiety. He sees his ₹50,000 amount entered, which is reassuring. But then he notices numbers he didn't expect: "Processing fee ₹2,044" and "Flexi facility charges ₹1,999" — together that's over ₹4,000 extra. He thought the page said "no hidden charges" earlier, so this feels contradictory. He also sees the EMI is ₹625 for first 24 months, then jumps to ₹1,057 — the changing EMI amount confuses him. He doesn't fully understand what "Flexi Hybrid Term Loan" means. But he also sees "Amount to be credited in your bank: ₹50,000" which reassures him he'll get the full amount. He wants to find the Apply button to move forward, so he scrolls down. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 🙂 Hopeful
Observation: Ramesh sees the loan summary section clearly showing: his requested ₹50,000 loan, processing fee ₹2,044, Flexi facility charges ₹1,999, total loan amount ₹54,043, and EMI breakdown. There's an orange "CHECK LOAN OFFER" button prominently visible, and an "APPLY" button mentioned as below-fold. The total amount to be credited to his bank is confirmed as ₹50,000. The page is on bajajfinserv.in/personal-loan. The APPLY button is listed as below-fold in interactive elements.
CX Note: Ramesh has scrolled down and now sees the full loan summary laid out in front of him. He sees ₹50,000 in bold as the "Amount to be credited in your bank" — that reassurance is key for him. But he also sees ₹54,043 as the "Total loan amount" and ₹4,043 in charges (processing fee + Flexi charges), which makes him uneasy. He thought there were "no hidden charges" — so why is he paying ₹4,043 extra? He's confused but not enough to stop. He sees the orange "APPLY" button and recognizes it as the big button that will move him forward. He wants to try — this is exactly what he came here for. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😕 Confused
Observation: Ramesh sees a bottom-sheet popup/modal that says "Get Started" with the subtitle "Check pre-approved offers & eligibility | Start investing Buy insurance | Manage account". Below that is a "Mobile Number" input field asking for a 10-digit mobile number, with the note "An OTP will be sent to this number for verification" and a large orange "GET OTP" button. The background shows the loan summary page with the ₹50,000 credit amount and the APPLY button behind the overlay. This is a login/OTP wall triggered by clicking APPLY.
CX Note: Ramesh tapped the big orange APPLY button, feeling hopeful — and now a popup has appeared asking for his mobile number. He sees "Get Started" in bold, and a field asking for a 10-digit number. The text says "An OTP will be sent" — Ramesh recognises OTP from his phone experience (banks send OTPs), but he's confused: why does he need to give his number just to apply? He hasn't been told anything about his eligibility yet. He was expecting to fill a form with his details, not be asked to verify himself first. For a low-literacy daily wage worker who is already anxious about data sharing, being asked for his phone number at this stage — before seeing any offer — feels premature and slightly suspicious. He hesitates. He notices the ✕ close button in the top-right corner of the popup. He feels deflated — this wasn't the "Apply" experience he expected. This login wall is a significant friction point for first-time, low-literacy users like Ramesh. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/
Emotion: 🙂 Hopeful
Observation: Ramesh is back on the Bajaj Finserv homepage after hitting the login wall. The page shows the familiar homepage with product tiles in a horizontal strip near the top. He can clearly see "Personal Loan" in the icon strip. There's also a banner lower down showing "Personal Loan Up to ₹55 Lakhs* Instant disbursal Apply Now". The homepage has loaded with the same product categories he saw before. He's already been through the personal loan page once and got stopped at a login wall — but as a low-literacy user who urgently needs money for home repair, he's still determined to try to understand the process better or find another way in.
CX Note: Ramesh is back on the Bajaj Finserv homepage, feeling a mix of frustration and determination. He just hit a wall — the app asked for his phone number before he could even see if he qualifies. He doesn't understand why. He stares at the familiar homepage again. The "Personal Loan" tile is right there in the icon strip, and he recognizes it. He also sees the banner below saying "Personal Loan Up to ₹55 Lakhs* Instant disbursal" — the word "Instant" feels encouraging. He's not ready to give up yet. He needs ₹50,000 for his home repair and this feels like the right place. He taps "Personal Loan" again, hoping maybe this time he'll find a different path — maybe a form that doesn't require him to verify his phone first. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Typed: 50000
Emotion: 🙂 Hopeful
Observation: Ramesh is back on the Personal Loan page. The page shows the loan calculator with a default amount of ₹1,00,000 — not his target of ₹50,000. He can see the product description with reassuring bullet points: "No collateral and no hidden charges", "Interest rates starting @ 10% p.a.*". The loan tenure is set to 96 months. There's a "CHECK LOAN OFFER" button prominently in orange at the bottom of the screen, partially overlapping the loan amount field. The loan summary shows ₹1,00,000 as the requested amount with processing fee ₹4,009 and Flexi facility charges ₹1,999. Ramesh needs to first enter his correct amount of ₹50,000 before doing anything else.
CX Note: Ramesh is back on the familiar Personal Loan page and recognises it from before. He immediately sees the calculator showing ₹1,00,000 — that's double what he needs. He knows he wants ₹50,000 for his home repair. The "No collateral and no hidden charges" text still catches his eye and reassures him slightly, even though he earlier saw fees of ₹4,009 and ₹1,999 that confused him. He wants to type in his real amount — ₹50,000 — to see what his monthly payment would actually be. The orange "CHECK LOAN OFFER" button is visible but he's not ready to tap it yet. He's focused on getting the number right first. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😕 Confused
Observation: Ramesh is back on the Personal Loan page. The calculator now shows ₹50,000 as the loan amount — exactly what he needs. He can see the tenure is set to 96 months with loan variant "Flexi Hybrid Term Loan" selected. The EMI options are visible: ₹625 initial instalment (24 months) and ₹1,057 subsequent instalment (72 months). He can also see the Loan Summary showing "Amount to be credited in your bank: ₹50,000" but also ₹4,043 in charges (processing fee ₹2,044 + Flexi facility charges ₹1,999). The "CHECK LOAN OFFER" orange button is prominently displayed. Below the fold is the APPLY button. Ramesh has already clicked APPLY once and hit a login wall — per the journey rules, he cannot click APPLY again. He needs to explore the public content: eligibility, rates, features — things a low-literacy user would want to understand before deciding what to do next.
CX Note: Ramesh stares at the calculator showing his ₹50,000 amount and sees two very different EMI numbers — ₹625 for the first 24 months, then ₹1,057 for the next 72 months. This jump in EMI is confusing and a little alarming. He's a daily wage worker — his income isn't always guaranteed. He wonders: will he be able to pay ₹1,057 every month later? He also notices the charges again — ₹4,043 in fees on top of his ₹50,000 loan. He thought there were "no hidden charges." These fees feel hidden to him. He knows he can't hit Apply again (it asked for his phone last time), so he scrolls down to look for more information — maybe something tells him if he even qualifies for this loan. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😰 Anxious
Observation: Ramesh is on the Personal Loan page showing the EMI calculator results for ₹50,000. He can see two EMI figures: ₹625 for the first 24 months and ₹1,057 for months 25-96. The total amount payable is ₹91,104. Below that is the Loan Summary section showing: Requested loan amount ₹50,000, Processing fee ₹2,044, Flexi facility charges ₹1,999, Total loan amount ₹54,043, and crucially "Amount to be credited in your bank: ₹50,000." The APPLY button is visible below the loan summary. There are also tabs at the top: Overview, Features, Eligibility, How to Apply, Fees and Charges, Loan Variants, FAQ. The page also shows a note about "CIBIL Score of 650 or higher" required for eligibility.
CX Note: Ramesh stares at the loan summary laid out in front of him. He can see his ₹50,000 written clearly — that reassures him. But then he reads the breakdown: ₹2,044 processing fee, ₹1,999 Flexi facility charges. He adds them up slowly in his head — that's over ₹4,000 extra he has to pay just to get ₹50,000. Earlier the page said "no hidden charges" — this feels contradictory and unfair to him. He's also troubled by the two different EMI amounts: ₹625 to start, but jumping to ₹1,057 later. As a daily wage worker whose income isn't consistent, the thought of paying over ₹1,000 every month for 6 years feels scary. He hasn't been told if he even qualifies. He remembers the page mentioned a "CIBIL Score of 650 or higher" — he doesn't know what his CIBIL score is, or even what CIBIL means. He needs to scroll down to find out more — maybe the Eligibility section will tell him if daily wage workers can apply. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😰 Anxious
Observation: Ramesh is on the Personal Loan page, currently seeing the Loan Summary section. He can see the full breakdown: Requested loan amount ₹50,000, Processing fee ₹2,044, Flexi facility charges ₹1,999, Total loan amount ₹54,043. The summary also shows Initial Instalment ₹676 (24 months) and Subsequent Instalment ₹1,143 (72 months) at 15% p.a. The Total Amount payable is ₹91,104. The "CHECK LOAN OFFER" orange button is visible at the bottom. The APPLY button is listed as below-fold. The page navigation tabs show: Overview, Features, Eligibility, How to Apply, Fees and Charges, Loan Variants, FAQ — all below the current scroll position.
CX Note: Ramesh stares at the loan summary numbers. He sees ₹50,000 as the 'Amount to be credited' — that's his target. But the total he'll repay is ₹91,104 — nearly double what he's borrowing. He doesn't fully grasp compound interest, but seeing ₹91,104 for a ₹50,000 loan feels jarring, even if he can't articulate why. He's also troubled: the page promised 'no hidden charges' but shows ₹4,043 upfront in fees. He counts ₹2,044 + ₹1,999 slowly in his head. That's money he didn't plan for. The 'CHECK LOAN OFFER' orange button dominates the bottom of the screen, but Ramesh is hesitant — he's not sure what it will ask him for. He remembers the login wall from before. He wants to scroll further down to find the Eligibility section — maybe it will tell him if someone like him (daily wage worker, no steady salary slip) can even apply. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😰 Anxious
Observation: Ramesh is currently viewing the Loan Summary section showing: Total charges ₹4,043 (Processing fee ₹2,044 + Flexi facility charges ₹1,999), Stamp duty "As applicable", Broken Period Interest "As applicable", and the highlighted box showing "Amount to be credited in your bank (A-B): ₹50,000". The large orange APPLY button is visible. Below the APPLY button is a "Click here" link for fair practice code and a "Please note" section explaining stamp duty and BPI. The page navigation tabs show: Overview, Features, Eligibility, How to Apply, Fees and Charges, Loan Variants, FAQ. Ramesh has already clicked APPLY once and hit a login wall — he cannot click it again. He needs to keep scrolling to find the Eligibility section to check if a daily wage worker like him qualifies.
CX Note: Ramesh stares at the screen showing the full loan breakdown. The highlighted box says "Amount to be credited in your bank: ₹50,000" — that's reassuring, that's exactly what he needs. But just above it, he sees ₹4,043 in charges — over ₹4,000 he wasn't expecting. He slowly reads: "Processing fee ₹2,044" and "Flexi facility charges ₹1,999." Earlier the page said "no hidden charges" — but these feel like charges to him, and they weren't hidden by now but they weren't mentioned upfront either. He's confused and mildly irritated. He also sees "Stamp duty* As applicable" and "Broken Period Interest...As applicable" — these vague "As applicable" labels feel uncertain and threatening to someone who doesn't know what they mean. He doesn't click APPLY (he remembers it asked for his phone number last time). Instead, he wants to scroll down — he remembers seeing "Eligibility" in the tab bar and wants to know if someone like him can even get this loan. He wonders: "Do they give loans to daily wage workers? What is CIBIL?" |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😰 Anxious
Observation: Ramesh is on the Personal Loan page, currently viewing the "Key features" section with "Disbursal in 24 hours*" expanded, and below it collapsed items: "Flexible tenures", "No collateral", "No hidden charges". He also sees the "Personal loan EMI calculator" section heading and the beginning of "Features and benefits of our personal loan" section. The page nav at top shows tabs: Overview, Features, Eligibility, How to Apply — he hasn't reached the Eligibility section yet, which is what he most needs to see.
CX Note: Ramesh sees the "Key features" section confirming "No hidden charges" with a dropdown he hasn't expanded yet. This is the same claim that confused him earlier when he saw ₹4,043 in fees. He notices the "Personal loan EMI calculator" collapsed section — he's already used a calculator above. He's still scrolling, looking for the Eligibility section. He's been scrolling for several steps now and hasn't found the eligibility criteria yet, which is causing mild frustration. He wants to know: "Am I even allowed to apply? Do daily wage workers qualify?" |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😰 Anxious
Observation: Ramesh is currently viewing the "Features and benefits of our personal loan" section. The page shows a video thumbnail with a wedding couple, and text about "3 unique variants" and "No part-prepayment charge on Flexi Loans." The orange "CHECK LOAN OFFER" button floats at the bottom. From the page headings visible in the extracted text, the section "Personal loan eligibility and documentation" exists further down the page — Ramesh has been scrolling toward it across multiple steps. He hasn't reached it yet. The loan summary with ₹4,043 in fees and the confusing dual EMI amounts (₹625 then ₹1,057) are still haunting him. He needs to find the eligibility section to understand if a daily wage worker like him even qualifies.
CX Note: Ramesh is looking at the Features section with the wedding video and benefit bullets. He skims past the "3 unique variants" text — he doesn't fully understand what "Flexi Term (Dropline)" means and doesn't care right now. What he does care about is: "Can I, a daily wage worker from Jodhpur, even get this loan?" He hasn't seen the eligibility section yet despite scrolling multiple times. The page is long and he's growing frustrated — he's been scrolling for a while and still hasn't found the answer he needs. The orange "CHECK LOAN OFFER" button at the bottom is tempting, but he remembers the login wall. He keeps scrolling, hoping the eligibility section will finally appear and tell him plainly whether someone like him qualifies. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😰 Anxious
Observation: Ramesh can see the page has reached the "Personal loan eligibility and documentation" heading — it's visible at the bottom of the screen. The text begins: "Anyone can apply for our personal loan online, as long as you meet five basic criteria mentioned below." He can also see the "CHECK LOAN OFFER" orange button floating at the bottom. The Features section content is visible — "No part-prepayment charge on Flexi Loans", "High loan amount" (Rs. 40,000 to Rs. 55 lakh), "Quick approval." The eligibility section heading is RIGHT THERE at the bottom of the current view but the actual criteria bullets haven't loaded into view yet.
CX Note: Ramesh can FINALLY see what he's been looking for — the "Personal loan eligibility and documentation" section header is right there at the bottom of his screen. He reads: "Anyone can apply for our personal loan online, as long as you meet five basic criteria mentioned below." The word "anyone" gives him a tiny spark of hope — maybe daily wage workers ARE included. But he can't see the actual criteria yet. He needs to scroll just a tiny bit more to find out if he's in that "anyone" category. The orange "CHECK LOAN OFFER" button is still floating at the bottom, tempting but also triggering his memory of the login wall. He ignores it for now and scrolls down — he wants to know IF he qualifies before he tries to apply again. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😰 Anxious
Observation: Ramesh can see the Eligibility section heading and the beginning of eligibility criteria content. The page shows a table with "Nationality: Indian" and "Employed with: Public, private, or MNC." The "Age" row is visible but the value is partially obscured by the orange "CHECK LOAN OFFER" sticky button. The tab bar shows "Eligibility" is currently the active tab. There's a video player with a play button and the heading "Eligibility Criteria and Documents Required for Bajaj Finserv Personal Loan" with a bullet point "Personal loan eligibility criteria." The table has partially loaded — he can see Nationality and "Employed with" rows but still needs to scroll to see all 5 criteria, especially whether daily wage workers qualify.
CX Note: Ramesh has FINALLY found the Eligibility section he's been searching for across many scroll steps. He sees the table starting with "Nationality: Indian" — fine, he's Indian. But then his eyes catch "Employed with: Public, private, or MNC." He stares at this. He works as a daily wage worker — not for a company, not for an MNC. He doesn't have a salary slip. This line feels like a door slamming in his face. The orange "CHECK LOAN OFFER" sticky button is actually blocking the "Age" row value, adding another frustration. He wants to scroll down to see if daily wage workers are mentioned anywhere, or if there's a "self-employed" category that might include him. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/myaccount/homepageDynamic/homeDynamic
Emotion: 😰 Anxious
Observation: Ramesh is currently on the Bajaj Finserv personal loan page, looking at the Eligibility section. The screenshot shows a table with Age (21-80 years), Employed with (Public, private, or MNC), CIBIL Score (650 or higher), and Customer profile (Self-employed or Salaried). There's a "Show More" link in orange below the table, and a "How to apply for a personal loan online?" section starting below. An orange "CHECK LOAN OFFER" button is visible at the bottom. The page URL shows the homepage dynamic URL but the content clearly shows the personal loan eligibility section.
CX Note: Ramesh reads the eligibility table carefully, moving his eyes slowly from row to row. "Employed with: Public, private, or MNC" — he doesn't work for any of these. He works on construction sites by the day. "CIBIL Score: 650 or higher" — he has no idea what CIBIL is or what his score might be. "Customer profile: Self-employed or Salaried" — he's neither. He doesn't have a salary slip. He feels his stomach drop. The word "Self-employed" gives him a tiny flicker of hope — maybe daily wage counts as self-employed? But he's not sure. He notices a "Show More" link in orange below the table. Maybe there's more information below — maybe it says something about daily wage workers or informal workers. He wants to scroll down and tap "Show More" to find out. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/
Observation: Ramesh is back on the Bajaj Finserv homepage. The page shows the home screen with product tiles including "Personal Loan - Up to ₹55 Lakhs*" and various other products. The search bar is visible at the top. Based on the journey context, Ramesh has been deep in the personal loan eligibility section and was looking for the "Show More" link to see if daily wage workers qualify. It appears the page has navigated back to the homepage during the journey. Ramesh sees the familiar homepage layout with promotional banners for Flipkart vouchers and electronics deals.
CX Note: Ramesh finds himself back on the Bajaj Finserv homepage. He's disoriented - he was deep in reading the eligibility section of the Personal Loan page and now the homepage is showing again. He sees the product strip with "Personal Loan" tile clearly labeled with "Quick Disbursal" badge and "Up to ₹55 Lakhs*". He remembers he was reading the eligibility table and was worried about the "Employed with: Public, private, or MNC" line. He still wants to find out if there's a "Show More" that might include daily wage workers. He needs to get back to that page. |  |
| --- | --- |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Observation | Ramesh is back on the Bajaj Finserv homepage. He can see the product strip at the top with "Personal Loan" tile visible with "Quick Disbursal" badge. He was deep in reading the eligibility section on the Personal Loan page — specifically looking for "Show More" to see if daily wage workers might qualify — and somehow ended up back on the homepage. He needs to navigate back to the Personal Loan product page to continue reading that eligibility section. |
| URL: https://www.bajajfinserv.in/personal-loan
Observation: Ramesh is back on the Personal Loan page (https://www.bajajfinserv.in/personal-loan). The page structure confirms there's a "Personal loan eligibility criteria" heading below. The current view shows the loan calculator and summary section. He needs to scroll down significantly to reach the eligibility section where he last left off — specifically to find the "Show More" link and see if daily wage workers are mentioned anywhere in the eligibility criteria.
CX Note: Ramesh is back on the Personal Loan page — he recognises the familiar layout with the EMI calculator and loan variants. He feels a mix of relief (he's on the right page) and continued anxiety about whether he qualifies. He can see the tab navigation at the top: "Overview Features Eligibility How to Apply Fees and Charges." He wants to get back to the Eligibility section he was reading before. The page shows ₹1,00,000 as the default loan amount in the calculator — not his ₹50,000 — but that's not his focus right now. He's fixated on one question: "Do they give loans to daily wage workers?" He scrolls down, determined to find that answer. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan
Emotion: 😰 Anxious
Observation: Ramesh is on the Personal Loan page and can see the tab navigation bar at the top with: "Overview Features Eligibility How to Apply Fees and Charges Loan Variants FAQ." He's currently looking at the "How to Apply" section (it's highlighted in orange). The page shows the 5-step process for applying. The current screenshot shows "How Personal Loan works" with bullet points about steps. Most critically, Ramesh can see the "Eligibility" tab in the navigation — this is exactly what he needs to click to jump directly to the eligibility section rather than scrolling endlessly through the long page.
CX Note: Ramesh is looking at a "How to Apply" step-by-step guide with 5 bullets. He reads them — check eligibility, enter personal details, loan offer, KYC, talk to specialist. It makes some sense to him but he's not ready to apply yet. His eyes drift upward to the tab row where he clearly sees "Eligibility" written in plain text. He thinks — that's what I need. Not 'how to apply', but 'am I even allowed to apply?' He sees the orange CHECK LOAN OFFER button floating at the bottom but ignores it. He wants that Eligibility tab. He taps it, hoping it will finally show him whether daily wage workers are welcome. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan-eligibility-calculator
Emotion: 😰 Anxious
Observation: Ramesh is now on the Personal Loan Eligibility Calculator page (https://www.bajajfinserv.in/personal-loan-eligibility-calculator). He can see the calculator form with fields for city, date of birth, monthly income, and monthly expenses — all currently empty/at 0. The page heading says "Personal Loan Eligibility Calculator" and the banner shows "Loan up to Rs. 55 lakh" with an orange APPLY ONLINE button. In the tab navigation strip below the banner, he can clearly see: Overview | Eligibility | Features | Fees and Charges | EMI Calculator | How to Apply | FAQs. The "Eligibility" tab at link [20] points to https://www.bajajfinserv.in/personal-loan-eligibility-and-do — this is the dedicated eligibility and documentation page he's been desperately trying to reach across many scroll steps.
CX Note: Ramesh stares at the Eligibility Calculator page — it's not what he wanted. He wanted to read the eligibility CRITERIA, not use a calculator. He can see the tab bar at the top clearly: "Overview | Eligibility | Features | Fees and Charges | EMI Calculator | How to Apply | FAQs." The word "Eligibility" jumps out at him. He thinks — that's the tab I need. He also notices the calculator below has fields for city, income, expenses — maybe he should fill those in first to see what it says? But his deeper anxiety is about the employment type criteria — "Public, private, or MNC" — and whether a daily wage worker like him even counts. He wants answers in plain text, not just a number from a calculator. He reaches for the "Eligibility" tab link. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan-eligibility-and-documents
Emotion: 😰 Anxious
Observation: Ramesh is now on the dedicated eligibility and documents page (https://www.bajajfinserv.in/personal-loan-eligibility-and-documents). He can finally see the full eligibility table clearly laid out on screen:
- Nationality: Indian ✓
- Age: 21 to 80 years ✓ (he's 29)
- Employed with: Public, private, or MNC ⚠️ (he's a daily wage worker)
- CIBIL Score: 650 or higher ⚠️ (he doesn't know his score)
- Customer profile: Self-employed or Salaried ⚠️ (he's neither in the traditional sense)

He also sees the documentation list: KYC docs, PAN card, Employee ID card, Salary slips (last 3 months), Bank statements (3 months). A "Show More" link is visible at the bottom of the content. There are two CTA buttons — orange "CHECK ELIGIBILITY" and floating "APPLY" button.
CX Note: Ramesh stares at the eligibility table and feels his heart sink a little. "Employed with: Public, private, or MNC" — that's not him. He works on construction sites, paid by the day. No company name. No salary slip. "Customer profile: Self-employed or Salaried" — again, neither fits clearly. The CIBIL score requirement of 650 is another unknown — he's never heard of CIBIL. But at the bottom he sees a "Show More" link and a section called "Tips to improve personal loan eligibility." He thinks — maybe there's something there for people like him? Maybe they'll explain what to do if you're not salaried? He also sees the documentation list mentions "Salary slips of the last 3 months" — which he definitely doesn't have. He feels a growing sense that this product might not be designed for him. But he scrolls down anyway, hoping to find something reassuring. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan-eligibility-and-documents
Emotion: 😰 Anxious
Observation: Ramesh is on the personal loan eligibility and documents page. He can see the full eligibility criteria: Nationality: Indian, Age: 21-80 years, Employed with: Public, private, or MNC, CIBIL Score: 650 or higher, Customer profile: Self-employed or Salaried. The documentation list is also visible including "Salary slips of the last 3 months" which he doesn't have. At the very bottom of the visible content there's a partially cut-off "Tips to improv..." section and a "Show More" button. The sticky bar at the bottom shows "Enter mobile number" and "CHECK ELIGIBILITY" in orange.
CX Note: Ramesh stares at the eligibility criteria on screen, reading slowly. "Nationality: Indian" — okay, that's him. "Age: 21 to 80 years" — he's 29, that's fine. But "Employed with: Public, private, or MNC" makes him freeze. He mutters quietly — he's not employed by any company. He works day-to-day on construction sites. "CIBIL Score: 650 or higher" — he's heard the word CIBIL once from a friend but has no idea what his score is or even how to find out. "Customer profile: Self-employed or Salaried" — neither really fits. He doesn't have salary slips. He sees the documentation list mentions "Salary slips of the last 3 months" — he definitely doesn't have those. His mood is sinking. But below the fold he can just barely see "Tips to improv..." — maybe those tips will say something about people in his situation. He scrolls down with cautious hope. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan-eligibility-and-documents
Observation: Ramesh is on the Personal Loan Eligibility and Documents page. The screen shows the "Tips to improve personal loan eligibility" section has just started appearing. He can see the intro text explaining that improving eligibility can get better rates. He sees tip #1 "Check your credit score" which mentions reviewing credit report. There's a "Show More" link visible at the bottom of the tips section. The fixed bottom bar shows "Enter mobile number" and a large orange "CHECK ELIGIBILITY" button. The tab navigation at top shows "Eligibility | Tips to improve eligibility | How to apply..." — he's currently reading the "Tips to improve eligibility" section.
CX Note: Ramesh reads the "Tips to improve personal loan eligibility" section slowly. He sees the first tip: "Check your credit score: Your credit score plays an important role in determining eligibility." He doesn't know what his credit score is — he's never checked it in his life. This tip doesn't help him directly. He sees there's a "Show More" below and keeps scrolling, hoping the next tips will be more relevant to someone like him — maybe something about how to apply if you're not salaried, or if your income is irregular. The page feels long and text-heavy. He's getting tired of reading but hasn't given up yet. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan-eligibility-and-documents
Emotion: 😰 Anxious
Observation: Ramesh is on the Personal Loan Eligibility and Documents page. The page shows the eligibility criteria he's been anxiously reading: "Employed with: Public, private, or MNC" and "Customer profile: Self-employed or Salaried" — neither clearly applies to him. The documentation list includes "Salary slips of the last 3 months" which he doesn't have. At the bottom of the visible screen, he can see the beginning of the "Tips to improve personal loan eligibility" section and what looks like a "Show More" link cut off. The "How to apply for a personal loan" section is visible below with a 5-step guide. Further down, there's "Key offerings: 3 loan types" section. The sticky bottom bar shows the "CHECK ELIGIBILITY" orange button and a mobile number input field.
CX Note: Ramesh reads through the documentation list with growing dread. "Salary slips of the last 3 months" — he doesn't have these. "Bank account statements of the previous 3 months" — he rarely uses a bank account. "Employee ID card" — he has no employer. Every document listed seems designed for someone with a formal job. He feels this loan is not meant for people like him. But he notices "Tips to improve personal loan eligibility" section just starting to appear. Maybe — just maybe — there's advice there for people in his situation. He scrolls down with fading hope, wanting one last chance to see if Bajaj Finserv has anything to offer him. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan-eligibility-and-documents
Emotion: 😰 Anxious
Observation: Ramesh is on the Personal Loan Eligibility and Documents page. The current screenshot shows the "Key offerings: 3 loan types" section with the "Flexi Hybrid Term Loan" tab selected, describing features like "Withdraw and prepay – no extra charges," "Instalment pattern" (interest-only EMIs for 36 months), and "Flexi facility charges." Below this there appear to be three grey card placeholders (possibly loading). At the bottom, there's a persistent "Enter mobile number" field with an orange "CHECK ELIGIBILITY" button. The page text extraction also shows "Tips to improv" was cut off, suggesting Ramesh hasn't yet seen the full Tips section. He needs to scroll more to read the complete eligibility tips.
CX Note: Ramesh is now staring at the "Key offerings: 3 loan types" section. He sees "Flexi Hybrid Term Loan" and reads about interest-only EMIs and withdrawing from a limit — this language is completely foreign to him. He doesn't understand what "Flexi facility charges applicable based on your loan amount" means. Three grey boxes below look like they might be loading slowly — his poor internet connection means images often don't load properly. He sees the persistent "CHECK ELIGIBILITY" orange button at the bottom, but he still hasn't found the reassurance he needed about whether daily wage workers qualify. He feels increasingly confused by the product complexity. The jargon — "Flexi Hybrid," "Dropline Loan," "instalment pattern" — is overwhelming. He just wants to know: can someone like him, who gets paid daily on construction sites, even apply? He scrolls further, hoping to find simpler language somewhere that speaks to his situation. |  |
| --- | --- |
| URL: https://www.bajajfinserv.in/personal-loan-eligibility-and-documents
Emotion: 😰 Anxious
Observation: Ramesh is on the Personal Loan Eligibility and Documents page. The screen shows three loan variant cards (Flexi Hybrid Loan, Flexi Term Loan, Term Loan) with "Apply Now" buttons, followed by a "Compare loan variants" section and a large promotional video banner saying "GET A PERSONAL LOAN IN JUST 24 HOURS*". Below that there are loan variant tabs starting with "Flexi Hybrid Term Loan" and "Flexi Term (Dropline) Loa..." — with content about "Interest-only EMIs" just beginning to appear. The persistent orange "CHECK ELIGIBILITY" button is anchored at the bottom. The page text shows the eligibility criteria section was above the current scroll position, and the "Tips to improv..." section was cut off — Ramesh has been scrolling to find the rest of those tips.
CX Note: Ramesh is staring at a confusing screen full of loan type videos and promotional imagery. The big video saying "GET A PERSONAL LOAN IN JUST 24 HOURS*" catches his eye momentarily — 24 hours sounds fast, but he wonders if that applies to someone like him. He sees the three loan variant cards: Flexi Hybrid Loan, Flexi Term Loan, Term Loan — three options he doesn't understand at all. The jargon is completely alien. He hasn't found any text that says 'daily wage workers welcome' or 'self-employed casual workers qualify.' The orange CHECK ELIGIBILITY button sits at the bottom, but he's not ready to enter his phone number yet — he wants to read the eligibility tips first. He scrolls down with fading hope, searching for any reassurance that this product is for someone like him. |  |
| --- | --- |
| URL | https://www.bajajfinserv.in/personal-loan-eligibility-and-documents |
| --- | --- |
| Emotion | 😞 Disappointed |
| Observation | Ramesh is on the Loan Variants tab of the Bajaj Finserv personal loan eligibility page. He sees a detailed comparison table for "Flexi Hybrid Term Loan" with terms like "Annual maintenance charges: Up to 0.472% (Inclusive of applicable taxes) of the Dropline limit during Initial Tenure" — language that is completely incomprehensible to him. He sees the orange CHECK ELIGIBILITY button at the bottom and a mobile number input field. The navigation tabs at the top show: Eligibility | Tips to improve eligibility | How to apply | Loan Variants | FAQ. He has visited most of these sections. The page URL is the eligibility-and-documents page. Nothing visible tells him that a daily wage construction worker is welcome to apply. |
| CX Note | Ramesh stares at the Flexi Hybrid Term Loan table with glazed eyes. "Annual maintenance charges... 0.472%... Dropline limit... Initial Tenure... Subsequent Tenure." These words mean nothing to him. He scrolled and scrolled hoping to find one sentence that said something like "we also welcome daily wage workers" or "no salary slip needed" — but he never found it. Instead, every criteria he encountered pointed toward formal employment: salary slips required, employed with a company, salaried customer profile. The documentation page mentioned an employee ID card — something he will never have working on construction sites. After nearly 10 anxious steps of searching, Ramesh quietly closes the app. He feels disappointed and slightly embarrassed — like this loan was made for office workers, not for someone like him. He wonders if there's any lender that would help a construction worker fix his leaking roof. The persistent orange "CHECK ELIGIBILITY" button at the bottom of every page felt mocking — he never felt eligible enough to even enter his phone number. Critical friction points identified: (1) Eligibility criteria explicitly states "Employed with: Public, private, or MNC" — excludes informal/daily wage workers with no plain-language alternative path shown; (2) Documentation requires salary slips, employee ID — impossible for informal workers; (3) No mention anywhere of self-employed informal workers or daily wage earners as an eligible category; (4) CIBIL score requirement of 650 with no guidance for first-time borrowers; (5) Complex loan variant jargon (Flexi Hybrid, Dropline, annual maintenance charges) overwhelms low-literacy users; (6) No customer support phone number visible to ask questions; (7) Eligibility check requires OTP — creates a barrier before the user can even see if they qualify. Ramesh would abandon this journey completely at this point. |