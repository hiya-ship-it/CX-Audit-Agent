<!-- converted from CX_Audit_Report_28_Apr_2026_0754_UTC.docx -->



CX AUDIT REPORT
Bajaj Finserv  |  Customer Experience Deep-Dive


Prepared by: CX Audit Agent  (Claude + Playwright)

# Table of Contents

(Open in Word and press Ctrl+A → F9 to populate the TOC)

# 1. Executive Summary

## Persona Verdicts at a Glance

## Critical Issues Across All Personas




## Top P1 Recommendations — Fix Immediately
No P1 recommendations.


# 2. Persona: Ramesh - First Personal Loan – Daily Wage Worker
## Persona Profile

## Journey Outcome & CX Score

## TL;DR

## Key Takeaways
- The APPLY CTA on /personal-loan routes to a 'How to Apply' guide — not a form — breaking the most basic user expectation at the most critical conversion moment.
- A 36% p.a. penal charge and dense fee table on /how-to-apply-for-personal-loan are the first financial details Ramesh sees after clicking Apply — likely alarming a daily wage worker into abandonment.
- CIBIL 650+ eligibility criterion is buried in body copy on the product page, not surfaced near the CTA — a silent eligibility blocker Ramesh never learns about before investing effort.
- The OTP gate before any eligibility result is shown is a pre-value authentication demand that offers Ramesh no reason to trust the exchange of his phone number.
- Four unexplained loan variants (Flexi Hybrid, Flexi Term, Term Loan, One IVR) with jargon labels create decision paralysis for a low-literacy user who simply wants ₹50,000 for home repair.

## Key Delight Factors





## Key Friction Points
HIGH SEVERITY



MEDIUM SEVERITY





LOW SEVERITY



## Emotional Journey
Ramesh opens Bajaj Finserv's website on his phone in Jodhpur hoping to find out if he can borrow ₹50,000 to fix his roof — a real, urgent need — but his first experience is a blank screen that tells him nothing for two full seconds, a small but telling signal that this digital world was not built with him in mind. He recovers when the homepage loads and he spots the 'Personal Loan' icon immediately, feeling a burst of hope — the site seems to know what he's looking for. On the product page, 'No collateral and no hidden charges' briefly makes him feel seen and safe, the kind of plain promise that cuts through his anxiety like a trusted neighbour's word. But when he taps APPLY, he lands on a page full of penalty charges and financial jargon — 36% penal charges, bounce fees, prepayment percentages — and the confidence drains away; he doesn't know if these are the costs he'll definitely pay or worst-case scenarios, and nobody on the page explains the difference. He finds the CHECK ELIGIBILITY widget and tries again, entering his phone number cautiously, only to be hit with an OTP demand carrying the cold header 'Verification required' and no word of why his number is needed or what will happen next — and in that moment, Ramesh closes the page, having shared his personal data, invested eight navigational steps, and learned absolutely nothing about whether he can get the ₹50,000 his home needs.


## CX Score Dashboard — All Dimensions

## Recommendations

## Complete User Journey — Step by Step
### Step 1  ✅  [WAIT]  Page load wait
What persona saw: The screen shows a plain light blue-grey blank page with no content, no navigation, no buttons, no text — just a solid background color. This is consistent with a page that is still loading. The extracted text only shows "Bajaj Finserv" as a heading with 0 interactive elements visible, confirming the page hasn't fully rendered yet.

📸  Step 1  —  ramesh-first-personal-loan-daily-wage-worker_step00_wait.png


### Step 2  ✅  [CLICK]  Personal Loan
What persona saw: The Bajaj Finserv homepage has fully loaded. I can see a horizontal icon strip with product categories including "Personal Loan" with a clear label beneath an icon. There's also a hero carousel showing "Personal Loan Up to ₹55 Lakhs* Instant disbursal Apply Now" card visible in the bottom section. The page has a prominent red banner for Mobiles on EMI and a "Summer Deals EMIs from ₹888" strip. As Ramesh, the "Personal Loan" icon in the quick-access strip is the most obvious path — it's labeled clearly, visible without scrolling, and directly matches my goal of getting a personal loan for home repair.

📸  Step 2  —  ramesh-first-personal-loan-daily-wage-worker_step01_click.png


### Step 3  ✅  [CLICK]  APPLY
What persona saw: Ramesh lands on the Personal Loan product page. He sees a bold hero image promising "Loan of up to ₹55 lakh*" with a smiling young man — this feels relatable and reassuring. Key highlights visible: "No collateral and no hidden charges", "Online application and disbursement in 24 hours*", "Attractive interest rates starting @ 10% p.a.*", "Quick approval." The loan range (₹40,000–₹55 lakh) and CIBIL requirement (650+) are mentioned in the body text. There's a clear "APPLY" button in the interactive elements — it's the most prominent action available. Rating of 4.8 and "Trusted by 3 lakh+ customers" add trust signals. Ramesh's ₹50,000 requirement fits well within the advertised range (₹40,000–₹55 lakh), giving him confidence.

📸  Step 3  —  ramesh-first-personal-loan-daily-wage-worker_step02_click.png


### Step 4  ✅  [SCROLL]  Page body — scroll down to reveal more content and find Apply CTA
What persona saw: Ramesh is on the "How to apply for a personal loan" page (https://www.bajajfinserv.in/how-to-apply-for-personal-loan). He can see: loan type icons at top, a loan range of ₹40,000–₹50 Lakh, "Calculate your EMIs" link, "Check now" CTA, several "Show More" collapsed sections, "Key offerings: 3 loan types" section showing Flexi Hybrid Term Loan, Flexi Term (Dropline) Loan, and Term Loan tabs, and a detailed fee/charges table. There's no prominent APPLY button visible in the current viewport. The page seems to be a "how to apply" informational page rather than the application form itself. Ramesh would be confused — he clicked APPLY but landed on a how-to guide, not a form. He'd scroll down looking for the actual Apply button or next step.

📸  Step 4  —  ramesh-first-personal-loan-daily-wage-worker_step03_scroll.png


### Step 5  ✅  [TYPE]  Enter mobile number
What persona saw: Ramesh is on the 'how to apply' page and can see a sticky/floating "Check Eligibility" widget at the bottom right of the screen with a mobile number input field and an orange "CHECK ELIGIBILITY" button. He also sees video thumbnails for Flexi Hybrid Loan, Flexi Term Loan, Term Loan, and One IVR for PL — each with "Apply Now" buttons. The "Enter mobile number" input field in the bottom-right widget is clearly visible and labeled simply. There's also an EMI calculator visible below fold. As a low-literacy user, Ramesh would be drawn to the "CHECK ELIGIBILITY" widget — it's prominently placed, uses simple language, and directly addresses his anxiety about whether he qualifies for the loan.

📸  Step 5  —  ramesh-first-personal-loan-daily-wage-worker_step04_type.png


### Step 6  ✅  [CLICK]  CHECK ELIGIBILITY
What persona saw: Ramesh can see the current page with the sticky "CHECK ELIGIBILITY" widget at the bottom right. His mobile number 8826100789 has already been typed into the input field (visible in the extracted elements: [02] INPUT showing "8826100789"). The orange "CHECK ELIGIBILITY" button is right next to the input. He also sees video cards for Flexi Hybrid Loan, Flexi Term Loan, Term Loan, and One IVR for PL — each with "Apply Now" buttons. The page is an informational guide but the eligibility widget is the most actionable, low-friction entry point visible to him. The EMI calculator is visible below-fold but that's secondary — checking eligibility is the priority step he's already started.

📸  Step 6  —  ramesh-first-personal-loan-daily-wage-worker_step05_click.png


### Step 7  ✅  [SCROLL]  Page body — scroll down to EMI calculator section
What persona saw: Ramesh is on the 'How to Apply for Personal Loan' page. He can see the video cards for Flexi Hybrid Loan, Flexi Term Loan, Term Loan, and One IVR for PL — each with "Apply Now" buttons. Below the fold, there is an EMI calculator with a loan amount input field and tenure buttons (12, 24, 36... months). The CHECK ELIGIBILITY widget at the bottom still shows his mobile number. The page has useful content about loan types and the calculator output is partially visible in the extracted text — it shows EMI calculations and a loan summary. Ramesh would be curious about what happens if he scrolls down to see the calculator and understand how much he'd pay for ₹50,000.

📸  Step 7  —  ramesh-first-personal-loan-daily-wage-worker_step06_scroll.png


### Step 8  ✅  [BACK]  https://www.bajajfinserv.in/how-to-apply-for-personal-loan
What persona saw: Ramesh sees a modal popup titled "Verification required" overlaying the EMI calculator page. The popup states "A one-time password has been sent to your mobile number +91 xxxxxxxx89 Change" with 6 OTP input boxes (showing "5" and "0" partially filled) and a bright orange "Submit" button. Behind the popup, the loan summary is visible showing ₹1,00,000 loan with processing fee ₹4,009, Flexi facility charges ₹1,999, and Rate of Interest 15% p.a. The bottom bar shows "8826100789" with a "CHECK ELIGIBILITY" button. The OTP popup completely blocks the application journey — Ramesh cannot proceed without entering the OTP sent to his real phone.

📸  Step 8  —  ramesh-first-personal-loan-daily-wage-worker_step07_back.png


| Target URL | https://www.bajajfinserv.in |
| --- | --- |
| Audit Date | 28 Apr 2026 0754 UTC |
| Personas Audited | 1 |
| Avg CX Score | 4.8 / 10  —  🟠 Weak |
| Overall Avg Score
4.8/10 | Best Experience
4.8/10 | Worst Experience
4.8/10 | Goals Achieved
0/1 |
| --- | --- | --- | --- |
| Persona | Score | Outcome | One-line Verdict |
| --- | --- | --- | --- |
| Ramesh - First Personal Loan – Daily Wage Worker | 4.8/10
██████░░░░░░ | 🚫 Loop Detected | Bajaj Finserv's APPLY button sends Ramesh to a fee-jargon page, then an unexplained OTP wall — a first-time borrower from Jodhpur never sees his ₹50,000 eligibility. |
| 🔴  [Ramesh - First Personal Loan – Daily Wage Worker]  /personal-loan — APPLY button (Step 2–3)
Clicking the primary APPLY CTA on the Personal Loan product page routes Ramesh to /how-to-apply-for-personal-loan — an informational guide — instead of an application form or eligibility checker. The CTA label 'APPLY' creates a direct expectation of a form to fill; landing on a guide page breaks that expectation completely.
Impact: Ramesh's forward momentum is halted. He arrived confident and ready to apply; he is now confused, reading a fee table he didn't ask for, with no obvious next step. A low-literacy first-time borrower in this state is very likely to abandon. This is the journey's single most damaging conversion failure. |
| --- |
| 🔴  [Ramesh - First Personal Loan – Daily Wage Worker]  /how-to-apply-for-personal-loan — Fee table (Step 3)
The first substantive financial information Ramesh encounters after clicking APPLY is a fee table listing penal charges up to 36% p.a., bounce charges ₹700–₹1,200, and prepayment charges up to 4.72% — all in dense lending jargon with no plain-language explanation of what these mean for a borrower who repays on time.
Impact: A daily wage worker seeing '36% penal charge' without context will interpret this as the loan's interest rate or a guaranteed cost — triggering alarm and loss of trust. This fee-first content sequence emotionally primes Ramesh to feel punished before he has even applied, creating a strong psychological barrier to conversion. |
| --- |
| 🔴  [Ramesh - First Personal Loan – Daily Wage Worker]  /how-to-apply-for-personal-loan — OTP popup (Step 7)
The CHECK ELIGIBILITY flow triggers an OTP popup with the header 'Verification required' before delivering any eligibility result. No explanation of why OTP is needed, no privacy assurance, and no alternative path (e.g., browse without OTP) is offered. Ramesh entered his mobile number expecting to see eligibility; he received a data collection gate instead.
Impact: The OTP demand arrives before any value is delivered — Ramesh has shared his phone number and received nothing in return. For a daily wage worker wary of digital data sharing, this pre-value authentication creates a high abandonment and distrust moment. The journey terminates here as a loop, with Ramesh no closer to knowing his ₹50,000 eligibility than when he started. |
| --- |
| Age
29 | Gender
— | Occupation
— | Location
— |
| --- | --- | --- | --- |
| Device
— | Financial Literacy
— | Constraints
Very low financial literacy, unsure about eligibility, accesses site on mobile w | Intent
Apply for first personal loan of ₹50,000 for home repair |
| Outcome
🚫 Loop Detected | CX Score
4.8 / 10  🟠 Weak | Steps Taken
8 / 40  (0 failures) |
| --- | --- | --- |
| Bajaj Finserv's APPLY button sends Ramesh to a fee-jargon page, then an unexplained OTP wall — a first-time borrower from Jodhpur never sees his ₹50,000 eligibility. |
| --- |
| ✨
The /personal-loan page headline copy — 'No collateral and no hidden charges' (Step 2) — directly addresses the two fears most likely to be in the mind of a first-time borrower from Jodhpur who has never taken a formal loan. Seeing this claim above the fold, before any fee information, would have created a genuine moment of reassurance and relief for Ramesh. |
| --- |
| ✨
The '4.8 star rating' and 'Trusted by 3 lakh+ customers' social proof on the /personal-loan page (Step 2) provides herd-based reassurance that is particularly powerful for a low-literacy user who doesn't know how to evaluate a lender independently — the crowd wisdom shortcut works perfectly here. |
| --- |
| ✨
The loan range '₹40,000–₹55 lakh' mentioned on the product page (Step 2) — even if not visually prominent — confirms that Ramesh's ₹50,000 need falls within the product's scope, which is a quiet but important eligibility confirmation for someone who wasn't sure whether his small amount would even be considered. |
| --- |
| ✨
The single-field CHECK ELIGIBILITY widget (Step 4) — just a mobile number input and an orange CTA — is a genuinely well-designed low-friction entry point that breaks the intimidating 'Apply for a loan' action into the smallest possible first step, making the journey feel accessible rather than bureaucratic for a first-time borrower. |
| --- |
| 🔴  /personal-loan — APPLY button (Step 2–3)
Clicking the primary APPLY CTA on the Personal Loan product page routes Ramesh to /how-to-apply-for-personal-loan — an informational guide — instead of an application form or eligibility checker. The CTA label 'APPLY' creates a direct expectation of a form to fill; landing on a guide page breaks that expectation completely.
User Impact: Ramesh's forward momentum is halted. He arrived confident and ready to apply; he is now confused, reading a fee table he didn't ask for, with no obvious next step. A low-literacy first-time borrower in this state is very likely to abandon. This is the journey's single most damaging conversion failure. |
| --- |
| 🔴  /how-to-apply-for-personal-loan — Fee table (Step 3)
The first substantive financial information Ramesh encounters after clicking APPLY is a fee table listing penal charges up to 36% p.a., bounce charges ₹700–₹1,200, and prepayment charges up to 4.72% — all in dense lending jargon with no plain-language explanation of what these mean for a borrower who repays on time.
User Impact: A daily wage worker seeing '36% penal charge' without context will interpret this as the loan's interest rate or a guaranteed cost — triggering alarm and loss of trust. This fee-first content sequence emotionally primes Ramesh to feel punished before he has even applied, creating a strong psychological barrier to conversion. |
| --- |
| 🔴  /how-to-apply-for-personal-loan — OTP popup (Step 7)
The CHECK ELIGIBILITY flow triggers an OTP popup with the header 'Verification required' before delivering any eligibility result. No explanation of why OTP is needed, no privacy assurance, and no alternative path (e.g., browse without OTP) is offered. Ramesh entered his mobile number expecting to see eligibility; he received a data collection gate instead.
User Impact: The OTP demand arrives before any value is delivered — Ramesh has shared his phone number and received nothing in return. For a daily wage worker wary of digital data sharing, this pre-value authentication creates a high abandonment and distrust moment. The journey terminates here as a loop, with Ramesh no closer to knowing his ₹50,000 eligibility than when he started. |
| --- |
| 🟡  https://www.bajajfinserv.in/ — Homepage (Step 0)
The homepage renders a completely blank light blue-grey screen with no loading indicator, skeleton UI, spinner, or partial content for the full 2-second wait period on slow mobile internet.
User Impact: For Ramesh on slow mobile data in Jodhpur, a blank first render is indistinguishable from a broken site. A user without prior experience of Bajaj Finserv's website will not know whether to wait, refresh, or leave. This is a measurable early-funnel abandonment trigger. |
| --- |
| 🟡  https://www.bajajfinserv.in/ — Homepage (Step 1)
The homepage simultaneously presents Apply Now buttons for 4+ different products, a Summer Deals banner, a Mobiles on EMI hero carousel, and 6+ product cards above the fold — all competing for attention with equal visual weight.
User Impact: Ramesh, a low-literacy first-time borrower, faces an overwhelming visual field the moment the page loads. While he successfully finds the Personal Loan icon, the clutter increases cognitive load and creates momentary confusion that could cause less determined users to disengage before finding their product. |
| --- |
| 🟡  /personal-loan — CIBIL score requirement (Step 2)
The CIBIL 650+ eligibility requirement is buried in the body paragraph text of the product page, not surfaced as a prominent eligibility callout near the APPLY button or in the key features list.
User Impact: Ramesh may not know his CIBIL score and may not even know what CIBIL is. Discovering this requirement after investing effort in navigating and entering his phone number would be a late-stage shock. Surfacing it prominently near the CTA — with a 'Check your CIBIL score free' link — would let Ramesh self-qualify before committing effort. |
| --- |
| 🟡  /how-to-apply-for-personal-loan — Loan type video cards (Step 6)
Four Apply Now buttons appear for Flexi Hybrid, Flexi Term, Term Loan, and One IVR loan variants, all with equal visual weight and no plain-language description of what differentiates them or which is appropriate for a first-time borrower needing ₹50,000.
User Impact: Ramesh faces four ambiguous choices with jargon labels ('Dropline', 'Instalment pattern', 'Flexi Hybrid') that are meaningless to him. He cannot make an informed selection and risks clicking the wrong product type — or being paralysed into inaction. Decision paralysis at a multi-CTA moment is a known conversion killer for low-literacy users. |
| --- |
| 🟡  /how-to-apply-for-personal-loan — CHECK ELIGIBILITY widget (Step 5)
The CHECK ELIGIBILITY widget collects Ramesh's mobile number with zero disclosure about what happens next — no 'We'll send you an OTP', no 'No impact on your credit score', no privacy statement visible at the point of data entry.
User Impact: Ramesh submits his phone number without informed consent about the OTP that follows. When the OTP popup appears at Step 7, it feels like an unexpected demand rather than a disclosed next step — eroding trust in a moment that should be building it. |
| --- |
| 🟢  /how-to-apply-for-personal-loan — OTP popup loan default (Step 7)
The loan summary visible behind the OTP popup shows ₹1,00,000 as the default loan amount — not Ramesh's target of ₹50,000.
User Impact: Even if Ramesh had completed OTP verification, the first personalised screen would show an amount double his need, requiring him to manually adjust. This disconnect between what he needs and what the system assumes reduces confidence that the product is right for him. |
| --- |
| 🟢  /how-to-apply-for-personal-loan — EMI calculator (Step 6)
The EMI calculator is positioned below the fold on the how-to-apply page with no anchor link, teaser stat, or above-fold prompt directing users to it.
User Impact: Ramesh scrolls down to discover the calculator (Step 6), but most users in his position — confused after the APPLY misdirection, overwhelmed by the fee table and four loan variants — would not scroll this far. The calculator's existence as a pre-sales decision-support tool is largely hidden from the users who need it most. |
| --- |
| Dimension | Score | Rationale |
| --- | --- | --- |
| Discoverability & Information Architecture | 6.5/10
████████░░░░ | The homepage quick-access icon strip at Step 1 surfaces 'Personal Loan' clearly above the fold with a recognisable icon — Ramesh found it in one tap without needing search or a hamburger menu. This is a genuine IA win for a low-literacy user. However, the architecture breaks down one level deeper: clicking APPLY on /personal-loan (Step 2–3) routes to /how-to-apply-for-personal-loan, a guide page with no Apply form, creating a navigational dead end. The product page and the how-to-apply page are structurally conflated, confusing a first-time visitor who has no mental model of the distinction. The EMI calculator is buried below the fold on the how-to-apply page with no anchor link from above the fold (Step 6). Personal Loan is reachable in 2 clicks from the homepage, which is positive, but the IA fails at depth. |
| Content Quality & Financial Clarity | 4.0/10
█████░░░░░░░ | The /personal-loan page (Step 2) shows strong trust copy — 'No collateral and no hidden charges', disbursement in 24 hours, ₹40,000–₹55 lakh range — all relevant to Ramesh's ₹50,000 need. However, the CIBIL 650+ requirement is buried in body paragraph text, not called out as a key eligibility criterion near the CTA — a critical gap for a first-time borrower who likely doesn't know his score. On /how-to-apply-for-personal-loan (Step 3), the first financial content Ramesh sees after clicking APPLY is a fee table listing bounce charges (₹700–₹1,200), prepayment charges (up to 4.72%), and penal charges (up to 36% p.a.) — all in dense financial jargon without plain-language explanation. There is no EMI breakdown for ₹50,000 visible above the fold. The default loan amount in the OTP screen behind the popup (Step 7) shows ₹1,00,000, not ₹50,000, further disconnecting the content from Ramesh's actual need. |
| Trust & Credibility Signals | 5.5/10
███████░░░░░ | The /personal-loan page (Step 2) deploys credible social proof — '3 lakh+ customers trusted', 4.8 star rating, 'No hidden charges' — that would meaningfully reassure a first-time borrower. These are well-placed above the fold. However, trust breaks down sharply at Step 7: the OTP popup after entering a mobile number carries the header 'Verification required' with zero explanation of why Ramesh's phone number is being collected, no privacy assurance, and no indication the data won't be shared. For a daily wage worker from Jodhpur who has never applied for a loan online, an unexplained OTP demand on a page he reached by clicking 'Check Eligibility' — not 'Apply' — feels coercive. RBI/NBFC registration markers and data security badges (SSL indicators, data protection statements) are not visible during the OTP interaction. The 'Change' link next to the mobile number in the OTP popup is a minor positive — it lets Ramesh correct his number — but does not compensate for the absent trust scaffolding. |
| Conversion & Task Flow Design | 3.5/10
████░░░░░░░░ | The fundamental conversion flow is broken at Step 3: the primary APPLY CTA on the product page does not lead to an application form — it leads to an informational guide. This is a flow design failure that would cause most low-literacy users to abandon. Ramesh recovers only because the sticky CHECK ELIGIBILITY widget (Step 4) provides an alternative micro-conversion entry. However, this path also ends in friction — the OTP gate at Step 7 arrives before any eligibility value is delivered, meaning Ramesh has invested effort (navigating, reading, entering phone number) for zero return. The four loan variant Apply Now buttons on video cards (Step 6) — Flexi Hybrid, Flexi Term, Term Loan, One IVR — add parallel CTA paths with no guidance on which to choose, fragmenting the funnel. Per logged-out journey rules, the OTP/login gate at application initiation is expected and is not scored negatively here; the negative score reflects the broken APPLY routing and the pre-value OTP demand on the eligibility checker path. |
| Emotional Experience & Persona Fit | 3.5/10
████░░░░░░░░ | Ramesh begins hopeful (Step 1) — the homepage icon strip is welcoming and the product page trust signals (Step 2) briefly reinforce confidence. But the tone pivots sharply at Step 3: landing on a fee table with penal charges of 36% p.a. immediately after clicking APPLY is emotionally jarring for a daily wage worker. The four unexplained loan variants (Step 6) — 'Flexi Hybrid', 'Dropline', 'Instalment pattern' — use language that is entirely alien to someone earning daily wages in Jodhpur, creating a feeling of being unqualified or out of place. The OTP popup at Step 7 with its cold 'Verification required' header, no warm explanation, and no privacy assurance delivers the journey's lowest emotional point — Ramesh ends the session anxious and no better informed about whether he can get ₹50,000. The site's tone is calibrated for financially literate urban users, not a first-time borrower in Tier-2 Rajasthan. |
| Mobile & Device Experience | 5.0/10
██████░░░░░░ | Step 0 reveals a completely blank screen with no loading indicator, skeleton UI, or spinner — on slow mobile internet (Ramesh's context), this is an immediate abandonment risk. No skeleton screens or progressive loading patterns are in evidence. The homepage icon strip (Step 1) works well on mobile — icons with text labels are touch-friendly. The sticky CHECK ELIGIBILITY widget (Step 4–5) is mobile-appropriate in concept, though its orange button is small relative to the competing Apply Now buttons on the video cards. The OTP popup (Step 7) is not assessed for mobile rendering but OTP flows on mobile are generally familiar. The overall page weight — Summer Deals banner, Mobiles on EMI hero carousel, multiple video cards, EMI calculator — is heavy for a user on slow mobile data, and no evidence of lazy loading or data-lite rendering is observed. |
| Accessibility & Inclusive Design | 3.0/10
████░░░░░░░░ | The homepage icon strip uses icons with text labels — a basic accessibility win. However, the four loan variants on the how-to-apply page (Step 6) — Flexi Hybrid, Flexi Term, Term Loan, One IVR — have no explanatory tooltips, no plain-language descriptions, and no recommendation logic for a first-time borrower. The fee table on /how-to-apply-for-personal-loan (Step 3) uses terms like 'penal charge', 'bounce charges', 'prepayment charges', and percentage ranges without any glossary, tooltip, or plain-language translation. The CIBIL score criterion (Step 2) is mentioned in body copy without explaining what CIBIL is or how to check it — a critical gap for someone who has never borrowed before. There is no Hindi language option observed despite Ramesh being from Jodhpur, Rajasthan, where Hindi is the primary language and English literacy may be limited. No help text or guided assistance is visible for complex financial fields. |
| Error Handling & Recovery Design | 5.0/10
██████░░░░░░ | No explicit form errors were triggered in this journey (Ramesh entered a valid mobile number). The 'Change' link in the OTP popup (Step 7) is a thoughtful recovery mechanism — allowing the user to correct their phone number without losing context. However, there is no graceful handling of the navigational error at Step 3: when Ramesh lands on the wrong page (how-to-apply guide instead of application form), there is no contextual message such as 'Looking to apply? Start here →' to redirect him. The OTP popup offers no fallback path ('Continue browsing without OTP' or 'Use email instead'). Error handling is adequate for explicit input errors but absent for flow-level misdirections, which is where Ramesh actually got lost. |
| Page Performance & Load Experience | 3.5/10
████░░░░░░░░ | Step 0 is the most damning evidence: the Bajaj Finserv homepage renders a completely blank light blue-grey screen with no content, no navigation, no skeleton UI, and no loading indicator for the full 2-second wait. For Ramesh on slow mobile internet in Jodhpur, this is the first impression of the brand — and it communicates nothing. In a country where 4G speeds in Tier-2 cities average 10–15 Mbps with frequent throttling, a blank first render with no progressive loading is a measurable abandonment driver. The homepage carries substantial media weight (hero carousel for Mobiles on EMI, Summer Deals banner, multiple product carousels, video cards) with no evidence of lazy loading. The 2-second explicit wait at Step 0 suggests the page is not optimised for low-bandwidth conditions. |
| Micro-copy & Language Quality | 4.0/10
█████░░░░░░░ | The /personal-loan product page (Step 2) has some excellent micro-copy for low-literacy users: 'No collateral and no hidden charges', 'disbursement in 24 hours*' — plain, direct, and addressing core anxieties. However, several micro-copy failures undermine the journey: (1) The APPLY button on /personal-loan routes to a guide — the CTA label creates a false promise. (2) The fee table on /how-to-apply-for-personal-loan uses 'penal charge up to 36% p.a.' with no plain-language translation of what this means for a first-time borrower. (3) The OTP popup header 'Verification required' is cold and bureaucratic — no warmth, no explanation, no reassurance. (4) There is no copy under the CHECK ELIGIBILITY button explaining what happens next (Step 5) — 'We'll send you an OTP to verify your number' would set accurate expectations. (5) The four loan variant labels — 'Flexi Hybrid', 'Dropline', 'Instalment pattern' — are jargon-heavy with no supporting plain-language descriptors. |
| Form Design & Data Collection UX | 5.5/10
███████░░░░░ | The CHECK ELIGIBILITY widget (Steps 4–5) is a well-designed micro-form: single field (mobile number), plain-language label, orange high-contrast CTA button — appropriate for a low-literacy user. The pre-filled mobile number in the widget at Step 5 indicates basic session retention. However, the widget provides no progress indication ('Step 1 of 3'), no explanation of what data will be collected beyond the mobile number, and no reassurance about data privacy — critical gaps for a first-time borrower. The full application form is never reached in this journey (OTP gate intervenes), so the deeper form design cannot be assessed. The default loan amount of ₹1,00,000 visible in the loan summary behind the OTP popup (Step 7) suggests forms are not pre-populated to Ramesh's stated need — a personalisation miss. |
| Navigation Depth & Efficiency | 5.0/10
██████░░░░░░ | Homepage → Personal Loan page is achieved in 1 click (Step 1) — efficient. However, from the Personal Loan page, the intended next step (Apply) routes to the wrong page (Step 3), effectively adding an unintended detour. The back navigation at Step 7 works (Ramesh returns to /how-to-apply-for-personal-loan), but there is no breadcrumb trail or progress indicator showing where Ramesh is in the overall journey. The EMI calculator requires scrolling past multiple video card sections to reach (Step 6), with no anchor link or 'jump to calculator' affordance. The four Apply Now buttons on video cards create parallel navigation branches with no signposting. Navigation is efficient at the top level but fractures at depth. |
| Personalisation & Context Awareness | 2.5/10
███░░░░░░░░░ | This is a logged-out journey, so deep personalisation is not expected. However, there are meaningful missed opportunities even for an anonymous user: (1) The loan summary behind the OTP popup (Step 7) defaults to ₹1,00,000 — Ramesh's target of ₹50,000 is never reflected anywhere in the UI, suggesting no contextual inference from navigation. (2) There is no 'Login to see your pre-approved offer' messaging at any point to communicate the value of authenticating. (3) The site does not adapt to Ramesh's Jodhpur location (Rajasthan) — no Hindi language option, no regional context. (4) The CHECK ELIGIBILITY widget (Steps 4–5) asks for a mobile number but gives no indication that this will be used to personalise the experience. Per logged-out journey scoring rules, the absence of personalisation itself is not penalised; the low score reflects the site's failure to communicate what value logging in would deliver and the ₹1,00,000 default that actively contradicts Ramesh's context. |
| Pre-Sales Support & Help Availability | 4.0/10
█████░░░░░░░ | An EMI calculator exists on /how-to-apply-for-personal-loan (Step 6) but is below the fold with no above-fold signposting — a user who doesn't scroll will miss it entirely. The CHECK ELIGIBILITY widget (Step 4) functions as a soft pre-sales tool but is positioned as a conversion entry rather than a help resource, and the OTP gate means it delivers no pre-sales value to Ramesh. No chatbot, FAQ section, or 'Chat with us' contact option is observed during the journey steps documented. There is no eligibility explainer ('You need a CIBIL score of 650+ — check yours free here') accessible without starting an application. For a first-time borrower with genuine eligibility anxieties, the absence of a low-commitment help path (chatbot, FAQ, pre-qualification tool without OTP) is a significant gap. |
| Visual Hierarchy & Scannability | 4.5/10
█████░░░░░░░ | The /personal-loan page (Step 2) has good visual hierarchy above the fold — trust badges, key stats, and a prominent APPLY CTA are scannable in under 5 seconds. However, the homepage (Step 1) is visually overloaded: Summer Deals banner, Mobiles on EMI hero carousel, 6+ product cards with simultaneous Apply Now CTAs, and promotional noise compete for attention. The /how-to-apply-for-personal-loan page (Step 3) has poor scannability — a dense fee table is the first substantive content after a section heading, with no visual hierarchy separating fees from product benefits. The four video card variants (Step 6) present equal visual weight to all four loan types with no highlighting of the most appropriate option for a new borrower. The EMI calculator below the fold (Step 6) is not visible in the scan zone and has no teaser element above the fold. Key stats like 'minimum loan ₹40,000' are not visually prominent for a user checking if ₹50,000 qualifies. |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Typed | 2000 |
| Emotion | 😰 Anxious |
| CX Note
Page appears completely blank at step 1 — only a light blue-grey background is visible with no navigation, CTAs, or content. For a low-literacy mobile user like Ramesh on slow internet, a blank loading screen with no spinner, progress indicator, or skeleton UI creates immediate anxiety. There is no reassurance that the site is working. A loading indicator or skeleton screen would significantly reduce abandonment risk at this stage. |
| --- |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
The homepage icon strip is a positive UX element for low-literacy users — "Personal Loan" is clearly labeled with an icon and visible above the fold without scrolling. However, the page is visually busy: a Summer Deals banner, a large Mobiles on EMI hero carousel, multiple carousels, and 6+ product cards compete for attention. For Ramesh (daily wage worker, first-time borrower), the clutter could cause momentary confusion. The Personal Loan icon in the quick-access strip is a key findability signal — its prominent placement aids navigation, but the sheer volume of competing CTAs (Apply Now buttons for 4 different products visible simultaneously) could overwhelm a low-literacy user. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Strong trust signals are visible above the fold on the Personal Loan page: "Trusted by 3 lakh+ customers", 4.8 rating, "No collateral and no hidden charges", and "disbursement in 24 hours*". For a low-literacy user like Ramesh, these bullet points in simple language are highly effective reassurance. However, the CIBIL score requirement of 650+ is buried in the body paragraph — not highlighted in the key features. For a first-time borrower who may not know their CIBIL score, this is a critical eligibility blocker that should be surfaced more prominently (e.g., as a key eligibility callout near the APPLY button). The loan range ₹40,000–₹55 lakh is mentioned in the text but not visually emphasized as a hero stat, which could cause a low-literacy user to miss whether their ₹50,000 need qualifies. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😕 Confused |
| CX Note
Critical friction: Clicking "APPLY" on the Personal Loan product page redirected Ramesh to a 'How to apply' informational guide page (URL: /how-to-apply-for-personal-loan) instead of an application form or loan eligibility check. For a low-literacy, first-time borrower like Ramesh, this is deeply confusing — he expected a form to fill in, but instead sees a wall of fee information (interest 10–30% p.a., bounce charges ₹700–1,200, prepayment charges up to 4.72%, penal charge up to 36% p.a.). This fee table with dense financial jargon — especially the 36% penal charge — is likely to alarm or overwhelm a daily wage worker unfamiliar with lending terminology. No clear 'Apply Now' CTA is visible above the fold on this page, meaning Ramesh has hit a dead end in his mental model of the journey. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Typed | 8826100789 |
| Emotion | 🙂 Hopeful |
| CX Note
The sticky "CHECK ELIGIBILITY" widget at the bottom right is a strong UX element for low-literacy users like Ramesh — it uses plain language, asks for only one piece of information (mobile number), and promises to check eligibility without requiring immediate commitment. However, the widget competes visually with four separate "Apply Now" buttons on the video cards, creating decision paralysis for a user unsure where to start. The floating widget's orange CTA button contrasts well but is small relative to the video card Apply Now buttons. Critically, the 'Check Eligibility' path is NOT the same as 'Apply Now' — there is no clear communication to the user about what happens next after entering their mobile number, which could cause anxiety for a first-time borrower wary of sharing personal data. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
The mobile number field already shows "8826100789" pre-filled from the previous step, and the orange CHECK ELIGIBILITY button is the immediate next action. This two-step micro-conversion flow (enter mobile → check eligibility) is good UX for low-literacy users — it breaks the intimidating "Apply" journey into a smaller, less threatening first step. However, there is ZERO disclosure about what happens after clicking this button: Will it send an OTP? Will it show an eligibility result immediately? Will it share data with third parties? For a daily wage worker like Ramesh who is wary of sharing personal information, this lack of "next step" communication is a trust gap. A simple "We'll check your eligibility in seconds. No impact on your credit score." label under the CTA would significantly reduce anxiety and abandonment risk at this critical micro-conversion point. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| CX Note
The page shows 4 video cards ("Personal loan for all your needs") with Apply Now buttons for Flexi Hybrid, Flexi Term, Term Loan, and One IVR — but these loan type variants are introduced with NO plain-language explanation of which is best for a first-time borrower needing ₹50,000. The jargon ("Flexi Hybrid", "Dropline", "Instalment pattern") is dense and unexplained for a low-literacy user like Ramesh. A simple recommendation like "Best for first-time borrowers: Term Loan" would dramatically reduce decision paralysis. The EMI calculator is below the fold and needs scrolling to reach — its presence is not signalled above the fold by a prominent anchor link, which means many users will miss it. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
CRITICAL FRICTION: The CHECK ELIGIBILITY flow triggered an OTP verification popup after Ramesh entered his mobile number — gating the entire application journey behind phone authentication before he can even see his eligibility or loan terms. For a daily wage worker like Ramesh who is wary of sharing personal data and unfamiliar with OTP flows, this is a high-abandonment risk moment. The popup provides NO explanation of WHY OTP is needed at this stage, NO privacy reassurance ("Your number won't be shared"), and NO alternative path (e.g., "Browse without OTP"). The OTP popup header "Verification required" is functional but not reassuring — a message like "Quick security check — we'll never share your number" would reduce anxiety. Additionally, the loan summary visible behind the popup shows ₹1,00,000 as the default loan amount — NOT Ramesh's target of ₹50,000 — meaning even if he passed OTP, he'd see an irrelevant default figure first. The "Change" link next to the mobile number is a positive micro-UX element (lets user correct mistakes), but the overall gate creates friction before value delivery. |
| --- |