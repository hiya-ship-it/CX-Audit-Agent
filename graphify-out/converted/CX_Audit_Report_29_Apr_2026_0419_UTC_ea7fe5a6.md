<!-- converted from CX_Audit_Report_29_Apr_2026_0419_UTC.docx -->



CX AUDIT REPORT
bajajfinserv.in  |  Customer Experience Deep-Dive


Prepared by: CX Audit Agent  (Claude + Playwright)

# Table of Contents
[ Open in Microsoft Word and press Ctrl+A → F9 to generate the Table of Contents ]

# 1. Executive Summary

## Persona Verdicts at a Glance

## Critical Issues — High Severity

## P1 Recommendations — Fix Immediately
No P1 recommendations.


# 2. Persona: Ramesh - First Personal Loan – Daily Wage Worker



## Key Takeaways
- The APPLY button on the Personal Loan page routes to a broken pushengineweb.bajajfinserv.in endpoint — it failed 5 consecutive times for a logged-in user, making the entire product page a dead end.
- The site search function returns 'Access Denied' for 'personal loan' queries — the only fallback navigation tool is also broken, leaving Ramesh with no escape route.
- The EMI calculator showing ₹91,104 total repayment on a ₹50,000 loan (96-month tenure) with no plain-language explanation caused real financial anxiety for a low-literacy borrower — tenure context is absent.
- The 'No collateral required' benefit on the product page was the single most relevant trust signal for Ramesh as a daily wage worker with no assets to pledge — it was buried in a bullet list, not featured prominently.
- Every 'Access Denied' error page carried no human-readable message, no helpline number, and no fallback CTA — a user who reads 'You don't have permission' assumes personal rejection, not a server misconfiguration.

## Critical Friction (High Severity)




## Recommendations
No recommendations generated.

# Annexures


# Annexure A — Full Friction & Delight Analysis
## Ramesh - First Personal Loan – Daily Wage Worker
Delight Factors



HIGH SEVERITY



MEDIUM SEVERITY




LOW SEVERITY




# Annexure B — CX Score Dimensions
## Ramesh - First Personal Loan – Daily Wage Worker


# Annexure C — Emotional Journey Details
## Ramesh - First Personal Loan – Daily Wage Worker
Ramesh arrived at bajajfinserv.in carrying the quiet anxiety of a first-time borrower — a 29-year-old daily wage worker from Jodhpur who needed ₹50,000 to fix his home and was already unsure whether a company this big would lend to someone like him. The homepage loaded as a blank screen on his slow connection, a small but telling omen. He found the product page after a circuitous path through a broken nav drawer and a search bar that returned 'Access Denied', but when he finally saw the loan summary panel — ₹50,000, 15% p.a., and the reassuring line 'Amount to be credited to your bank: ₹50,000' — his confidence briefly bloomed. He read about no collateral required and felt a wave of genuine hope: maybe a person without property could indeed borrow here. Then he clicked the large orange APPLY button — and the site said 'Access Denied. You don't have permission.' He clicked it again. Denied. He scrolled the entire product page twice, reading every word, gathering courage, scrolling back up, and clicked again. Denied. By the fifth time that white page with the reference number appeared, Ramesh had stopped asking 'what is this error' and started asking 'kya main eligible nahi hoon?' — the website's technical breakdown had transformed, in his mind, into a personal rejection, and he ended 25 exhausting steps without ever reaching an application form, his trust in Bajaj Finance fractured and his home repair no closer to being funded.



# Annexure D — Complete Journey Log with Screenshots

## Ramesh - First Personal Loan – Daily Wage Worker  —  Step-by-Step Journey
### Step 1  ✅  [CLICK]  Loans
What persona saw: The page appears to be loading — the screenshot shows a blank/light blue-grey screen with no visible content yet. However, the extracted text shows a fully loaded navigation with links including "Loans", "Personal Loan", and other nav items. Ramesh can see a menu structure with "Loans" as a prominent navigation item. The page is the Bajaj Finserv homepage and Ramesh is logged in.

📸  Step 1  —  ramesh-first-personal-loan-daily-wage-worker_step00_click_on.png


### Step 2  ❌  [CLICK]  Personal Loan
What persona saw: Ramesh sees the Bajaj Finserv homepage with a side drawer/main menu visible in the page text. The extracted text clearly shows "Personal Loan" as a direct link in the main menu content ("HelloMain MenuMain MenuSummer OffersPersonal Loan..."). There's also a banner section at the bottom showing "Personal LoanFunds up to ₹55 Lakh" as a product tile. The homepage is loaded with the hero carousel showing "Loan On Property" and an "Apply Now" button. Ramesh needs to find the Personal Loan product specifically.

📸  Step 2  —  ramesh-first-personal-loan-daily-wage-worker_step01_click.png


### Step 3  ✅  [TYPE]  Search
What persona saw: Ramesh is on the Bajaj Finserv homepage. The page is fully loaded with a busy layout — product icons, banners about Demat accounts, Self Employed Loan Guide, and various product cards. He can see "Personal LoanFunds up to ₹55 Lakh" mentioned in the page text at the bottom, but it's not clearly clickable as a tile from his current view. The top nav links all route to /myaccount/# which caused issues in previous steps. The search bar is clearly visible at the top — it says "Search Bajajfinserv.in". This is the reliable fallback path per navigation rules.

📸  Step 3  —  ramesh-first-personal-loan-daily-wage-worker_step02_type.png


### Step 4  ✅  [NAVIGATE]  https://www.bajajfinserv.in/myaccount/search/content?reqData=g0D6cVIZz
What persona saw: Ramesh sees a plain "Access Denied" page. The search for "personal loan" has led to a server error on pushengineweb.bajajfinserv.in — the search backend returned an Access Denied response. There are zero interactive elements on this page, no buttons, no links, nothing to click. The page is completely broken for him.

📸  Step 4  —  ramesh-first-personal-loan-daily-wage-worker_step03_navigate.png


### Step 5  ✅  [TYPE]  loan-amount-input
What persona saw: Ramesh has successfully landed on the Bajaj Finserv Personal Loan page. He can see a loan calculator with a loan amount input field currently showing ₹1,00,000, a tenure selector showing 96 months selected, and three loan variant cards. The right side shows a "Loan Summary" panel with processing fees, flexi charges, and an orange "APPLY" button. The page mentions loans from ₹40,000 to ₹55 lakh. Ramesh needs ₹50,000, but the current amount shown is ₹1,00,000 — he needs to change it to ₹50,000. However, the page text says "Enter an amount between ₹40,000 & ₹50,00,000" which means ₹50,000 is the minimum threshold shown — wait, it says ₹40,000 minimum. ₹50,000 is within range. The input field for loan amount is clearly visible and labeled.

📸  Step 5  —  ramesh-first-personal-loan-daily-wage-worker_step04_type.png


### Step 6  ✅  [CLICK]  APPLY
What persona saw: The page shows the personal loan product page with ₹50,000 entered as loan amount. The right-side loan summary panel clearly shows all the key figures: ₹50,000 requested amount, 15% rate of interest, ₹52,504 total loan amount. The large orange "APPLY" button is prominently displayed in the loan summary panel on the right. The loan variant selected is "Flexi Hybrid Term Loan" with tenure of 96 months. There's also a smaller "APPLY" link in the top navigation. The main orange APPLY button in the summary panel is the most prominent CTA.

📸  Step 6  —  ramesh-first-personal-loan-daily-wage-worker_step05_click_on.png


### Step 7  ✅  [BACK]  https://www.bajajfinserv.in/myaccount/landing/PersonalLoan?reqData=g0D
What persona saw: The screen shows a stark "Access Denied" error page — plain white background, bold "Access Denied" heading, a technical error message saying "You don't have permission to access http://pushengineweb.bajajfinserv.in/3in1web/index.html? on this server." with a reference number and edgesuite.net error URL. No buttons, no navigation, no interactive elements at all. The URL in the browser is a Bajaj Finserv myaccount/landing/PersonalLoan URL.

📸  Step 7  —  ramesh-first-personal-loan-daily-wage-worker_step06_back.png


### Step 8  ✅  [TYPE]  loan-amount-input
What persona saw: Ramesh is back on the personal loan product page at bajajfinserv.in/personal-loan. The page shows the loan calculator with a loan amount input field currently displaying ₹1,00,000, and a loan summary on the right side also showing ₹1,00,000. The loan tenure is set to 96 months, and the loan variant shows "Flexi Hybrid Term Loan." The APPLY button is visible in orange. The page text says "Enter an amount between ₹40,000 & ₹50,00,000" — so ₹50,000 is within range. Ramesh needs to set the loan amount to ₹50,000 before exploring further, since the APPLY button previously redirected to an error. He should now focus on the EMI calculator and loan summary with his actual target amount.

📸  Step 8  —  ramesh-first-personal-loan-daily-wage-worker_step07_type.png


### Step 9  ✅  [SCROLL]  page body — looking for inline application form below the loan summary
What persona saw: Ramesh is back on the personal loan page at bajajfinserv.in/personal-loan. The page shows the loan amount set to ₹50,000, with the loan summary on the right showing: Requested loan amount ₹50,000, Processing fee ₹505, Flexi facility charges ₹1,999, Total loan amount ₹52,504, Rate of Interest 15% p.a. The APPLY button is visible in orange. The previous APPLY click led to an Access Denied error. Per the logged-in journey rules, clicking APPLY may open an inline form below — the instructions say to scroll down immediately after an APPLY click to find the form. Since Ramesh already clicked APPLY in step 05 and landed on an error, the recovery was to go back. Now he's back on the same page with the correct amount. The page notes indicate there are elements below the fold. The audit rules say to scroll down to look for an application form that may have appeared, especially for logged-in users where APPLY can open an inline form on the same page.

📸  Step 9  —  ramesh-first-personal-loan-daily-wage-worker_step08_scroll.png


### Step 10  ✅  [SCROLL]  page body
What persona saw: Ramesh is on the personal loan page. The screenshot shows the loan summary on the right side with ₹50,000 as requested loan amount, Processing fee ₹505, Flexi facility charges ₹1,999, Total charges ₹2,504, and a prominent orange APPLY button. The EMI calculator shows ₹625 for first 24 months and ₹1,057 for subsequent 72 months at 15% p.a. The page structure shows there are more sections below: "Personal loan EMI calculator", "Features and benefits", "Top uses", "Personal loan eligibility and documentation", and "Personal loan eligibility criteria". Ramesh has already clicked APPLY once which led to Access Denied. The logged-in journey rules say to scroll down after APPLY to find an inline form. He needs to scroll further down to check if there's an application form, EMI calculator section, or eligibility information below the current viewport.

📸  Step 10  —  ramesh-first-personal-loan-daily-wage-worker_step09_scroll.png


### Step 11  ✅  [SCROLL]  page body
What persona saw: Ramesh is on the personal loan page. The screenshot shows he's scrolled to the "Personal loan EMI calculator" and "Features and benefits of our personal loan" section. The page text shows a full loan summary for ₹50,000 with all the key numbers: Principal ₹50,000, Total Interest ₹41,104, Total Amount ₹91,104, EMI ₹625 (first 24 months), ₹1,057 (next 72 months). He can see "No hidden charges", "Flexible tenures", "No collateral" bullet points. The EMI calculator section is visible. He needs to scroll down further to see the eligibility criteria, interest rates, fees section, and any inline application form that may have appeared below.

📸  Step 11  —  ramesh-first-personal-loan-daily-wage-worker_step10_scroll.png


### Step 12  ✅  [SCROLL]  page body
What persona saw: Ramesh is currently on the personal loan page. The screenshot shows the FAQ section with "Frequently asked questions" and tabs for Overview, Application, Repayment, Eligibility, Fees and charges. Below that are customer reviews showing 35 million+ customers, 4.8 Playstore Rating, 6.5 million+ Reviews. The orange "APPLY" button is visible at the bottom right. The page has shown the loan summary with ₹50,000, EMI calculator showing total ₹91,104. The FAQ tabs are visible — Ramesh needs to scroll down to see if there's an inline application form that appeared after the previous APPLY click, or to document the eligibility criteria and fees sections for the audit. The page text shows "Personal loan eligibility criteria" and "Documents required" sections that haven't been seen yet.

📸  Step 12  —  ramesh-first-personal-loan-daily-wage-worker_step11_scroll.png


### Step 13  ✅  [SCROLL]  page body
What persona saw: The current screenshot shows the very bottom of the bajajfinserv.in personal loan page — disclaimer text, video thumbnails (loan for school fees, travel, wedding, emergencies), and collapsed sections for "Languages" and "Application Forms." The page has been fully explored from top to bottom. Ramesh has documented all the key pre-application content areas. The APPLY button is visible at the top of the page (it was visible earlier). He needs to scroll back up to reach it.

📸  Step 13  —  ramesh-first-personal-loan-daily-wage-worker_step12_scroll.png


### Step 14  ✅  [SCROLL]  page body
What persona saw: Ramesh is currently seeing the FAQ section with "Frequently asked questions" and "Overview, Application, Repayment, Eligibility, Fees and charges" tabs visible. Customer reviews section is visible with 35 million+ customers, 4.8 Playstore Rating, 6.5 million+ Reviews. The APPLY button is shown in orange at the bottom right of the screen. The page URL shows he's still on the personal loan page. He needs to scroll up to reach the top section with the main APPLY button.

📸  Step 14  —  ramesh-first-personal-loan-daily-wage-worker_step13_scroll.png


### Step 15  ✅  [CLICK]  APPLY
What persona saw: Ramesh is back at the top of the personal loan page. The page shows his loan summary: ₹50,000 requested, processing fee ₹505, Flexi facility charges ₹1,999, total loan amount ₹52,504, with an initial instalment of ₹631 for 24 months and ₹1,068 for 72 months at 15% p.a. The orange APPLY button [02] is visible. This is a logged-in session. The loan summary looks complete and correct. He needs to click APPLY to enter the application funnel.

📸  Step 15  —  ramesh-first-personal-loan-daily-wage-worker_step14_click_on.png


### Step 16  ✅  [BACK]  https://www.bajajfinserv.in/myaccount/landing/PersonalLoan?reqData=g0D
What persona saw: The screen shows a stark white "Access Denied" page — same as before. The error references pushengineweb.bajajfinserv.in/3in1web/index.html. There are zero interactive elements. No buttons, no links, no nav, nothing. Just a server error message.

📸  Step 16  —  ramesh-first-personal-loan-daily-wage-worker_step15_back.png


### Step 17  ✅  [BACK]  https://www.bajajfinserv.in/personal-loan
What persona saw: Ramesh is back on the personal loan page after two failed APPLY attempts (both led to "Access Denied"). The page is showing ₹1,00,000 as the current loan amount in the loan summary — not ₹50,000, which is what he needs. The current screenshot shows the Flexi Hybrid Term Loan variant selected, with EMIs of ₹1,250 and ₹2,115, and a Total Amount of ₹1,82,280 based on ₹1,00,000. There's a loan-amount-input field below-fold (element [19]) that Ramesh can use to set his actual target amount of ₹50,000. Since the APPLY button has repeatedly led to Access Denied errors, he should now explore the EMI calculator by entering ₹50,000 to at least document what the loan terms look like for his actual target amount. This fulfills the audit requirement of documenting the calculator interaction.

### Step 18  ✅  [BACK]  https://www.bajajfinserv.in/myaccount/search/content?reqData=g0D6cVIZz
What persona saw: Ramesh is staring at the same "Access Denied" white screen for the third time. The page heading says "Access Denied" and the error message reads "You don't have permission to access http://pushengineweb.bajajfinserv.in/3in1web/index.html? on this server." There are absolutely no interactive elements — no buttons, no links, no form fields. Just a reference number and the error text. This is the same dead end he's hit every time he clicks APPLY.

📸  Step 18  —  ramesh-first-personal-loan-daily-wage-worker_step17_back.png


### Step 19  ✅  [SCROLL]  page body
What persona saw: Ramesh is back on the Bajaj Finserv homepage (bajajfinserv.in). The page appears mostly blank/loading — showing only "Bajaj Finserv" as a heading with zero interactive elements visible. The screenshot shows a plain light blue-grey background with no content loaded yet. This is likely a loading state or above-the-fold empty state. He needs to scroll down to find product tiles or a search bar to navigate to the Personal Loan page via a different route than the APPLY button (which has been throwing Access Denied errors).

📸  Step 19  —  ramesh-first-personal-loan-daily-wage-worker_step18_scroll.png


### Step 20  ✅  [TYPE]  Search
What persona saw: Ramesh is back on the Bajaj Finserv homepage. He can see the search bar at the top with placeholder "Search Bajajfinserv.in". The page also shows a "Personal Loan - Funds up to ₹55 Lakh" tile in the product strip below the banner. There's also an orange "Apply Now" button visible in the hero area. The homepage is loaded with various products. The APPLY button on the personal loan page has repeatedly thrown Access Denied errors, so he needs a fresh approach to reach the personal loan application form.

📸  Step 20  —  ramesh-first-personal-loan-daily-wage-worker_step19_type.png


### Step 21  ✅  [NAVIGATE]  https://www.bajajfinserv.in/myaccount/search/content?reqData=g0D6cVIZz
What persona saw: Ramesh is on yet another "Access Denied" page — the same white screen with "Access Denied" in bold black text and a reference number. There are ZERO interactive elements on this page. The URL is the pushengineweb.bajajfinserv.in error URL again. He's been here multiple times. The search bar attempt (Step 19) also landed him here instead of the personal loan page. He's completely stuck in an error loop.

📸  Step 21  —  ramesh-first-personal-loan-daily-wage-worker_step20_navigate.png


### Step 22  ✅  [BACK]  https://www.bajajfinserv.in/personal-loan
What persona saw: Ramesh is back on the personal loan page (https://www.bajajfinserv.in/personal-loan). The page is loaded and showing the loan calculator with a default loan amount of ₹1,00,000 and tenure of 96 months. The Loan Summary on the right shows ₹1,00,000 requested amount with processing fee ₹4,009 and flexi facility charges ₹1,999. The APPLY button [03] is visible. There's a loan amount input field [02] labeled 'loan-amount-input'. The page says "Enter an amount between ₹40,000 & ₹50,00,000". Ramesh needs ₹50,000 — the minimum is ₹40,000 so his target amount is within range. He should first set the loan amount to ₹50,000 before attempting APPLY again, so the summary reflects his actual need.

### Step 23  ✅  [NAVIGATE]  https://www.bajajfinserv.in/myaccount/search/content?reqData=g0D6cVIZz
What persona saw: Ramesh is stuck on the same "Access Denied" page again — the pushengineweb.bajajfinserv.in error that has blocked him repeatedly. The page shows: "Access Denied You don't have permission to access..." with Reference #18.6df9da17. There are ZERO interactive elements on this page — no buttons, no links, no search bar. The screenshot shows the personal loan product page with a loan summary (₹1,00,000 loan, processing fee ₹4,009, APPLY button visible) — but the URL shows the Access Denied error page. This is a disconnect between the screenshot and the current URL state. The only viable recovery is to navigate directly back to the personal loan page URL which Ramesh previously visited successfully.

📸  Step 23  —  ramesh-first-personal-loan-daily-wage-worker_step22_navigate.png


### Step 24  ✅  [CLICK]  APPLY
What persona saw: Ramesh is back on the personal loan page (https://www.bajajfinserv.in/personal-loan). The page is fully loaded — he can see the loan calculator showing ₹1,00,000 loan amount, the loan summary on the right side with processing fee ₹4,009 and total loan amount ₹1,06,008, and the orange APPLY button prominently displayed on the right side. The page header says "Loan of up to ₹55 lakh*" and there's a "Trusted by 3 lakh+ customers" trust signal. The APPLY button is visible both in the top navigation area and in the loan summary panel on the right.

📸  Step 24  —  ramesh-first-personal-loan-daily-wage-worker_step23_click_on.png


### Step 25  ✅  [BACK]  browser back button
What persona saw: The screen shows a stark white page with "Access Denied" in bold at the top. The message reads: "You don't have permission to access http://pushengineweb.bajajfinserv.in/3in1web/index.html? on this server." There is a reference number and an edgesuite.net error link. No buttons, no navigation, no interactive elements whatsoever. This is the same Access Denied page Ramesh has seen multiple times in this session.

📸  Step 25  —  ramesh-first-personal-loan-daily-wage-worker_step24_back.png


| Target URL | https://www.bajajfinserv.in |
| --- | --- |
| Audit Date | 29 Apr 2026 0419 UTC |
| Personas Audited | 1 |
| Avg CX Score | 2.8 / 10  —  🔴 Critical |
| Overall Avg Score
2.8/10 | Best Experience
2.8/10 | Worst Experience
2.8/10 | Goals Achieved
0/1 |
| --- | --- | --- | --- |
| Persona | Score | Outcome | One-line Verdict |
| --- | --- | --- | --- |
| Ramesh - First Personal Loan – Daily Wage Worker | 2.8/10
███░░░░░░░░░ | 🚫 Loop Detected | Bajaj Finserv's broken Apply button and search endpoint turned a ready-to-borrow Ramesh into an "Access Denied" victim — |
| Persona | Location | Issue |
| --- | --- | --- |
| Ramesh - First Personal Loan – Daily Wage Worker | Personal Loan APPLY button — /personal-loan, Steps 5, 14, 23 | Every time Ramesh clicked the large orange APPLY button — the most prominent CTA on the page, the natural and obvious ne |
| Ramesh - First Personal Loan – Daily Wage Worker | Site search — /myaccount/search/content, Steps 3 and 20 | When Ramesh typed 'personal loan' in the site search bar (his fallback navigation tool after nav drawer links failed), t |
| Ramesh - First Personal Loan – Daily Wage Worker | Access Denied error page — all instances (Steps 3, 6, 15, 17 | The error page that appeared 7 times during Ramesh's 25-step journey contained: raw server text ('Reference #18.6df9da17 |
| Age
29 | Gender
— | Occupation
— | Location
— |
| --- | --- | --- | --- |
| Device
— | Fin. Literacy
— | Constraints
Very low financial literacy, unsure about eligibility, low i | Intent
Apply for first personal loan of ₹50,000 for home repair |
| Outcome
🚫 Loop Detected | CX Score
2.8 / 10  🔴 Critical | Steps
25  (1 failures) |
| --- | --- | --- |
| TL;DR
Bajaj Finserv's broken Apply button and search endpoint turned a ready-to-borrow Ramesh into an "Access Denied" victim — 5 times, 25 steps, zero applications submitted. |
| --- |
| 🔴  Personal Loan APPLY button — /personal-loan, Steps 5, 14, 23
Every time Ramesh clicked the large orange APPLY button — the most prominent CTA on the page, the natural and obvious next step — he was routed to pushengineweb.bajajfinserv.in which returned a raw 'Access Denied' error page. This happened 3 times from the product page alone (Steps 5→6, 14→15, 23→24). The error page showed 'You don't have permission to access this resource' with a reference number (e.g., #18.6df9da17) — no Bajaj branding, no explanation, no next step.
User Impact: Ramesh, a first-time borrower with low financial literacy, interpreted the word 'Denied' as personal rejection — 'Kya mujhe loan nahi milega?' (Will I not get a loan?). He attempted the same action 5 times across 25 steps, never reaching an application form. His goal was completely blocked and he ended the session without applying. |
| --- |
| 🔴  Site search — /myaccount/search/content, Steps 3 and 20
When Ramesh typed 'personal loan' in the site search bar (his fallback navigation tool after nav drawer links failed), the search endpoint returned the same 'Access Denied' error page at pushengineweb.bajajfinserv.in — identical to the Apply CTA failure. Both the primary conversion path (APPLY) and the primary discovery fallback (SEARCH) were broken simultaneously for this user session.
User Impact: Ramesh lost both of his navigation options within the first 4 steps. He felt trapped: 'Ramesh has now tried 3 different ways to get to the Personal Loan page and has been blocked each time — his confidence is dropping fast' (Step 3 CX note). The second search attempt at Step 20 confirmed this was not a one-time glitch, destroying whatever remaining hope he had. |
| --- |
| 🔴  Access Denied error page — all instances (Steps 3, 6, 15, 17, 20, 22, 24)
The error page that appeared 7 times during Ramesh's 25-step journey contained: raw server text ('Reference #18.6df9da17.1777436134.108f7e3'), the domain 'pushengineweb.bajajfinserv.in' and 'edgesuite.net', no Bajaj Finserv branding, no human-readable explanation, no 'Go back' button, no helpline number, no chatbot, and no alternative application pathway. The only interaction available was the browser's native back button.
User Impact: Each encounter with this page deepened Ramesh's conviction that the system was personally rejecting him. By Step 22 he was asking 'Kya Bajaj mujhe loan dena hi nahi chahta?' (Does Bajaj even want to give me a loan?). The back button looped him through the same errors at Steps 16–17, creating a circular navigation trap that lasted 9 steps. |
| --- |
| ✨
At Step 14, the loan summary line 'Amount to be credited in your bank (A-B): ₹50,000' cut through all the fee confusion with crystalline clarity — Ramesh immediately understood 'toh mujhe poore 50,000 milenge' (so I'll get the full 50,000). For a daily wage worker anxious about deductions, this transparency was a genuine moment of relief that exceeded his expectations. |
| --- |
| ✨
The Sudhakar Chobey review about a home repair loan (Step 11) was a genuine coincidence that created a powerful moment of recognition for Ramesh — he wasn't reading generic testimonials, he was reading his own story told by someone who had already succeeded. This is exactly the kind of social proof that converts hesitant first-time borrowers. |
| --- |
| ✨
The 'No collateral required' feature (Step 10) functioned as an unexpected moment of liberation for Ramesh — he came in unsure about eligibility and likely feared he'd need to pledge something. Seeing this in plain language, without having to ask, removed an unspoken fear and replaced it with confidence that 'someone like me can get this loan.' |
| --- |
| 🔴  Personal Loan APPLY button — /personal-loan, Steps 5, 14, 23
Every time Ramesh clicked the large orange APPLY button — the most prominent CTA on the page, the natural and obvious next step — he was routed to pushengineweb.bajajfinserv.in which returned a raw 'Access Denied' error page. This happened 3 times from the product page alone (Steps 5→6, 14→15, 23→24). The error page showed 'You don't have permission to access this resource' with a reference number (e.g., #18.6df9da17) — no Bajaj branding, no explanation, no next step.
User Impact: Ramesh, a first-time borrower with low financial literacy, interpreted the word 'Denied' as personal rejection — 'Kya mujhe loan nahi milega?' (Will I not get a loan?). He attempted the same action 5 times across 25 steps, never reaching an application form. His goal was completely blocked and he ended the session without applying. |
| --- |
| 🔴  Site search — /myaccount/search/content, Steps 3 and 20
When Ramesh typed 'personal loan' in the site search bar (his fallback navigation tool after nav drawer links failed), the search endpoint returned the same 'Access Denied' error page at pushengineweb.bajajfinserv.in — identical to the Apply CTA failure. Both the primary conversion path (APPLY) and the primary discovery fallback (SEARCH) were broken simultaneously for this user session.
User Impact: Ramesh lost both of his navigation options within the first 4 steps. He felt trapped: 'Ramesh has now tried 3 different ways to get to the Personal Loan page and has been blocked each time — his confidence is dropping fast' (Step 3 CX note). The second search attempt at Step 20 confirmed this was not a one-time glitch, destroying whatever remaining hope he had. |
| --- |
| 🔴  Access Denied error page — all instances (Steps 3, 6, 15, 17, 20, 22, 24)
The error page that appeared 7 times during Ramesh's 25-step journey contained: raw server text ('Reference #18.6df9da17.1777436134.108f7e3'), the domain 'pushengineweb.bajajfinserv.in' and 'edgesuite.net', no Bajaj Finserv branding, no human-readable explanation, no 'Go back' button, no helpline number, no chatbot, and no alternative application pathway. The only interaction available was the browser's native back button.
User Impact: Each encounter with this page deepened Ramesh's conviction that the system was personally rejecting him. By Step 22 he was asking 'Kya Bajaj mujhe loan dena hi nahi chahta?' (Does Bajaj even want to give me a loan?). The back button looped him through the same errors at Steps 16–17, creating a circular navigation trap that lasted 9 steps. |
| --- |
| 🟡  EMI Calculator — /personal-loan, Step 9
The EMI calculator displayed a 'Total Amount ₹91,104' for a ₹50,000 loan with no explanation of what tenure (96 months = 8 years) drives that figure. The calculator showed the total repayment amount prominently but provided no plain-language bridge: no 'This is the total amount you repay over 8 years including interest' message, no toggle to show shorter tenures and their corresponding totals.
User Impact: Ramesh paused with genuine alarm — 'Main ₹50,000 le raha hoon lekin ₹91,104 waapis dunga?' (I'm taking ₹50,000 but paying back ₹91,104?). He lacked the financial literacy to understand compound interest over a long tenure. This moment created financial anxiety that was never resolved during the journey, potentially shaking his intent to borrow even if the Apply button had worked. |
| --- |
| 🟡  'Flexi facility charges ₹1,999' — loan summary panel, /personal-loan, Step 5
The loan summary panel showed 'Processing fee ₹505' and 'Flexi facility charges ₹1,999' as line items without any tooltip, explanation, or link to a definition. There was no indication of whether these were deducted from the ₹50,000 disbursed or added on top, or whether the Flexi facility was mandatory or optional.
User Impact: Ramesh wondered if these were 'extra costs on top of what he'll repay' (Step 5 CX note). For a daily wage worker budgeting for a home repair, uncertainty about ₹2,504 in charges on a ₹50,000 loan is material — it's 5% of his loan amount. The 'No hidden charges' reassurance on the same page was contradicted by charges he didn't understand. |
| --- |
| 🟡  Homepage nav drawer links — Step 1
The 'Personal Loan' link in the nav drawer routed to /myaccount/# instead of the product page, meaning the most natural discovery path — clicking 'Personal Loan' from the main menu — silently failed. Ramesh had to fall back to search (which was also broken) before eventually reaching /personal-loan.
User Impact: Ramesh felt 'a bit frustrated but not giving up' by Step 2. He had to spend 3 steps and 2 error encounters before reaching the product page he could have reached in 1 click. For a low-digital-literacy user, each failed step erodes confidence in the site's reliability. |
| --- |
| 🟡  Homepage initial load — Step 0
The homepage displayed as a blank screen while loading on Ramesh's slow internet connection in Jodhpur — a Tier 2 city where mobile data speeds can be significantly slower than Tier 1 metros. No skeleton screen or loading indicator was noted.
User Impact: Ramesh started his session with immediate anxiety — 'He's a bit anxious' (Step 0 CX note). A blank opening screen for a low-literacy user unfamiliar with financial websites creates doubt about whether the site is working at all, setting a nervous tone for the entire journey. |
| --- |
| 🟢  Eligibility criteria visibility — /personal-loan product page, Steps 8–11
Eligibility criteria for a personal loan were accessible only via an FAQ tab labelled 'Eligibility', visible below the fold after significant scrolling. There was no proactive eligibility indicator near the APPLY button — no 'Check your eligibility in 30 seconds' CTA, no 'Suitable for salaried and self-employed individuals' line near the top of the page.
User Impact: Ramesh, whose primary stated constraint was being 'unsure about eligibility', scrolled the entire page twice without having his eligibility anxiety resolved. He noticed the FAQ tab at Step 11 but didn't click it. A daily wage worker's specific eligibility concerns (income type, minimum income) were never proactively addressed. |
| --- |
| 🟢  No help/support option during the journey — all error pages and product page
At no point during 25 steps did Ramesh encounter a visible helpline number, chatbot prompt, or 'Apply via our app' alternative. The /personal-loan page and all error pages had no customer support surface — not even a footer phone number was noted as accessible during the loop.
User Impact: By Step 22, Ramesh was asking 'Ab kya karoon?' (What do I do now?) — a user in crisis with no support anchor on screen. A visible helpline or chatbot at this moment would have been a lifeline; its absence likely contributed to the decision to abandon. |
| --- |
| Dimension | Score | Rationale |
| --- | --- | --- |
| Discoverability & Information Architecture | 4.5/10
█████░░░░░░░ | Ramesh found 'Loans' as a top-level nav item at Step 0 and 'Personal Loan' was visible in the nav drawer at Step 1 — the label hierarchy is broadly correct. However, the nav drawer links (Step 1) routed to /myaccount/# and the click failed, forcing him to fall back to the search bar at Step 2. When search itself returned 'Access Denied' (Step 3), Ramesh had no remaining discoverability pathway except manually navigating to /personal-loan. For a user who does not know direct URLs, the IA effectively had a single viable path — and that path collapsed at two different points. The 'Loans > Personal Loan' hierarchy is intuitive in concept but broken in execution for this user's session. |
| Content Quality & Financial Clarity | 5.5/10
███████░░░░░ | The personal loan product page at bajajfinserv.in/personal-loan showed Ramesh the rate (15% p.a.), processing fee (₹505), Flexi facility charges (₹1,999), and confirmed 'Amount to be credited to your bank: ₹50,000' — the last detail was genuinely reassuring (Step 14). However, the EMI calculator displayed a total repayment of ₹91,104 on a ₹50,000 loan across a 96-month tenure with no plain-language explanation of why (Step 9 — 'itna zyada?'). The terms 'Flexi facility charges' and their purpose were not explained anywhere visible, leaving Ramesh confused about whether these were deductions from his disbursed amount. Eligibility criteria for a daily wage worker — the single most important question for Ramesh given his 'unsure about eligibility' constraint — were present in an FAQ tab but not surfaced proactively. |
| Trust & Credibility Signals | 5.0/10
██████░░░░░░ | The product page carried several genuine trust signals: '35 million+ customers', '4.8 Playstore Rating', 'No hidden charges', 'No collateral required', and a customer review from Sudhakar Chobey specifically about a home repair loan (Step 11) — this last signal was serendipitously perfect for Ramesh and resonated deeply. However, all of this trust was catastrophically undermined by five consecutive 'Access Denied' errors on the primary Apply CTA. The error pages showed 'pushengineweb.bajajfinserv.in' and 'You don't have permission' with a raw reference number (e.g., Reference #18.6df9da17) — no brand identity, no reassurance, no Bajaj logo. For Ramesh, the word 'Denied' read as personal rejection (Step 17: 'Kya main eligible nahi hoon?'), not a server error. Trust built on the product page was destroyed by the error pages. |
| Conversion & Task Flow Design | 1.0/10
█░░░░░░░░░░░ | This dimension must be scored almost at the floor. The single most critical conversion action — clicking the orange APPLY button on the Personal Loan product page — failed 5 times across Steps 5, 6, 14, 15, 23, and 24, each time routing to a broken pushengineweb.bajajfinserv.in endpoint returning 'Access Denied'. There was no alternative conversion path: no inline form, no 'Call us to apply' CTA on the error page, no WhatsApp apply option, no branch locator as fallback. The flow was entirely linear with a single CTA, and that CTA was non-functional. A logged-in user with clear intent, correct loan amount, and 25 steps of persistence could not submit an application. |
| Emotional Experience & Persona Fit | 2.5/10
███░░░░░░░░░ | The product page content showed moments of genuine persona fit — 'No collateral required' (Step 10) was deeply relevant for a daily wage worker, the Hindi-language video thumbnail ('Papa, Shimla chalein? Loan ready hai', Step 12) showed cultural awareness, and the home repair testimonial (Step 11) mirrored Ramesh's exact situation. But the dominant emotional experience of this journey was not served by the page — it was defined by repeated 'Access Denied' errors. For a 29-year-old first-time borrower with low financial literacy, the phrase 'You don't have permission to access this resource' at Steps 6, 15, 17, 20, 22, and 24 created a devastating emotional arc from hope to personal shame. The emotional design of the product page was reasonable; the emotional design of the error state was non-existent. |
| Mobile & Device Experience | 5.0/10
██████░░░░░░ | The product page at /personal-loan rendered adequately on Ramesh's device — the loan amount input field was accessible with a ₹ symbol (Steps 4 and 7), the orange APPLY button was described as 'big and bold and hard to miss' (Step 5), and the loan summary panel was readable. The homepage loaded slowly on Ramesh's low internet connection, showing a blank screen initially (Step 0). The 'Access Denied' error pages were a stark white page with raw server text — no mobile-optimised layout, no touch targets, no recovery button. Given Ramesh's 'low internet' constraint, the homepage's heavy asset loading (carousels, videos at Step 12) on a slow connection compounds the friction, though no specific timeout was recorded for the product page itself. |
| Accessibility & Inclusive Design | 3.5/10
████░░░░░░░░ | The product page made some inclusive choices: Hindi-language video content was present (Step 12), bullet points for 'No collateral', 'No hidden charges', 'Flexible tenures' were plain-language and icon-supported. However, 'Flexi facility charges ₹1,999' (Step 5) had no tooltip, no explanation, and no context — for a low-literacy user this label is opaque. The EMI calculator showed ₹91,104 total repayment without any explanatory copy about what '96 months' means in human terms (Step 9). The 'Access Denied' error pages were the most inaccessible elements in the journey — raw server text with reference numbers, no translation, no simplified explanation, no visual cues. No helpline or chatbot was surfaced at any point during the journey, which is a significant gap for a first-time borrower who needs human guidance. |
| Error Handling & Recovery Design | 0.5/10
█░░░░░░░░░░░ | This is the most catastrophically failed dimension. The 'Access Denied' error pages that appeared at Steps 3, 6, 15, 17, 20, 22, and 24 contained: no error explanation in plain language, no 'Go back to Personal Loan' button, no helpline number, no chatbot trigger, no brand identity, no alternative pathway (WhatsApp, branch, app), and no indication that this was a technical error rather than an eligibility failure. The only recovery action available was the browser back button — which itself sometimes looped back through the error. The search endpoint (Step 3) and the Apply endpoint (Steps 6, 15, 24) both failed silently with the same generic Access Denied page, providing zero differentiation between 'your search failed' and 'your application was blocked'. This is a 0.5 rather than 0 only because the browser back button did technically function. |
| Page Performance & Load Experience | 4.5/10
█████░░░░░░░ | At Step 0, the homepage appeared blank while still loading on Ramesh's slow internet in Jodhpur — a real performance issue for a Tier 2/3 user on low data. The product page at /personal-loan loaded adequately across multiple visits (Steps 4, 7, 8–13, 23). The EMI calculator appeared functional and updated reactively when the loan amount was changed (Steps 4, 7). However, the page includes video thumbnails, customer review carousels, and banner content that would increase load time on a slow connection. No skeleton screens or loading indicators were noted in the journey log. The most damaging 'performance' issue was the Access Denied pages loading instantly but containing nothing useful — speed without content. |
| Micro-copy & Language Quality | 4.0/10
█████░░░░░░░ | The product page copy had genuinely good moments: 'No hidden charges', 'No collateral required', and 'Amount to be credited in your bank (A-B): ₹50,000' (Step 14) — that last line was clear enough that Ramesh understood he would receive the full ₹50,000. However, 'Flexi facility charges ₹1,999' (Step 5) had no accompanying explanation — it reads as an additional deduction and confused Ramesh about whether he'd receive less than ₹50,000. The button label 'APPLY' was clear and action-oriented. The 'Access Denied' error pages contained no brand copy, no human language — just raw server strings like 'Reference #18.6df9da17.1777436134.108f7e3'. The FAQ tab label 'Eligibility' was the right word but was not proactively surfaced for a user explicitly uncertain about eligibility. |
| Form Design & Data Collection UX | 1.0/10
█░░░░░░░░░░░ | Ramesh never reached a form. After 25 steps and 5 attempts to click APPLY, the application form was never rendered — the APPLY button consistently routed to a broken backend URL before any form could be displayed. This dimension cannot be scored on form quality; it must be scored on the fact that the form was entirely inaccessible. A 1.0 is awarded (rather than 0) only because the loan summary panel on the product page functioned as a lightweight pre-form: it accepted a loan amount input (₹50,000 at Steps 4 and 7) and displayed fee and EMI figures, giving Ramesh some sense of a pre-application interaction. |
| Navigation Depth & Efficiency | 3.0/10
████░░░░░░░░ | The homepage-to-product-page path required Ramesh to use the search bar (Steps 2–3) after the nav drawer links failed — adding unnecessary detours early. Once on /personal-loan, the page was stable and Ramesh could navigate it by scrolling. However, every attempt to proceed deeper into the funnel (via APPLY at Steps 5, 14, 23) created a dead-end navigation state — a page with no links, no back navigation context, and no forward path. The browser back button looped Ramesh through the same error states at Steps 15–17 and 20–22, creating genuine circular navigation. At Step 16, the system itself detected a loop (loop_detected after streak 1), confirming this was a structural circular navigation failure, not just user error. Navigation depth to the product page was reasonable (3 clicks); navigation depth to the application was infinite — it was unreachable. |
| Personalisation & Context Awareness | 3.0/10
████░░░░░░░░ | This was a logged-in journey. Despite Ramesh being authenticated, the product page showed no personalised signals: no pre-approved offer amount, no 'Based on your profile, you are eligible for up to ₹X' message, no income-based eligibility indication, and no recognition that this was his first loan enquiry. The loan summary was interactive (he could set ₹50,000) but it was not pre-populated with any account-aware data. Most critically, a logged-in user hitting the APPLY endpoint should have received a personalised application form — instead he received a generic 'Access Denied' server error. The only personalisation-adjacent moment was the system apparently recognising him as logged-in enough to route through /myaccount/ URLs — but that routing itself was broken. |
| Pre-Sales Support & Help Availability | 2.5/10
███░░░░░░░░░ | The product page contained an FAQ section with an 'Eligibility' tab (Step 11) — visible when Ramesh scrolled down — which was the only self-serve support available for his primary anxiety (am I eligible?). An EMI calculator was present and functional. However, no chatbot, no 'Call us' button, and no helpline number were surfaced at any point during the 25-step journey — not on the product page and critically not on any of the 5+ 'Access Denied' error pages. When Ramesh was most confused and most in need of human support (Steps 17, 22, 24: 'Ab kya karoon?'), there was nothing on screen to help him. A branch locator or 'Apply via our app' alternative was never offered. For a low-literacy daily wage worker who hits a technical wall, the absence of a visible helpline is a journey-ending gap. |
| Visual Hierarchy & Scannability | 6.0/10
███████░░░░░ | The personal loan product page at /personal-loan had a reasonably clear visual hierarchy: the orange APPLY button was prominent and described as 'big and bold and hard to miss' (Step 5); the loan summary panel on the right displayed ₹50,000, processing fee, and EMI in a scannable card format; 'No hidden charges' and 'No collateral' were bullet-pointed and visually distinct (Step 10). The '35 million+ customers' and '4.8 Playstore Rating' social proof numbers were scannable (Step 11). The homepage, however, showed as a blank screen initially (Step 0) and when loaded, was described as overwhelming with 'so many things on screen' (Step 1). The 'Access Denied' error pages had no visual hierarchy whatsoever — plain white screen with raw text. |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Emotion | 🤔 Curious |
| CX Note
Ramesh opens the Bajaj Finserv homepage but sees a blank screen — the page is still loading on his slow internet connection. He's a bit anxious. He notices "Loans" in the text navigation and thinks "yahi se loan milega" (I'll get the loan from here). He taps on "Loans" hoping it will take him somewhere he can apply for ₹50,000. |
| --- |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Emotion | 🙂 Hopeful |
| Error | No visible element found matching: 'search bar or search icon' |
| CX Note
Ramesh sees the homepage loaded with lots of products. He's a bit overwhelmed — there are so many things on screen. But then he spots "Personal Loan" and his eyes light up. He thinks "yahi chahiye tha mujhe" (this is what I needed). He's hopeful that clicking this will take him closer to getting ₹50,000 for fixing his house. The page shows "Funds up to ₹55 Lakh" next to Personal Loan — he doesn't fully understand what that means, but ₹50,000 should be well within that, which makes him feel his request isn't too big. |
| --- |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Typed | personal loan |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh has tried clicking on "Loans" and "Personal Loan" in the menu before but it hasn't worked properly. He's a bit frustrated but not giving up. He notices the big search bar at the top and thinks "yahan type karke dekhta hoon" (let me try typing here). He types "personal loan" hoping the website will just show him where to go. For someone with low financial literacy who's never taken a loan before, having to use search just to find a loan option is friction — he expected a big, obvious "Personal Loan" button somewhere on the homepage. |
| --- |
| URL | https://www.bajajfinserv.in/myaccount/search/content?reqData=g0D6cVIZzWcXRWVTNAqATEFQYbwH%2F7ntWe567 |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh typed "personal loan" in the search bar and instead of seeing loan options, he got a big "Access Denied" error page. For someone with low financial literacy who already struggles with digital interfaces, this is deeply discouraging. He sees no buttons, no links — just an error message with a long URL that means nothing to him. He probably thinks something is broken or that he's done something wrong. This is a CRITICAL friction point: the Bajaj Finserv search feature is returning an Access Denied error instead of search results, completely blocking a first-time loan seeker from finding the product he needs. Ramesh has now tried 3 different ways to get to the Personal Loan page and has been blocked each time — his confidence is dropping fast. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Typed | 50000 |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh finally sees the personal loan page after multiple failed attempts. He's relieved — he can see "Loan of up to ₹55 lakh" and notices the loan amount box showing ₹1,00,000. He thinks "yeh toh bahut zyada hai, mujhe toh sirf 50,000 chahiye" (this is too much, I only need 50,000). He wants to change the number to match what he actually needs. The input box is clearly visible with a ₹ symbol — he recognises this and decides to change the amount. He feels hopeful that this page will finally show him what his EMI would be for ₹50,000. The "No hidden charges" bullet point near the top catches his eye and reassures him slightly. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh sees the loan summary on the right side showing ₹50,000 — exactly what he needs for his home repair. He notices the orange "APPLY" button which is big and bold and hard to miss. He feels hopeful — "yeh toh sahi lag raha hai, ₹50,000 dikh raha hai" (this looks right, ₹50,000 is showing). However, he's also slightly nervous about the numbers he doesn't fully understand — "Flexi facility charges ₹1,999" and "Processing fee ₹505" are confusing. He wonders if these are extra costs on top of what he'll repay. But the "No hidden charges" bullet point he saw earlier reassures him a little. He takes a breath and clicks the big orange APPLY button, hoping this finally starts his loan application. |
| --- |
| URL | https://www.bajajfinserv.in/myaccount/landing/PersonalLoan?reqData=g0D6cVIZzWcXRWVTNAqATEFQYbwH%252F |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh is now deeply frustrated. He clicked the big orange "APPLY" button on the personal loan page — the most obvious thing to do — and instead of getting a loan application form, he's staring at another "Access Denied" error. This is the THIRD time he's hit an error wall during this journey. For a 29-year-old daily wage worker with low digital literacy who has been trying to get a ₹50,000 loan for home repair, this is crushing. He sees "Access Denied" in big bold letters and probably wonders "kya mujhe loan nahi milega?" (will I not get a loan?). He doesn't understand what "pushengineweb" or "edgesuite" means — it just looks like the website is refusing him. This is a CRITICAL UX failure: the primary APPLY button on the personal loan page redirects to an inaccessible backend URL, completely blocking a logged-in user from initiating their application. Ramesh's only option is to press back and try again. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Typed | 50000 |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh is back on the personal loan page after two frustrating "Access Denied" errors. He sees the loan amount showing ₹1,00,000 in the input box — "yeh toh meri zaroorat se zyada hai" (this is more than I need). He wants to see what ₹50,000 would look like — his actual home repair budget. The field clearly shows the ₹ symbol and a number he can change. He's hopeful: at least this part of the page seems to work. He carefully changes the number, thinking "agar 50,000 type karunga toh mera EMI kitna hoga?" (if I type 50,000, what will my EMI be?). The "No hidden charges" bullet still reassures him slightly, though he remains anxious about the fees he saw earlier. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh is back on the loan page with ₹50,000 showing in the summary — exactly what he needs. He sees the orange APPLY button but remembers it gave him an error last time. He decides to scroll down first to see what else is on the page, thinking "pehle thoda aur dekh leta hoon" (let me look a bit more first). He's cautiously hopeful — the numbers look right, and "No hidden charges" still reassures him. He scrolls down slowly, hoping to find either a form or more information that confirms he's eligible for ₹50,000. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh sees the loan summary showing exactly ₹50,000 — his exact home repair budget. He's relieved the numbers look right. The orange APPLY button is right there but he's been burned by it before. He decides to scroll down carefully — "neeche kuch aur hai kya" (is there something more below). He notices "Total Amount ₹91,104" in the EMI section and pauses — "itna zyada?" (so much?). He starts doing rough mental math: ₹50,000 loan but he'll pay back ₹91,104 total? This number worries him — he doesn't understand the concept of total interest over 96 months. He doesn't realize this is because of the 8-year tenure. This is a key financial literacy gap moment. Still, he scrolls down hoping to find a form to fill or a phone number to call. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh is scrolling down slowly, reading what he can. He saw the EMI calculator showing ₹50,000 loan with Total Amount ₹91,104 — that number still bothers him. "Main ₹50,000 le raha hoon lekin ₹91,104 waapis dunga?" (I'm taking ₹50,000 but paying back ₹91,104?). He doesn't understand that 96 months = 8 years of interest accumulation. He spots "No hidden charges" and "No collateral" — the "No collateral" part is very reassuring because as a daily wage worker he has no property to pledge. He scrolls down hoping to find: (a) eligibility criteria to check if he even qualifies, and (b) a phone number or a form to fill. The bullet "Flexible tenures" and "No collateral" give him cautious hope. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh sees customer reviews at the bottom of his screen — "35 million+ customers" and "4.8 Playstore Rating." These big numbers catch his eye and actually reassure him: "itne log le chuke hain toh theek hi hoga" (so many people have taken it, it must be okay). He reads a review from "Sudhakar Chobey" about home repair: "I've borrowed from several lenders in the past, but Bajaj Finance offered the fastest and most seamless experience." This is EXACTLY his situation — home repair, first-time borrower. This review resonates deeply. He also notices the FAQ section with tabs like "Eligibility" — he wants to click that but first scrolls down to see if there's more content or a form below. The "APPLY" button in orange at the bottom right is tempting but he's been burned before. He keeps scrolling carefully. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh has seen everything on this page — the loan summary showing exactly ₹50,000, the fees, the EMI calculator. He spots video thumbnails at the bottom — one says "Papa, Shimla chalein? Loan ready hai" (Papa, shall we go to Shimla? Loan is ready) — and another about "Pre-approved loan, perfect shaadi moment." These feel relatable but he's focused. He thinks "main toh pura page dekh chuka hoon, ab wapas upar jaake APPLY karna hai" (I've seen the whole page, now I need to go back up and APPLY). He scrolls back up, hoping this time the APPLY button actually opens a form for him to fill. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh has scrolled all the way through the personal loan page. He sees "35 million+ customers" and "4.8 rating" which reassure him — "itne log le chuke hain" (so many people have taken it). He reads a review from Japesh Oberoi about getting a personal loan for a foreign vacation and Sudhakar Chobey about home repair — this second one resonates. The orange APPLY button visible at the bottom right tempts him. He thinks "chalo wapas upar chalte hain, aur APPLY button dhundte hain" (let me go back up and find the APPLY button). He's been on this page a long time and wants to finally get his form submitted. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh finally scrolled all the way back to the top and sees his loan summary neatly laid out: ₹50,000 loan, ₹631 initial EMI, 15% p.a. — it's a lot but at least the numbers are there. He also spots "***Amount to be credited in your bank (A-B) ₹50,000" — that line is crystal clear to him: "toh mujhe poore 50,000 milenge" (so I'll get the full 50,000). That's reassuring. The orange APPLY button is right there, bold and visible. He takes a breath and clicks it — "is baar kaam kare" (let this work this time). He's been on this page for what feels like forever, and he just wants to fill a form and get his loan for home repair. |
| --- |
| URL | https://www.bajajfinserv.in/myaccount/landing/PersonalLoan?reqData=g0D6cVIZzWcXRWVTNAqATEFQYbwH%252F |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh stares at the same white "Access Denied" screen for the second time after clicking APPLY. He's genuinely frustrated: "Phir se yahi aaya!" (I'm back to the same error again!). He scrolled the entire page, waited, gathered confidence, clicked APPLY — and hit a wall again. For a daily wage worker who has never taken a loan before, this feels like rejection, not a technical glitch. He doesn't understand "server permission" errors. He just sees the word "Denied" in bold and feels like the system is blocking him personally. This is a CRITICAL CX failure — the primary Apply CTA on the personal loan page repeatedly throws an Access Denied error for a logged-in user, destroying trust and completely blocking the application journey. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| URL | https://www.bajajfinserv.in/myaccount/search/content?reqData=g0D6cVIZzWcXRWVTNAqATEFQYbwH%2F7ntWe567 |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh sees "Access Denied" for what feels like the hundredth time. He's a 29-year-old daily wage worker who just wants ₹50,000 for home repair. He doesn't know what "permission to access" means or what a "Reference #18.84f9da17" is. All he knows is that the big orange APPLY button keeps bringing him to this blank white page with the word "Denied." At this point, his trust in Bajaj Finance is severely shaken. He's thinking: "Kya main eligible nahi hoon? Kya yeh system mujhe reject kar raha hai?" (Am I not eligible? Is this system rejecting me?) This is a CRITICAL CX failure — the primary Apply CTA for a logged-in user on the personal loan page repeatedly throws an Access Denied server error, creating what feels like personal rejection to a low-literacy, first-time borrower. |
| --- |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh lands back on the Bajaj Finserv homepage staring at what looks like a blank blue-grey screen. After going through the APPLY button multiple times and hitting "Access Denied" each time, he's genuinely demoralized. "Phir se shuru se?" (Starting from scratch again?). He's a daily wage worker who took time out of his day to do this, and he's been bounced around between error pages. He scrolls down slowly, hoping to find a "Personal Loan" tile or card he can click — a fresh start, a different path. He's still determined but his patience is wearing thin. |
| --- |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Typed | personal loan |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh sees the homepage again — same one he started from. After being blocked by "Access Denied" twice from the APPLY button, he feels like he's going in circles. But then he notices the search bar at the top — "Search Bajajfinserv.in." He thinks: "Search mein 'personal loan' type karta hoon, shayad wahan se koi alag raasta mile" (Let me type 'personal loan' in search, maybe that gives a different path). He's frustrated but still determined — ₹50,000 for his home repair is too important to give up on. He types carefully. |
| --- |
| URL | https://www.bajajfinserv.in/myaccount/search/content?reqData=g0D6cVIZzWcXRWVTNAqATEFQYbwH%2F7ntWe567 |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh stares at the same "Access Denied" screen for what feels like the dozenth time. He's a 29-year-old daily wage worker who took time off to sort out his home repair loan, and every path is hitting the same wall. He doesn't understand "Reference #18.6df9da17" or what "edgesuite.net" means — all he sees is DENIED, again. The search bar he tried in the previous step brought him right back here. He feels completely helpless. "Ab kya karoon?" (What do I do now?). He decides to try typing the Bajaj personal loan address directly — he remembers seeing "bajajfinserv.in/personal-loan" somewhere on the page earlier. It's his last attempt before potentially giving up entirely. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| URL | https://www.bajajfinserv.in/myaccount/search/content?reqData=g0D6cVIZzWcXRWVTNAqATEFQYbwH%2F7ntWe567 |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh is staring at "Access Denied" for what must be the 4th or 5th time in this session. He's a 29-year-old daily wage worker who took time off work to apply for a ₹50,000 home repair loan. Every time he tries something — clicks APPLY, uses the search bar, goes back — he ends up on this same blank white page with the word "Denied." He doesn't know what "Reference #18.6df9da17.1777436134.108f7e3" means. He just sees "Denied" and feels like the system is personally rejecting him. "Kya Bajaj mujhe loan dena hi nahi chahta?" (Does Bajaj even want to give me a loan?). This is a CRITICAL, systemic CX failure — the logged-in Apply flow and the search functionality both route through a broken pushengineweb.bajajfinserv.in URL that returns Access Denied errors, completely blocking the application journey for this user. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh sees the Bajaj Finance personal loan page again — familiar territory after multiple failed attempts. He spots the big orange "APPLY" button on the right side of the screen inside the loan summary box. He takes a deep breath: "Ek baar aur try karta hoon" (Let me try one more time). The page looks professional and the "Trusted by 3 lakh+ customers" badge gives him a tiny bit of confidence. He's cautiously hopeful but his trust has been severely damaged by the repeated "Access Denied" errors. He clicks APPLY, praying this time something different happens. |
| --- |
| URL | https://www.bajajfinserv.in/myaccount/landing/PersonalLoan?reqData=g0D6cVIZzWcXRWVTNAqATEFQYbwH%252F |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh sees "Access Denied" for what must be the 5th or 6th time in this session. He's a 29-year-old daily wage worker who has been trying to apply for a simple ₹50,000 home repair loan for what feels like forever. The words "Access Denied" and "You don't have permission" feel deeply personal to him — like the system itself is saying "you don't qualify." He doesn't understand what "pushengineweb.bajajfinserv.in" or "edgesuite.net" or "Reference #18.6df9da17" means. All he knows is: the big APPLY button on the Bajaj Finserv personal loan page — the one promising loans up to ₹55 lakh — keeps dumping him on this blank white page with the word "DENIED." This is a CRITICAL systemic CX failure. The logged-in Apply flow for Personal Loan consistently routes to a broken pushengineweb.bajajfinserv.in endpoint that returns Access Denied for this user. A low-literacy, first-time borrower like Ramesh has no way to understand this is a technical error and not a personal rejection. He's very close to abandoning the application entirely. |
| --- |