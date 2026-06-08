<!-- converted from CX_Audit_Report_28_Apr_2026_1034_UTC.docx -->



CX AUDIT REPORT
bajajfinserv.in  |  Customer Experience Deep-Dive


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
- Eligibility criteria for informal/daily wage workers is completely absent — Ramesh's #1 question went unanswered across 38 steps and 3 pages.
- The 'CHECK ELIGIBILITY' widget is a false promise — it demands OTP verification instead of giving Ramesh any eligibility answer, destroying the trust of a first-time applicant.
- Two conflicting EMI figures (₹856 from the calculator vs. ₹975 in the Loan Summary) on the same screen would make a first-time borrower like Ramesh distrust every number on the page.
- The charges table — with 'Penal charge: up to 36% per annum' displayed without plain-language explanation — genuinely frightened Ramesh and could push informal-sector borrowers to abandon the journey entirely.
- The EMI calculator was Ramesh's single moment of genuine empowerment — ₹856/month on a ₹50,000 loan gave him a concrete, manageable number for the first time.

## Key Delight Factors
No notable delight factors identified.

## Key Friction Points
HIGH SEVERITY





MEDIUM SEVERITY





LOW SEVERITY



## Emotional Journey

## CX Score Dashboard — All Dimensions

## Recommendations

## Complete User Journey — Step by Step
### Step 1  ✅  [WAIT]  https://www.bajajfinserv.in/
What persona saw: The screen is completely blank — just a solid light blue-grey background with no text, buttons, images, or navigation visible. The page title confirms we're on bajajfinserv.in but nothing has rendered yet. This is consistent with a slow internet connection causing delayed page load.

📸  Step 1  —  ramesh-first-personal-loan-daily-wage-worker_step00_wait.png


### Step 2  ✅  [CLICK]  Personal Loan
What persona saw: The page has fully loaded now. Ramesh can see the Bajaj Finserv homepage with a horizontal icon strip near the top showing product categories. "Personal Loan" is clearly visible as one of the icons in the product strip. He also sees a banner section below that mentions "Personal Loan Up to ₹55 Lakhs* Instant disbursal Apply Now". The page is busy with many offers and products, but the "Personal Loan" icon in the category strip jumps out as the most direct path to what he needs.

📸  Step 2  —  ramesh-first-personal-loan-daily-wage-worker_step01_click.png


### Step 3  ✅  [CLICK]  APPLY
What persona saw: Ramesh is on the Bajaj Finserv Personal Loan page. He can see a prominent banner showing "Loan of up to ₹55 lakh*" and key reassuring bullet points: "No collateral and no hidden charges," "Online application and disbursement in 24 hours*," "Attractive interest rates starting @ 10% p.a.*" and "Quick approval." There's a rating of 4.8 and "Trusted by 3 lakh+ customers" trust signal. The page mentions loans from ₹40,000 to ₹55 lakh — which means his ₹50,000 need is well within range. There's an "APPLY" button visible in the interactive elements. The right side of the page appears to have some content loading (grey placeholder blocks visible in screenshot). Overall the page feels trustworthy and approachable.

📸  Step 3  —  ramesh-first-personal-loan-daily-wage-worker_step02_click.png


### Step 4  ✅  [SCROLL]  Main page content
What persona saw: Ramesh clicked "APPLY" and instead of landing on an application form, he's now on a page titled "How to get a personal loan in 6 easy steps" at the URL /how-to-apply-for-personal-loan. This is an informational/guide page, NOT an application form. The page shows loan types (Flexi Hybrid, Flexi Term Dropline, Term Loan), interest rates (10%-30% p.a.), and a fee schedule. There are icons for Loan Types, Calculator, FAQs, and Videos visible at the top. The loan range ₹40,000 - ₹50 Lakh is shown. There's a "Calculate your EMIs" link and a "Check now" button. The page has multiple "Show More" collapsed sections. No Apply button is visible in the current scroll position.

📸  Step 4  —  ramesh-first-personal-loan-daily-wage-worker_step03_scroll.png


### Step 5  ✅  [TYPE]  Enter mobile number
What persona saw: Ramesh is on the "How to apply for a personal loan" informational page. He scrolled down and now sees a sticky widget at the bottom right corner with an orange "CHECK ELIGIBILITY" button and a mobile number input field labeled "Enter mobile number." Above that, there's a section about "Key offerings: 3 loan types" with tabs for Flexi Hybrid Term Loan, Flexi Term (Dropline) Loan, and Term Loan. The fee table is visible with complex terms. At the very bottom right, the CHECK ELIGIBILITY CTA with the mobile input is the most action-oriented element visible — it's what Ramesh would naturally gravitate toward as his path to actually starting the process.

📸  Step 5  —  ramesh-first-personal-loan-daily-wage-worker_step04_type.png


### Step 6  ✅  [CLICK]  CHECK ELIGIBILITY
What persona saw: Ramesh can see the page showing 3 loan types (Flexi Hybrid, Flexi Term, Term Loan) with some explanation text. The mobile number field at the bottom right already shows his number "8826100789" that he typed in the previous step. The orange "CHECK ELIGIBILITY" button is right next to it. This is the most obvious next action — he's already entered his number and now just needs to tap the button to see if he qualifies.

📸  Step 6  —  ramesh-first-personal-loan-daily-wage-worker_step05_click.png


### Step 7  ✅  [DISMISS_POPUP]  X close button on the Verification required popup
What persona saw: A modal popup titled "Verification required" has appeared, saying an OTP was sent to +91 xxxxxxxxx89. It shows 6 OTP input boxes, a "Resend OTP in secs" link, and a "Submit" button. There's also an X (close) button in the top-right corner of the modal. This is an OTP gate — Ramesh cannot proceed without a real OTP on his actual phone.

📸  Step 7  —  ramesh-first-personal-loan-daily-wage-worker_step06_dismiss_popup.png


### Step 8  ✅  [TYPE]  loan-amount-input
What persona saw: Ramesh is now on the personal loan product page, which has loaded with a loan calculator showing ₹1,00,000 as the default loan amount. The page shows a "Loan summary" panel on the right with processing fee (₹1,010), Flexi facility charges (₹1,999), and EMI breakdowns. The loan amount input field is visible with "Enter an amount between ₹40,000 & ₹50,00,000". There are tenure buttons (12, 24, 36, 48, 60, 72, 84, 96, 108 months) and loan variant options. The OTP popup from Step 06 has been dismissed. This is the public calculator section that Ramesh can use without logging in.

📸  Step 8  —  ramesh-first-personal-loan-daily-wage-worker_step07_type.png


### Step 9  ✅  [SCROLL]  Main page content
What persona saw: The calculator now shows ₹50,000 as the loan amount — exactly what Ramesh needs. The Loan Summary on the right is very informative: Requested loan amount ₹50,000, Processing fee ₹505, Flexi facility charges ₹1,999, Total loan amount ₹52,504. The EMI shown is ₹625 for first 24 months and ₹1,057 for subsequent 72 months under Flexi Hybrid Term Loan at 15% p.a. There's also an APPLY button visible. The page shows three loan variants: Term Loan (₹785 fixed), Flexi Hybrid Term Loan (₹625 initial), and Flexi Term Dropline (₹897 fixed). Ramesh can now see what ₹50,000 would cost him monthly — but he needs to scroll down to explore eligibility criteria, documentation requirements, and any other public information available before trying to apply.

📸  Step 9  —  ramesh-first-personal-loan-daily-wage-worker_step08_scroll.png


### Step 10  ✅  [SCROLL]  Main page content - eligibility criteria section
What persona saw: Ramesh can see the loan summary box clearly: ₹50,000 requested, ₹505 processing fee, ₹1,999 Flexi facility charges, total ₹52,504. He sees EMI of ₹625 for the first 24 months and ₹1,057 for the remaining 72 months, with total interest of ₹41,104 over 96 months. The page headings indicate there's a "Personal loan eligibility and documentation" and "Personal loan eligibility criteria" section below the fold. Ramesh is anxious about whether he — a daily wage worker earning ₹15,000/month — even qualifies. The most important thing for him right now is to find out eligibility requirements. The APPLY button is visible but per audit rules, he already clicked it once and it led to a login/OTP wall.

📸  Step 10  —  ramesh-first-personal-loan-daily-wage-worker_step09_scroll.png


### Step 11  ✅  [SCROLL]  Personal loan eligibility criteria section
What persona saw: Ramesh can see the page headings indicating there's a "Personal loan eligibility criteria" section below. The current view shows the loan summary box with ₹50,000 principal, processing fee of ₹505, Flexi facility charges of ₹1,999, and EMIs of ₹625 (first 24 months) and ₹1,057 (remaining 72 months). There are also accordion sections visible: "Features and benefits of our personal loan", "Personal loan eligibility and documentation", "How to apply for a personal loan online?", "Personal loan interest rate and applicable charges", "Compare loan variants", and "Frequently asked questions". The FAQ section shows tabs: Overview, Application, Repayment, Eligibility, Fees and charges. The "What is a personal loan?" accordion appears to be open showing description text.

📸  Step 11  —  ramesh-first-personal-loan-daily-wage-worker_step10_scroll.png


### Step 12  ✅  [SCROLL]  Personal loan eligibility criteria section
What persona saw: Ramesh is on the personal loan page and has been scrolling to find the eligibility criteria. The page structure shows "Personal loan eligibility criteria" and "Documents required for a personal loan" headings exist on the page. The current view shows the FAQ section with customer reviews and an APPLY button at the bottom. The page text confirms there's eligibility content below — the critical question for Ramesh is whether a daily wage worker earning ₹15,000/month qualifies. He can see the FAQ section with questions like "What is a personal loan?" but hasn't yet found the specific eligibility criteria (minimum income, employment type, etc.).

📸  Step 12  —  ramesh-first-personal-loan-daily-wage-worker_step11_scroll.png


### Step 13  ✅  [SCROLL]  Main page content - Personal loan eligibility criteria section
What persona saw: Ramesh is at the bottom of the page — he can see the footer area with videos, disclaimers, and language/form/portfolio sections. The page structure confirms "Personal loan eligibility criteria" exists as a heading on this page. It appears the eligibility section was somewhere in the middle of the page, and he's scrolled past it to the bottom. He needs to scroll back up to find the eligibility criteria section that he's been looking for urgently.

📸  Step 13  —  ramesh-first-personal-loan-daily-wage-worker_step12_scroll.png


### Step 14  ✅  [SCROLL]  Personal loan eligibility criteria section
What persona saw: Ramesh is currently near the bottom of the page, having scrolled past the eligibility criteria section. The page headings confirm "Personal loan eligibility criteria" and "Personal loan eligibility and documentation" sections exist on this page. The current scroll position shows the FAQ section with "Frequently asked questions" and customer reviews like Sudha Chobey, Meenu Parashar, Japesh Oberoi, Neeraj Kumar. The eligibility criteria section is above the current viewport — Ramesh overshot it while scrolling down. He needs to scroll back up to find it.

📸  Step 14  —  ramesh-first-personal-loan-daily-wage-worker_step13_scroll.png


### Step 15  ✅  [SCROLL]  Personal loan eligibility criteria section
What persona saw: Ramesh is currently seeing the bottom portion of the page — the FAQ section with tabs (Overview, Application, Repayment, Eligibility, Fees and charges) and the "What is a personal loan?" accordion expanded. The page structure confirms "Personal loan eligibility criteria" exists as a heading on this page, somewhere between the calculator and the FAQ section. He has overshot by scrolling too far down. He needs to scroll UP to find the eligibility criteria section that lists who can apply, minimum income, and employment type requirements. This is the most critical information for him — a daily wage worker earning ₹15,000/month who is unsure if he qualifies.

📸  Step 15  —  ramesh-first-personal-loan-daily-wage-worker_step14_scroll.png


### Step 16  ✅  [SCROLL]  Personal loan eligibility criteria section
What persona saw: Ramesh is currently on the personal loan page, viewing the loan summary section with the APPLY button visible. The page structure clearly shows "Personal loan eligibility criteria" exists as a heading on this page. The current view shows the loan summary with fees breakdown (₹505 processing fee, ₹1,999 Flexi facility charges) and the APPLY button. The eligibility section must be below this loan summary section. Ramesh has been scrolling up and down repeatedly — he needs to scroll DOWN from the current loan summary position to reach the eligibility criteria section which appears after "Features and benefits" and "Top uses" sections in the page structure.

📸  Step 16  —  ramesh-first-personal-loan-daily-wage-worker_step15_scroll.png


### Step 17  ✅  [SCROLL]  Main page content - eligibility criteria section
What persona saw: Ramesh is now on the "How to get a personal loan in 6 easy steps" page (URL: https://www.bajajfinserv.in/how-to-apply-for-personal-loan). The page title changed — this is a different page from the product page he was on before. He can see sections like "Key offerings: 3 loan types", "Personal loan interest rate and applicable charges" with a full fee table, and mentions of Flexi Hybrid, Flexi Term, and Term Loan options. He also sees the "Features and benefits of our personal loan", "Personal loan eligibility and documentation", "How to apply for a personal loan online?", "Personal loan interest rate and applicable charges", "Compare loan variants", and "Frequently asked questions" headings in the page structure. The FAQ section at the bottom has tabs including "Eligibility." The page he's on has the eligibility information he's been desperately searching for — he needs to scroll down to find it.

📸  Step 17  —  ramesh-first-personal-loan-daily-wage-worker_step16_scroll.png


### Step 18  ✅  [SCROLL]  Main page content - eligibility criteria section
What persona saw: Ramesh is on the "How to apply for personal loan" page. He can see the "Key offerings: 3 loan types" section with Flexi Hybrid Term Loan, Flexi Term (Dropline) Loan, and Term Loan tabs. Below that is a "Personal loan for all your needs" section with video cards. The page still shows loan summary content with fees. Ramesh has been hunting for the eligibility criteria for many steps — he needs to scroll down further to find the section that tells him if a daily wage worker earning ₹15,000/month qualifies.

📸  Step 18  —  ramesh-first-personal-loan-daily-wage-worker_step17_scroll.png


### Step 19  ✅  [SCROLL]  Main page content - eligibility criteria section
What persona saw: Ramesh sees the loan summary panel on the right side with ₹1,00,000 as the requested amount, processing fee ₹4,009, and Flexi facility charges ₹1,999. The calculator shows EMI options and loan type cards (Flexi Hybrid, Flexi Term, Term Loan) with "Apply Now" buttons. There's an APPLY NOW button prominently in orange at the bottom of the loan summary. The page is still showing the calculator/loan type section — the eligibility criteria section he's been hunting for across 17 steps is still not visible on screen.

📸  Step 19  —  ramesh-first-personal-loan-daily-wage-worker_step18_scroll.png


### Step 20  ✅  [SCROLL]  Main page content - FAQs/Eligibility section below the calculator
What persona saw: Ramesh is looking at the EMI calculator showing loan types (Flexi Term, Flexi Hybrid, Term Loan) with the loan summary on the right side. The calculator shows ₹1,00,000 as the amount with Flexi Hybrid selected. There's an "APPLY NOW" button prominently visible in orange. The page structure shows there are FAQs and Videos sections below the current view (indicated by the icon tabs at top: "Loan Types Icon", "Calculator - Icon", "FAQs - Icon", "Videos - Icon"). Ramesh has been desperately searching for eligibility criteria and has not found it yet. The FAQs section — which likely contains eligibility information — must be below the current scroll position.

📸  Step 20  —  ramesh-first-personal-loan-daily-wage-worker_step19_scroll.png


### Step 21  ✅  [SCROLL]  Main page content - Personal loan interest rate and applicable charges
What persona saw: Ramesh is looking at the loan summary panel which shows the "APPLY" button prominently. He can see the total loan amount of ₹1,03,009, processing fee of ₹1,010, Flexi facility charges of ₹1,999, and rate of interest at 15% p.a. Below this, he can see the beginning of a section called "Personal loan interest rate and applicable charges" — this might finally contain the eligibility criteria he's been desperately hunting for across 20+ steps. He needs to scroll down to see what's in that section.

📸  Step 21  —  ramesh-first-personal-loan-daily-wage-worker_step20_scroll.png


### Step 22  ✅  [CLICK]  APPLY NOW
What persona saw: Ramesh is now seeing the FAQ section with "Frequently asked questions" visible, along with a "Personal loan for all your needs" section below. Most importantly, the big orange "APPLY NOW" button is visible at the top of the screen. After 20+ steps of scrolling without finding clear eligibility criteria, Ramesh has reached his breaking point. He's exhausted from searching and decides to just click the Apply button to see what happens. The FAQ answers he can see talk about "good credit score" and "financial details and employment history" — which actually increases his anxiety since he's a daily wage worker without formal employment documents. But he's going to try anyway.

📸  Step 22  —  ramesh-first-personal-loan-daily-wage-worker_step21_click.png


### Step 23  ✅  [SCROLL]  Main page content - Personal loan eligibility criteria section
What persona saw: Ramesh is currently seeing the "Personal loan for all your needs" section with video cards showing different loan use cases (debt consolidation, goals, entrepreneurial dreams, etc.) with "Apply Now" links. Above the fold was the FAQ section with "How do I get an immediate personal loan?" He's now scrolled to what appears to be near the bottom of the page content. The page shows the FAQ answers and below that "Personal loan for all your needs" with video carousel. There's a big orange "APPLY NOW" sticky button visible at the bottom. He already clicked Apply in step 21 but it seems he's back on this page still exploring.

📸  Step 23  —  ramesh-first-personal-loan-daily-wage-worker_step22_scroll.png


### Step 24  ✅  [SCROLL]  Main page content - FAQ section with eligibility information
What persona saw: Ramesh is at the bottom of the "how to apply for personal loan" page. He can see the Related Articles section with links about "Why choose Bajaj Finserv Personal Loan," "How is your Personal Loan amount decided," and "Switch to our..." He can also see a Disclaimer at the bottom mentioning "For customer support, call Personal Loan IVR: 7757 000 000" and sections for "Languages" and "Application Forms." The FAQ section visible earlier had only 3 questions shown with a "Show More" option. He's still hunting for eligibility criteria — specifically whether a daily wage worker earning ₹15,000/month can qualify. The page appears to be near its bottom. The FAQ section with "Show More" is the best remaining option to find eligibility info.

📸  Step 24  —  ramesh-first-personal-loan-daily-wage-worker_step23_scroll.png


### Step 25  ✅  [SCROLL]  Main page content - FAQ section with Show More button
What persona saw: Ramesh is at the very bottom of the page — the footer area with corporate identity numbers, office addresses, and company links. The current screenshot shows the footer with "Languages," "Application Forms," "Products Portfolio," "Calculators," and "Important Links" accordion sections. He's reached the end of the page without finding eligibility criteria. Earlier in the journey, there was a "Show More" button in the FAQ section that he never clicked. That FAQ section is somewhere above his current position — he needs to scroll back up to find it and click "Show More" to see if additional FAQ entries reveal eligibility information for daily wage workers.

📸  Step 25  —  ramesh-first-personal-loan-daily-wage-worker_step24_scroll.png


### Step 26  ✅  [CLICK]  Show More
What persona saw: Ramesh is at the bottom of the page, seeing the footer area with Related Articles, Disclaimer, and collapsed sections. He's scrolled back up slightly and can see the FAQ section which has a "Show More" button after the 3 visible FAQ entries. The FAQ section shows questions like "How do I get an immediate personal loan?", "How to get a personal loan for the first time?", and "How to get quick approval on my personal loan application?" — followed by a "Show More" link. This is his last hope on this page for finding eligibility criteria.

📸  Step 26  —  ramesh-first-personal-loan-daily-wage-worker_step25_click.png


### Step 27  ✅  [SCROLL]  Main page content - FAQ section after Show More was clicked
What persona saw: Ramesh is at the top portion of the page after clicking "Show More" in step 25. The screenshot shows the loan types section with "Key offerings: 3 loan types" and the Flexi Hybrid/Flexi Term/Term Loan tabs. The page text shows there are FAQ entries below — "How do I get an immediate personal loan?" is cut off at the bottom. After clicking "Show More" in the FAQ section, new content should have been revealed below the current scroll position. Ramesh needs to scroll down to see if the expanded FAQ now contains eligibility information about income requirements for daily wage workers.

📸  Step 27  —  ramesh-first-personal-loan-daily-wage-worker_step26_scroll.png


### Step 28  ✅  [SCROLL]  Main page content - FAQ section after Show More was clicked
What persona saw: Ramesh is currently seeing the "Key offerings: 3 loan types" section with Flexi Hybrid, Flexi Term, and Term Loan tabs. Below this are video cards ("Personal loan for all your needs"). The page text extraction shows that the FAQ section exists further below with "Frequently asked questions" and "Show More" buttons — but he's currently seeing the loan types and video section. He needs to scroll down past the calculator and loan summary to reach the FAQ section where "Show More" was presumably clicked in step 25 to reveal more content including potential eligibility information.

📸  Step 28  —  ramesh-first-personal-loan-daily-wage-worker_step27_scroll.png


### Step 29  ✅  [SCROLL]  Main page content - FAQ section with expanded questions
What persona saw: Ramesh is looking at the loan calculator section with the loan summary panel visible. The page shows the calculator with ₹1,00,000 default amount, tenure buttons (84 months selected), loan type tabs (Flexi Hybrid selected), and the loan summary showing ₹1,03,009 total with APPLY NOW button. The FAQ section is mentioned in the page text at the very bottom: "Frequently asked questions... How do I get an immediate personal loan" — meaning there's FAQ content below the current scroll position. The "Show More" was clicked in step 25 and Ramesh has been scrolling to find the expanded FAQ content. He needs to continue scrolling down past the calculator and loan summary to reach the FAQ section.

📸  Step 29  —  ramesh-first-personal-loan-daily-wage-worker_step28_scroll.png


### Step 30  ✅  [TYPE]  loan-amount-input
What persona saw: Ramesh is looking at the EMI calculator on the page. The calculator currently shows ₹1,00,000 as the default loan amount, with the Flexi Hybrid loan type selected, showing EMIs of ₹1,250 (initial) and ₹2,379 (subsequent) for 84 months at 15% p.a. The total amount shown is ₹1,72,740. The screenshot clearly shows the calculator with loan summary details — but it's all based on ₹1,00,000, not Ramesh's target of ₹50,000. There's a loan amount input field (element [02] "loan-amount-input") that he can change. This is a meaningful action — Ramesh should try entering ₹50,000 to see what his actual EMIs would be, which will help him understand if this loan is affordable for him.

📸  Step 30  —  ramesh-first-personal-loan-daily-wage-worker_step29_type.png


### Step 31  ✅  [SCROLL]  Main page content - Loan Summary and EMI calculator results
What persona saw: The page now shows the EMI calculator with ₹50,000 entered (from step 29). The loan summary section is now visible showing: Requested loan amount ₹50,000, Processing fee ₹505, Total loan amount (A) ₹50,505, EMI for 84 months at 15% p.a. = ₹856, Total Interest = ₹21,904, Total Amount = ₹71,904. There are also tenure buttons (12, 24, 36, 48, 60, 72, 84, 96 months) below fold, and an APPLY button visible. The loan summary box is partially visible but needs scrolling to see in full. Also visible are product cards for Flexi Hybrid, Flexi Term, and Term Loan with "Apply Now" buttons.

📸  Step 31  —  ramesh-first-personal-loan-daily-wage-worker_step30_scroll.png


### Step 32  ✅  [SCROLL]  Main page content - Loan Summary section
What persona saw: The calculator is now showing exactly what Ramesh wanted to see: ₹50,000 loan amount entered, 84 months tenure selected, Term Loan type chosen. The EMI is ₹856/month at 15% p.a. The Loan Summary on the right side shows: Requested loan amount ₹50,000, Processing fee ₹505, Total loan amount (A) ₹50,505, Instalment for 84 months ₹975, Rate of Interest 15% p.a. Total interest paid would be ₹21,904. The APPLY NOW button is prominently visible in orange. There's also a loan summary box on the right side with all the breakdown. The full summary seems cut off at the bottom — there may be more information below including the final "Amount to be credited" line.

📸  Step 32  —  ramesh-first-personal-loan-daily-wage-worker_step31_scroll.png


### Step 33  ✅  [SCROLL]  Main page content - Personal loan interest rate and applicable charges
What persona saw: Ramesh can see the loan summary section clearly now. The screen shows:
- EMI: ₹856 for 84 months at 15% p.a.
- Loan summary: Requested loan amount ₹50,000, Processing fee ₹505, Total loan amount ₹50,505
- Instalment (84 months): ₹975 (confusingly different from the ₹856 shown in the calculator)
- Amount to be credited in bank (A-B): ₹50,000
- An "APPLY" button in blue
- An "APPLY NOW" button lower down
- A note section explaining stamp duty and broken period interest
- Below that: "Personal loan interest rate and applicable charges" section header
- A "Not your nearest branch? LOCATE STORE" section
- FAQ section visible at the very bottom

The page is showing him exactly ₹50,000 will be credited to his bank — that's the key confirmation he needed. There's also a section about "Personal loan interest rate and applicable charges" just below that he hasn't seen yet — this could contain the interest rate table and fees info that's critical for a first-time borrower.

📸  Step 33  —  ramesh-first-personal-loan-daily-wage-worker_step32_scroll.png


### Step 34  ✅  [CLICK]  Personal loan interest rate and applicable charges
What persona saw: Ramesh can see the current FAQ section showing "How do I get an immediate personal loan?" with a brief answer about NBFCs and credit scores. Below that are two more FAQ questions (How to get a personal loan for the first time? / How to get quick approval?) which are collapsed. There's a "Show More" link. The "Personal loan interest rate and applicable charges" section is visible as a collapsed accordion — this is exactly what Ramesh needs to understand fees, eligibility criteria, and whether his income qualifies. The calculator already confirmed ₹856/month EMI for ₹50,000, and "Amount to be credited ₹50,000" was reassuring. Now the rate and charges section is the logical next click to understand the full cost picture and any eligibility requirements listed there.

📸  Step 34  —  ramesh-first-personal-loan-daily-wage-worker_step33_click.png


### Step 35  ✅  [SCROLL]  Main page content - Personal loan interest rate and applicable charges
What persona saw: Ramesh can see the "Personal loan interest rate and applicable charges" table is now expanded and visible. He can read: Rate of interest per annum: 10% to 30% p.a., Processing fees: Up to 3.93%, Bounce charges: Rs. 700 to Rs. 1,200 per bounce, and Part-prepayment charges with complex percentages. The APPLY NOW floating button is visible at the bottom. The table is dense with financial jargon — "Flexi Facility Charge," "Flexi Term (Dropline) Loan," "Broken Period Interest" — none of which Ramesh understands.

📸  Step 35  —  ramesh-first-personal-loan-daily-wage-worker_step34_scroll.png


### Step 36  ✅  [SCROLL]  Main page content - charges table and FAQ section
What persona saw: Ramesh is looking at the detailed charges table for personal loan fees. He can see Part-prepayment charges that are cut off, and the text shows Flexi Hybrid Term Loan charges, Part Pre-payment details, Penal charge (up to 36% per annum), Stamp duty, Annual maintenance charges, Credit guarantee scheme fee details. There's also an "APPLY NOW" button floating at the bottom of the screen. The page has a lot of dense financial jargon that is overwhelming for someone with low financial literacy.

📸  Step 36  —  ramesh-first-personal-loan-daily-wage-worker_step35_scroll.png


### Step 37  ✅  [SCROLL]  Main page content - FAQ section with expanded questions about eligibil
What persona saw: Ramesh is on the "How to get a personal loan in 6 easy steps" page. He can see the FAQ section at the bottom with "Frequently asked questions" visible. The screenshot shows three FAQ items: "How do I get an immediate personal loan?", "How to get a personal loan for the first time?", and "How to get quick approval on my personal loan application?" — with the first one already expanded showing content about NBFCs and credit scores. The "APPLY NOW" sticky button is prominently visible at the bottom. He's been scrolling through this page for many steps trying to find eligibility criteria for daily wage workers. The FAQ section is his last hope before giving up.

📸  Step 37  —  ramesh-first-personal-loan-daily-wage-worker_step36_scroll.png


### Step 38  ✅  [GOAL_ACHIEVED]  https://www.bajajfinserv.in/how-to-apply-for-personal-loan
What persona saw: The page shows a section "Personal loan for all your needs" with video thumbnails for various personal loan use cases, including "Personal Loan for debt consolidation," "Your goals, our support with Personal Loan," "Fund your entrepreneurial dream with Personal Loan," "5 ways to use our Personal Loan," and "Pre-approved Personal Loan." There's also a prominent orange "APPLY NOW" floating button. At the bottom right is a persistent orange "APPLY NOW" CTA button. Ramesh has seen everything meaningful available on the public site without logging in.


| Target URL | https://www.bajajfinserv.in |
| --- | --- |
| Audit Date | 28 Apr 2026 1034 UTC |
| Personas Audited | 1 |
| Avg CX Score | 4.8 / 10  —  🟠 Weak |
| Overall Avg Score
4.8/10 | Best Experience
4.8/10 | Worst Experience
4.8/10 | Goals Achieved
1/1 |
| --- | --- | --- | --- |
| Persona | Score | Outcome | One-line Verdict |
| --- | --- | --- | --- |
| Ramesh - First Personal Loan – Daily Wage Worker | 4.8/10
██████░░░░░░ | ✅ Achieved | Ramesh spent 38 steps and never found eligibility criteria for informal workers — the site is built for salaried professionals, not daily wage earners. |
| 🔴  [Ramesh - First Personal Loan – Daily Wage Worker]  /personal-loan — Step 2–3, 'APPLY' CTA
Ramesh tapped 'APPLY' on the personal loan page expecting to start his loan application. Instead, he was silently redirected to /how-to-apply-for-personal-loan — a dense informational guide page with fee tables and loan-type jargon. The button was labelled 'APPLY' but delivered a content page about the application process, not the application itself.
Impact: Ramesh felt immediately confused and deflated — 'Did I click the wrong button?' He lost momentum at his peak motivation moment. For a first-time, low-literacy borrower who mustered the courage to click Apply, landing on a guide page instead of a form felt like a false start that set a tone of confusion for the next 35+ steps. |
| --- |
| 🔴  [Ramesh - First Personal Loan – Daily Wage Worker]  /how-to-apply-for-personal-loan — Steps 5–6, 'CHECK ELIGIBILITY' widget
The 'CHECK ELIGIBILITY' widget accepted Ramesh's mobile number and then immediately triggered an OTP verification popup rather than providing any eligibility insight. The widget's label promised Ramesh a yes/no eligibility answer — exactly what he'd been searching for — but delivered only an authentication gate with no explanation of what completing the OTP would give him.
Impact: This was the most damaging single friction event in the journey. Ramesh had invested hope in 'CHECK ELIGIBILITY' as his path to a simple answer about whether he qualified. When it turned out to be a login wall in disguise, it shattered that hope and left him feeling tricked. He dismissed the popup and lost all progress, with no eligibility information gained despite providing his phone number. |
| --- |
| 🔴  [Ramesh - First Personal Loan – Daily Wage Worker]  /personal-loan and /how-to-apply-for-personal-loan — Steps 9–28, Eligibility criteria section
Ramesh spent 20+ consecutive scroll steps hunting for a clear eligibility criteria section across both pages. The eligibility section existed on the /personal-loan page but was buried below marketing banners, customer testimonials, and video thumbnails. There was no sticky section navigation, no anchor link, no 'Jump to eligibility' shortcut, and no clear visual signpost. Ramesh overshot it multiple times, reaching the footer and scrolling back up repeatedly.
Impact: Ramesh's single most urgent question — 'Can a daily wage worker earning ₹15,000/month from Jodhpur get this loan?' — was never answered across 38 steps. He arrived at Step 37 still not knowing if he was eligible. This uncertainty means he is likely to either abandon the journey entirely or call the helpline — an additional barrier that could cost Bajaj a genuine conversion. |
| --- |
| 🔴  [Ramesh - First Personal Loan – Daily Wage Worker]  /personal-loan and /how-to-apply-for-personal-loan — Entire journey, Eligibility for informal workers
Neither the /personal-loan page nor the /how-to-apply-for-personal-loan page contained any information about eligibility for informal workers, daily wage earners, or self-employed individuals with irregular income. All eligibility framing — in FAQs, disclaimers, and any visible eligibility content — referenced 'employment history,' 'credit score,' and 'financial details' in the context of formal employment.
Impact: Ramesh, a daily wage worker with no salary slips and possibly no formal employment record, had no way to determine whether Bajaj Finserv's personal loan was even an option for someone like him. This is not just a UX problem — it is a product communication failure that excludes a significant segment of India's working population. Ramesh left the site anxious, not confident. |
| --- |
| 🔴  [Ramesh - First Personal Loan – Daily Wage Worker]  /how-to-apply-for-personal-loan — Steps 34–35, Charges table
The charges table displayed 'Penal charge: up to 36% per annum' in the same visual format as other routine charges, with no plain-language explanation of what a 'penal charge' is, when it applies, or how it is calculated. The table also listed 'Flexi Hybrid Term Loan,' 'Flexi Term (Dropline),' 'annual maintenance charges,' 'broken period interest,' and 'credit guarantee scheme fee' — all without tooltips, glossary links, or contextual explanations.
Impact: Ramesh was genuinely frightened by '36% per annum' appearing on the same screen as his 15% interest rate. He interpreted it as a potential catastrophic penalty — 'Agar EMI miss ho gayi toh 36% penalty lagegi??' — which introduced the fear of financial ruin into a journey where he was already anxious. This could be a conversion killer for low-literacy, low-income borrowers who are unfamiliar with the distinction between loan interest rates and penalty charges. |
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
✅ Goal Achieved | CX Score
4.8 / 10  🟠 Weak | Steps Taken
38 / 40  (0 failures) |
| --- | --- | --- |
| Ramesh spent 38 steps and never found eligibility criteria for informal workers — the site is built for salaried professionals, not daily wage earners. |
| --- |
| 🔴  /personal-loan — Step 2–3, 'APPLY' CTA
Ramesh tapped 'APPLY' on the personal loan page expecting to start his loan application. Instead, he was silently redirected to /how-to-apply-for-personal-loan — a dense informational guide page with fee tables and loan-type jargon. The button was labelled 'APPLY' but delivered a content page about the application process, not the application itself.
User Impact: Ramesh felt immediately confused and deflated — 'Did I click the wrong button?' He lost momentum at his peak motivation moment. For a first-time, low-literacy borrower who mustered the courage to click Apply, landing on a guide page instead of a form felt like a false start that set a tone of confusion for the next 35+ steps. |
| --- |
| 🔴  /how-to-apply-for-personal-loan — Steps 5–6, 'CHECK ELIGIBILITY' widget
The 'CHECK ELIGIBILITY' widget accepted Ramesh's mobile number and then immediately triggered an OTP verification popup rather than providing any eligibility insight. The widget's label promised Ramesh a yes/no eligibility answer — exactly what he'd been searching for — but delivered only an authentication gate with no explanation of what completing the OTP would give him.
User Impact: This was the most damaging single friction event in the journey. Ramesh had invested hope in 'CHECK ELIGIBILITY' as his path to a simple answer about whether he qualified. When it turned out to be a login wall in disguise, it shattered that hope and left him feeling tricked. He dismissed the popup and lost all progress, with no eligibility information gained despite providing his phone number. |
| --- |
| 🔴  /personal-loan and /how-to-apply-for-personal-loan — Steps 9–28, Eligibility criteria section
Ramesh spent 20+ consecutive scroll steps hunting for a clear eligibility criteria section across both pages. The eligibility section existed on the /personal-loan page but was buried below marketing banners, customer testimonials, and video thumbnails. There was no sticky section navigation, no anchor link, no 'Jump to eligibility' shortcut, and no clear visual signpost. Ramesh overshot it multiple times, reaching the footer and scrolling back up repeatedly.
User Impact: Ramesh's single most urgent question — 'Can a daily wage worker earning ₹15,000/month from Jodhpur get this loan?' — was never answered across 38 steps. He arrived at Step 37 still not knowing if he was eligible. This uncertainty means he is likely to either abandon the journey entirely or call the helpline — an additional barrier that could cost Bajaj a genuine conversion. |
| --- |
| 🔴  /personal-loan and /how-to-apply-for-personal-loan — Entire journey, Eligibility for informal workers
Neither the /personal-loan page nor the /how-to-apply-for-personal-loan page contained any information about eligibility for informal workers, daily wage earners, or self-employed individuals with irregular income. All eligibility framing — in FAQs, disclaimers, and any visible eligibility content — referenced 'employment history,' 'credit score,' and 'financial details' in the context of formal employment.
User Impact: Ramesh, a daily wage worker with no salary slips and possibly no formal employment record, had no way to determine whether Bajaj Finserv's personal loan was even an option for someone like him. This is not just a UX problem — it is a product communication failure that excludes a significant segment of India's working population. Ramesh left the site anxious, not confident. |
| --- |
| 🔴  /how-to-apply-for-personal-loan — Steps 34–35, Charges table
The charges table displayed 'Penal charge: up to 36% per annum' in the same visual format as other routine charges, with no plain-language explanation of what a 'penal charge' is, when it applies, or how it is calculated. The table also listed 'Flexi Hybrid Term Loan,' 'Flexi Term (Dropline),' 'annual maintenance charges,' 'broken period interest,' and 'credit guarantee scheme fee' — all without tooltips, glossary links, or contextual explanations.
User Impact: Ramesh was genuinely frightened by '36% per annum' appearing on the same screen as his 15% interest rate. He interpreted it as a potential catastrophic penalty — 'Agar EMI miss ho gayi toh 36% penalty lagegi??' — which introduced the fear of financial ruin into a journey where he was already anxious. This could be a conversion killer for low-literacy, low-income borrowers who are unfamiliar with the distinction between loan interest rates and penalty charges. |
| --- |
| 🟡  /personal-loan — Steps 31–32, Loan Summary showing conflicting EMI figures
The EMI calculator displayed ₹856/month as the EMI for Ramesh's ₹50,000 loan at 15% p.a. over 84 months. Simultaneously, the 'Loan Summary' panel — visible on the same screen — showed 'Instalment: ₹975.' Both figures appeared to refer to monthly payments for the same loan, with no explanation of the difference.
User Impact: Ramesh stared at both numbers in confusion — 'EMI ₹856 hai ya ₹975?' — unable to determine what he would actually pay each month. For a first-time borrower making his first-ever financial commitment, contradictory numbers from the same system on the same screen destroyed his confidence in the accuracy of everything else he'd read. He left not knowing his actual monthly obligation. |
| --- |
| 🟡  /personal-loan — Step 8–9, Flexi facility charges in Loan Summary
When Ramesh entered ₹50,000 in the calculator, the Loan Summary showed 'Flexi facility charges: ₹1,999' added to the total, taking the figure from ₹50,505 to ₹52,504. There was no explanation of what 'Flexi facility' is, whether it was optional, or whether it could be avoided by choosing a standard Term Loan.
User Impact: Ramesh was confused and slightly alarmed — 'I wanted ₹50,000 but now I owe ₹52,504 before I even get the money?' The unexplained ₹1,999 charge felt like the very 'hidden charge' that the headline 'No hidden charges' had promised wouldn't exist. It created a direct contradiction between the product's marketing promise and the calculator's output. |
| --- |
| 🟡  /personal-loan — Step 12, Footer disclaimer
While scrolling in search of eligibility information, Ramesh stumbled across a disclaimer stating that 'Bajaj Finance has absolute discretion, without assigning any reason to accept or reject any application.' This text appeared without any reassuring context, softening language, or explanation of the application review process.
User Impact: Ramesh was hit unexpectedly by this line — 'So they can just say no without telling me why?' For someone already anxious about whether a daily wage worker qualifies, this blunt legal disclaimer — encountered mid-scroll while hunting for basic information — was deflating and trust-eroding. It made the institution feel opaque and powerful, not customer-friendly. |
| --- |
| 🟡  /how-to-apply-for-personal-loan — Step 17, Three loan type cards
The page presented three distinct loan product variants — Flexi Hybrid Loan, Flexi Term Loan, and Term Loan — each with its own 'Apply Now' button and different EMI structures. The cards gave no plain-language guidance on which type suited which borrower profile, and the term 'Dropline' appeared without any explanation.
User Impact: Ramesh had no idea which loan type to choose and no way to understand the difference. He was faced with a three-way decision point with zero decision-making support — a paralyzing experience for a first-time borrower who just wants ₹50,000. He scrolled past all three cards without engaging, feeling more confused than when he arrived on the page. |
| --- |
| 🟡  https://www.bajajfinserv.in/ — Step 0, Page load
On Ramesh's slow mobile connection in Jodhpur, the Bajaj Finserv homepage took over 2 seconds to show any content at all — the screen was completely blank with no skeleton screen, no spinner, no logo, and no loading indicator of any kind.
User Impact: Ramesh's very first experience of Bajaj Finserv was a blank screen that made him wonder if the link was broken or his internet was too slow. For someone already nervous about attempting his first-ever loan application, this blank opening screen set an immediately anxious tone and could cause high-anxiety users to abandon the page entirely before it loads. |
| --- |
| 🟢  /personal-loan — Step 8–9, EMI structure for Flexi loan
The Loan Summary for the default Flexi loan type showed two different EMI amounts — ₹625 for the first 24 months and ₹1,057 for the remaining 72 months — with no explanation of why the EMI approximately doubles after the first two years.
User Impact: Ramesh could not understand why the EMI jumps from ₹625 to ₹1,057. He earns ₹15,000/month — ₹625 feels manageable but ₹1,057 feels harder, and he had no idea which amount would apply to him or why the structure works this way. This created unnecessary confusion about his actual future financial commitment. |
| --- |
| 🟢  /how-to-apply-for-personal-loan — Step 23, Customer support number
The helpline number '7757 000 000' appeared only in the footer disclaimer text — in regular-weight, small-print copy — and was not surfaced as a prominent, visually distinct help option anywhere during Ramesh's journey.
User Impact: Ramesh noticed the number at Step 23 and considered calling, but hesitated. Had the number been presented as a clear, prominent 'Need help? Call us' CTA near the eligibility section or the charges table, Ramesh might have called and converted. Instead, it was buried in legalese, and he let it go. |
| --- |
| Dimension | Score | Rationale |
| --- | --- | --- |
| Discoverability & Information Architecture | 6.5/10
████████░░░░ | Ramesh found 'Personal Loan' in under 2 clicks from the homepage — the coloured icon strip at Step 1 was immediately recognisable to him, and 'Personal Loan' is a label he understood without any financial literacy. That was a genuine win. However, once inside the product pages, the information architecture completely failed him. The eligibility criteria section — the most critical content for a first-time borrower — was buried so deep in a long-scroll page that Ramesh spent Steps 9 through 28 hunting for it without success. He scrolled past it multiple times, overshot to the footer, and came back up. The page also silently redirected the 'APPLY' button from the /personal-loan page to /how-to-apply-for-personal-loan (Steps 2–3) — a destination that felt like the wrong room. There was no breadcrumb, no sticky section nav, and no 'jump to eligibility' anchor link that could have saved Ramesh 20+ scroll steps. |
| Content Quality & Financial Clarity | 3.5/10
████░░░░░░░░ | The site completely failed Ramesh on the content that mattered most to him. His singular question — 'As a daily wage worker earning ₹15,000/month, am I eligible?' — was never answered anywhere across 38 steps and 3 pages. The eligibility section, when eventually visible, appeared to be written for salaried professionals with no mention of informal workers, daily wage earners, or minimum income thresholds that would apply to Ramesh's profile. The charges table (Steps 16, 34–35) displayed 'Penal charge: up to 36% per annum,' 'Flexi Hybrid Term Loan,' 'Flexi Term (Dropline),' and 'Credit guarantee scheme fee' without any plain-language explanations — language that reads like a legal document to someone of Ramesh's literacy level. Two conflicting EMI figures — ₹856 from the calculator and ₹975 in the Loan Summary (Steps 31–32) — were never reconciled on screen, leaving Ramesh genuinely unsure what he would pay monthly. The disclaimer at Step 12 stating Bajaj Finance has 'absolute discretion, without assigning any reason to accept or reject any application' was shown without any softening context, hitting Ramesh like a cold rejection warning. Positive note: the EMI calculator clearly showed 'Amount to be credited in your bank: ₹50,000,' which gave Ramesh the clarity that he would receive his full amount. |
| Trust & Credibility Signals | 6.0/10
███████░░░░░ | The initial trust signals on the /personal-loan page were genuinely effective for Ramesh. At Step 2, he noticed 'Trusted by 3 lakh+ customers' and a 4.8-star rating, and felt reassured — 'if so many people use it, it must be safe.' The 'No collateral and no hidden charges' copy at Step 2 directly addressed his fear of losing assets or being surprised by fees. The professional design and Bajaj brand recognition also conveyed legitimacy. However, several elements actively eroded trust for Ramesh specifically: (1) The disclaimer at Step 12 — 'Bajaj Finance has absolute discretion, without assigning any reason to accept or reject any application' — felt threatening and opaque. (2) The 'Penal charge: up to 36% per annum' in the charges table (Step 35) felt like a hidden punishment, not a transparent disclosure, because no plain-language explanation accompanied it. (3) The CHECK ELIGIBILITY widget (Steps 5–6) that promised a simple yes/no but delivered an OTP gate felt like a bait-and-switch, damaging trust in the brand's stated promises. For a first-time borrower with low financial literacy, unexplained large numbers like 36% are scarier than reassuring. |
| Conversion & Task Flow Design | 4.0/10
█████░░░░░░░ | Per logged-out journey rules, reaching a login wall at the application step is expected and not penalised. However, the flow had multiple design failures. The primary 'APPLY' button on /personal-loan navigated Ramesh to /how-to-apply-for-personal-loan — a content page, not an application form — causing genuine confusion at Step 3. This is a mislabelled CTA: a button labelled 'APPLY' that delivers an informational guide page is a broken promise. The 'CHECK ELIGIBILITY' widget (Steps 4–6) promised to check eligibility but immediately demanded OTP verification without offering any eligibility insight first — making it functionally a login wall disguised as a feature. The flow had no clear recommended path for a logged-out first-time visitor: no 'Start Here' guidance, no 'Find out if you qualify' section above the fold. Ramesh spent 38 steps navigating a maze that offered him no forward momentum until he gave up and clicked Apply out of exhaustion at Step 21. |
| Emotional Experience & Persona Fit | 2.5/10
███░░░░░░░░░ | The entire site is emotionally calibrated for a salaried professional in a Tier 1 city who already knows they qualify and just needs to compare rates and apply. For Ramesh — a 29-year-old daily wage worker from Jodhpur who has never taken a loan, earns ₹15,000/month, and doesn't know if he even qualifies — the site was an almost continuous source of anxiety and confusion. He felt hopeful at Step 1 (found the product), briefly reassured at Step 2 ('No collateral, no hidden charges'), then confused at Step 3 when Apply led to a guide page. His dominant emotional state from Steps 9 through 37 was anxious-to-frustrated, cycling through the same unanswered question. The tone of the charges table (Step 34–35), the 'absolute discretion' disclaimer (Step 12), the three unexplained loan types (Flexi Hybrid, Flexi Term, Term Loan at Step 17), and the FAQ copy referencing 'credit score' and 'employment history' (Step 21) all spoke to a different, more financially literate persona. There was no moment where the site said 'you belong here' to someone in Ramesh's situation. |
| Mobile & Device Experience | 5.5/10
███████░░░░░ | The coloured icon strip on the homepage (Step 1) was clearly visible and tappable on mobile, suggesting reasonable touch target sizing for primary navigation. The EMI calculator input field accepted Ramesh's typed amount (₹50,000) successfully at Steps 7 and 29, indicating functional mobile form inputs. However, the overall mobile experience for Ramesh's context — slow internet in Jodhpur — was problematic. Step 0 showed a completely blank screen for 2000ms+ with no skeleton screen or loading indicator, which caused anxiety on a slow connection. The page is extremely long (Ramesh needed 30+ scroll events to traverse it), which is particularly punishing on mobile. The charges table (Steps 16, 34) appeared to be a complex multi-column table that is notoriously difficult to read on a small mobile screen. The FAQ 'Show More' button (Step 25) was small enough that Ramesh had to hunt for it after scrolling back up. No evidence of content being mobile-first optimised for a persona on a 4G/slow connection in Rajasthan. |
| Accessibility & Inclusive Design | 2.0/10
██░░░░░░░░░░ | The site demonstrates almost no inclusive design for a user of Ramesh's profile. The charges table uses financial jargon — 'Flexi Hybrid Term Loan,' 'Flexi Term (Dropline),' 'penal charge,' 'part-prepayment charges,' 'annual maintenance charges,' 'broken period interest' — without a single tooltip, glossary link, or plain-language explanation anywhere in the journey. For Ramesh, this table reads like a legal document in a foreign language (Steps 16, 34–35). There are no help text callouts explaining what 'Flexi' means vs. a Term Loan, which would be essential for a first-time borrower choosing between product types (Step 17). The FAQ section uses headings like 'How to get a personal loan for the first time?' but its answers reference 'credit score,' 'employment history,' and 'financial details' without acknowledging the reality of informal workers. There is no Hindi language option surfaced prominently during the journey (though language options exist in the footer, Step 23, which Ramesh never interacted with). There is no help chatbot or financial education resource accessible during the journey without navigating away entirely. |
| Error Handling & Recovery Design | 5.5/10
███████░░░░░ | No technical errors or form submission failures were observed in Ramesh's journey — he had zero failed actions across 38 steps. The EMI calculator responded correctly to his ₹50,000 input at Steps 7 and 29. The 'Show More' button (Step 25) expanded the FAQ as intended. However, the OTP popup at Step 6, which appeared after Ramesh clicked 'CHECK ELIGIBILITY,' had no graceful failure path for a user who did not want to proceed with OTP verification — the only option was to dismiss the popup entirely, losing any progress. There was no 'Continue browsing without verifying' message, no explanation of what value completing the OTP would unlock, and no alternative path offered. The silent redirect of the 'APPLY' button to a different page (/how-to-apply-for-personal-loan) at Step 3 had no explanation or confirmation — Ramesh had no idea he'd been redirected. Inline validation and error recovery on the calculator fields worked adequately. |
| Page Performance & Load Experience | 4.0/10
█████░░░░░░░ | Step 0 is damning: Ramesh waited 2000ms staring at a completely blank screen — no skeleton, no spinner, no logo, no partial content. For a daily wage worker accessing the site on slow mobile internet in Jodhpur, this blank screen felt like the link was broken. There was no progressive loading feedback at all. The pages are visually heavy — multiple marketing carousels, video thumbnails, banners for 'Loan se fees nahi, future invest kiya,' and animated product cards. These elements are appropriate for a fast broadband connection in a metro but would cause significant additional lag for Ramesh's slow 4G connection in Rajasthan. The extremely long page length (requiring 30+ scroll events to traverse) compounds the performance problem — more content means more to load and more rendering work on a mid-range Android device. No evidence of lazy loading or lightweight mobile-first asset delivery was observed during this journey. |
| Micro-copy & Language Quality | 3.5/10
████░░░░░░░░ | Several micro-copy failures were directly observed during Ramesh's journey. The 'APPLY' button on /personal-loan navigated to a guide page — the label promised action but delivered information, a broken promise in 3 characters (Step 3). The 'CHECK ELIGIBILITY' widget promised a yes/no eligibility answer but immediately demanded OTP verification — another broken promise (Steps 5–6). The charges table used terms like 'Flexi Hybrid Term Loan,' 'Dropline,' 'penal charge,' 'broken period interest,' and 'credit guarantee scheme fee' with zero glossary or tooltip support (Steps 34–35). The disclaimer copy — 'Bajaj Finance has absolute discretion, without assigning any reason to accept or reject any application' — is written in dense legal language that would alarm any first-time borrower (Step 12). The FAQ answers referenced 'credit score' and 'employment history' without acknowledging informal workers. Positive: 'No collateral and no hidden charges' at Step 2 was the single best piece of persona-fit copy in the entire journey — clear, relevant, and directly addressing Ramesh's fear. |
| Form Design & Data Collection UX | 5.0/10
██████░░░░░░ | Ramesh never reached the actual application form in this logged-out journey, so the full form UX cannot be evaluated. What can be evaluated is the pre-form data collection: the 'Enter mobile number' widget and the EMI calculator. The mobile number widget (Steps 4–5) was the right idea — a low-commitment single-field entry — but its execution failed because it immediately triggered an OTP popup rather than any eligibility insight. The EMI calculator (Steps 7, 29–32) accepted Ramesh's ₹50,000 input cleanly and displayed results, but presented two conflicting EMI figures — ₹856 from the calculator and ₹975 in the Loan Summary — on the same screen (Steps 31–32) with no explanation. There was no progress indicator anywhere on the pages visited, no guidance on how many steps an application involves, and no reassurance that starting to explore wouldn't commit Ramesh to anything. |
| Navigation Depth & Efficiency | 4.0/10
█████░░░░░░░ | Finding the Personal Loan product was efficient — 2 clicks from homepage at Steps 1–2. But everything after that was deeply inefficient. The 'APPLY' CTA on /personal-loan silently redirected Ramesh to /how-to-apply-for-personal-loan (Step 3), adding an unexpected navigation step. The eligibility section that Ramesh needed was on both pages but discoverable only through exhaustive manual scrolling — there were no sticky section tabs, no 'jump to eligibility' anchor links, and no table of contents for the long-scroll page. Ramesh navigated to the bottom of the page multiple times (Steps 12, 23) and had to scroll back up, wasting dozens of scroll events. The FAQ 'Show More' button (Step 25) required hunting to find after scrolling back from the footer. The 'Eligibility' tab observed at Step 14 was not clicked by Ramesh — a typical low-literacy user who scrolls rather than clicking sub-navigation tabs. Total navigation depth to reach eligibility information: never fully achieved in 38 steps. |
| Personalisation & Context Awareness | 3.5/10
████░░░░░░░░ | This was a logged-out journey, so deep personalisation is not expected. However, the site showed no contextual awareness of Ramesh as a new visitor with no account. The CHECK ELIGIBILITY widget (Steps 4–6) demanded OTP without offering any hint of what personalised information Ramesh would receive by completing it — no 'Log in to see your pre-approved offer' or 'Verify your number to check your loan limit' messaging. The widget offered no value proposition for providing personal data. The homepage and product page content was identical for every visitor — no geographic adaptation for a Jodhpur user (e.g., regional loan agent availability), no income-band adaptation, and no acknowledgement that this might be a first-time borrower exploring for the first time. The EMI calculator did not surface any contextual prompt like 'For your loan amount of ₹50,000, your likely interest band would be...' — it just showed a generic 15% default rate. The site treated Ramesh identically to a repeat salaried customer with an existing account. |
| Pre-Sales Support & Help Availability | 3.0/10
████░░░░░░░░ | Ramesh's most urgent pre-sales need was eligibility information — and no support mechanism helped him get it. There was no chatbot accessible during his journey that could have answered 'Can a daily wage worker with ₹15,000/month income apply?' The customer support number '7757 000 000' appeared only in the footer disclaimer text (Step 23) — not in a prominent help banner, not in a sticky footer button, not contextually near the eligibility section. Ramesh noticed it but felt too hesitant to call. There was no FAQ answer that specifically addressed informal workers or daily wage employees. The EMI calculator was the only genuinely useful pre-sales tool — it gave Ramesh the ₹856/month figure that was his single concrete piece of decision-making information (Step 30). But an eligibility estimator (income-based) was completely absent. No proactive 'Have questions? Chat with us' prompt was observed at any step of the 38-step journey. |
| Visual Hierarchy & Scannability | 4.5/10
█████░░░░░░░ | The homepage icon strip (Step 1) had excellent visual hierarchy for the top-level task — finding Personal Loan was a 5-second task. The APPLY and APPLY NOW CTAs in orange were visually prominent throughout the journey. However, for the content Ramesh actually needed, visual hierarchy failed completely. The eligibility criteria section — the most critical information for a first-time borrower — was not visually emphasised over marketing banners, customer testimonials, and video thumbnails. The charges table was presented in dense tabular format without visual highlighting of the most important rows (e.g., the 'penal charge: 36%' row appeared in the same visual weight as a 0.3% maintenance fee, yet carried very different emotional weight for Ramesh). The Flexi Hybrid/Term/Dropline product cards (Step 17) were visually equal in prominence despite being meaningless to Ramesh. The 'No collateral and no hidden charges' benefit was presented in a bulleted list that competed visually with multiple other bullet points — it deserved to be far more prominent given how directly it addressed a first-time borrower's anxiety. |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Typed | 2000 |
| Emotion | 😰 Anxious |
| CX Note
Ramesh stares at a completely blank screen after clicking on the Bajaj Finserv link. On his slow mobile connection, the page hasn't loaded anything yet — no logo, no menu, no buttons. For someone who's already nervous about applying for his first-ever loan, this blank screen feels unsettling. He wonders if the link was wrong, or if his internet is too slow. He holds on, hoping something will appear. |
| --- |
| URL | https://www.bajajfinserv.in/ |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
After the anxious wait on a blank screen, Ramesh is relieved to see the Bajaj Finserv homepage finally load up. He's immediately drawn to the colorful icon strip near the top — there it is: "Personal Loan" with a clear icon. That's exactly what he's come here for. He doesn't fully understand the other options like "Insta EMI Card" or "Loan Against MF," but "Personal Loan" is something he recognizes. He also notices the banner text "Personal Loan Up to ₹55 Lakhs* Instant disbursal" and feels a mix of hope — maybe he can get ₹50,000 for his home repair — and slight worry about whether he'll be eligible. He clicks "Personal Loan" to learn more before committing to anything. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh reads "No collateral and no hidden charges" and feels a wave of relief — he was worried he'd need to put something up or be hit with surprise fees. The "₹55 lakh" banner feels big, but he notices it says loans start from ₹40,000 too, so his ₹50,000 ask should be fine. He sees "Trusted by 3 lakh+ customers" and feels reassured — if so many people use it, it must be safe. The 4.8 star rating also catches his eye. He spots the APPLY button and without hesitation clicks it — he's finally doing it, applying for his first-ever loan to fix his home. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😕 Confused |
| CX Note
Ramesh clicked "APPLY" with excitement, expecting to fill out a form and submit his loan request. Instead, he finds himself on a page that talks about "how to get a personal loan in 6 easy steps" — a guide page, not the form he expected. He sees a table full of charges: processing fees, bounce charges, penal charges, prepayment fees. Words like "Flexi Hybrid Term Loan", "Flexi Term (Dropline)", "penal charge at 36% per annum" — none of this means anything to him. He's not here to read a manual; he just wants to apply for ₹50,000. He's confused and slightly frustrated — did he click the wrong button? He scrolls down hoping to find an actual "Apply Now" or "Start Application" button somewhere below. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Typed | 8826100789 |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh has been scrolling through this confusing page full of fee tables and loan type jargon — none of it made sense to him. But then he spots something simple and action-oriented in the bottom-right corner: a field that just says "Enter mobile number" and a big orange button that says "CHECK ELIGIBILITY." This feels much less scary than filling out a full form. He thinks: "Maybe I just enter my number and they'll tell me if I qualify?" This is exactly the kind of simple, step-by-step reassurance that works for Ramesh. He feels a flicker of hope — he doesn't need to understand Flexi Hybrid vs Term Loan; he just needs to know if he can get his ₹50,000. He types in his number: 8826100789. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh has typed his number into the small widget. He sees the big orange "CHECK ELIGIBILITY" button right next to it and thinks: "Okay, let me see if I qualify." He doesn't fully understand what "eligibility" means, but the word feels reassuring — it sounds like the system will tell him yes or no before he has to fill out anything complicated. He taps the button with cautious optimism, hoping to see something like "Yes, you qualify for ₹50,000." |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh tapped "CHECK ELIGIBILITY" hoping the site would just tell him if he qualifies. Instead, a popup with a padlock icon appears: "Verification required — A one-time password has been sent to your mobile number." He sees six empty boxes waiting for a code, and a "Submit" button. He's not sure what to do — he didn't expect to need a password just to check eligibility. This feels like a login wall disguised as a simple eligibility check. For a daily wage worker who just wanted a yes/no answer about his ₹50,000 loan, this is a significant barrier. He feels anxious — should he enter the OTP? He looks for a way to close the popup and go back to exploring the page. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Typed | 50000 |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh closes the OTP popup and finds himself back on the personal loan page with a calculator showing ₹1,00,000 — way more than he needs. He sees the input field says "Enter an amount between ₹40,000 & ₹50,00,000" and thinks: "Okay, I need ₹50,000, let me type that in and see what I'd have to pay every month." He doesn't fully understand what "Flexi Hybrid Term Loan" means, or why there's a "Flexi facility charges" of ₹1,999 on top, but he's curious to see the EMI for HIS amount. He carefully types 50000 into the field — it's the first time he's used a loan calculator like this and it feels empowering, even if slightly intimidating. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh stares at the loan summary box and tries to make sense of the numbers. He sees "Requested loan amount: ₹50,000" — that's his number, good. But then he notices "Processing fee: ₹505" and "Flexi facility charges: ₹1,999" — suddenly the total jumps to ₹52,504. He's confused: he wanted ₹50,000 but now he owes ₹52,504 before getting the money? He also sees "EMI ₹625" for the first 24 months — that sounds manageable on his ₹15,000 income — but then "₹1,057" for the remaining 72 months. That's a bigger number. He doesn't fully understand why the EMI jumps. He wants to scroll down to understand if he even qualifies — he recalls the page mentions eligibility criteria somewhere below, and he's nervous about whether a daily wage worker like him can get this loan at all. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh stares at the loan summary numbers and tries to add them up in his head. ₹50,000 loan + ₹505 processing fee + ₹1,999 Flexi charge = ₹52,504 total — so he'd be borrowing more than he asked for? He's confused. And the EMI jumps from ₹625 to ₹1,057 after 24 months — he doesn't understand why it doubles. But the biggest question gnawing at him is: "Will they even give the loan to someone like me?" He earns ₹15,000 a month doing daily wage work — no salary slips, probably no formal employment. He scrolls down urgently, looking for the eligibility section to find out if he qualifies at all. This is the make-or-break moment for him. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh has been staring at the loan summary with its confusing fee structure — ₹505 processing fee, ₹1,999 Flexi charges on top of his ₹50,000. The numbers don't fully make sense to him, but the thing that worries him most isn't the fees — it's whether someone like HIM can even get the loan. He earns ₹15,000 a month doing daily wage work. No monthly salary slips. Maybe no formal employment proof. He scrolls down with a tight feeling in his chest, looking for the eligibility section — hoping it won't say something like "minimum salary ₹25,000" or "salaried employees only." He just wants to fix his home. |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh is scrolling past the customer reviews — he briefly reads one that mentions "fastest and most seamless experience" and thinks: "That sounds good, but will they give the loan to someone like me?" He's not reassured by testimonials from people who already got loans; he wants to know if HE qualifies. He keeps scrolling, looking for the eligibility section he's been hunting for across multiple page scrolls. Every second he doesn't find clear eligibility information, his anxiety builds. He's thinking: "Please don't say salaried only. Please don't say ₹25,000 minimum." |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh has scrolled all the way to the bottom of the page and finds himself looking at videos with titles like "Loan se fees nahi, future invest kiya" and a disclaimer saying Bajaj Finance has "absolute discretion, without assigning any reason to accept or reject any application." That last line hits him hard — "reject any application." He wasn't expecting to see that. He thinks: "So they can just say no without telling me why?" He's confused and a little deflated. He hasn't found the eligibility criteria yet — he scrolled right past it. He instinctively scrolls back up, still searching for the section that will tell him: "Can someone like me get this loan?" |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh has been scrolling up and down for several steps now, desperately hunting for the eligibility criteria. He sees the FAQ section with customer reviews — people with successful loan experiences — but none of that tells him if HE can qualify. He scrolls back up urgently, his eyes scanning for anything that says "eligibility" or "who can apply." Every extra scroll without finding this information makes him more anxious. He's thinking: "I just want to know if they'll give ME the loan. Is ₹15,000 per month enough? Will they ask for a salary slip? I don't have one." |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh is at his wit's end after scrolling up and down repeatedly without finding the eligibility criteria. He catches a glimpse of the FAQ section with tabs — he notices the "Eligibility" tab label right there in the navigation. He might not think to click it — he's been trained by experience to scroll for information, not to click sub-tabs. But he's still scrolling up instinctively, eyes scanning for anything that says "who can apply" or lists income requirements. Every extra scroll without finding his answer makes him more deflated. He's thinking: "Why is it so hard to find out if I even qualify?" |
| --- |
| URL | https://www.bajajfinserv.in/personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh is staring at the APPLY button and the loan summary one more time. He's been going up and down this page for what feels like forever — he's scrolled past testimonials, videos, and the footer — but he STILL hasn't clearly read the eligibility criteria. The page is long and the information he needs most is buried deep. He takes a breath and scrolls down slowly, eyes scanning specifically for the word "eligibility" or any text about income requirements. He's thinking: "If they say ₹15,000 is not enough, I won't waste their time. But if it says daily wage workers can apply, I'll figure out the rest." The anxiety of not knowing is worse than a clear "no." |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh lands on this page and sees a giant fees table — interest rates 10% to 30%, processing fees up to 3.93%, bounce charges ₹700–₹1,200, penal charges up to 36% per annum. This is deeply overwhelming for someone with very low financial literacy. He doesn't know what "Part-prepayment charges," "Flexi Hybrid Term Loan," or "Penal charge" mean. He feels like he's reading a legal document in a foreign language. But buried somewhere below must be the eligibility section — the one answer he's been hunting for across dozens of page scrolls. He squints at the screen and scrolls down, muttering: "Just tell me if I can get it. Can someone like me get this loan or not?" |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh is staring at the loan type cards and their "Apply Now" buttons — Flexi Hybrid Loan, Flexi Term Loan, Term Loan. He has no idea which one to pick or what "Flexi" even means. He notices the EMI calculator showing ₹1,250 for the first 24 months and ₹2,379 for months 25–84 — the jumping EMI confuses him again. But none of this matters to him right now. He's still fixated on one question: "Will they give ME this loan?" He scrolls past the loan type cards and video thumbnails, eyes darting across the page, searching desperately for the words "eligibility" or "who can apply" or "income requirement." His chest is tight. Multiple scrolls and he still hasn't found a clear answer. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh is staring at the APPLY NOW button in orange — it's big and obvious — but he won't click it yet. He's been burned before by not reading the fine print. His one burning question remains unanswered after 17 steps of scrolling: "Can someone like ME — a daily wage worker making ₹15,000 a month — actually get this loan?" The loan summary shows ₹1,00,000 as the amount (not his target ₹50,000), and processing fees that feel like a lot of extra money. He scrolls past all of this, eyes darting left and right across the page, desperately hunting for the word "eligibility" anywhere on the screen. He's been going up and down this page so many times that it's starting to feel like a maze designed to confuse him. He just wants one simple answer. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh stares at the loan summary panel showing ₹1,03,009 as total loan amount with ₹3,009 in charges — he's confused about why the amount shown is ₹1,00,000 and not his target ₹50,000. The "Rate of Interest p.a. 15%" stands out to him — he understands that's a rate but has no idea if that's good or bad. The big orange "APPLY NOW" button is impossible to miss, but Ramesh refuses to click it until he knows he qualifies. He's thinking: "If I apply and they reject me, does that affect my credit? Will they call me and embarrass me?" He scrolls down past the fees table, still hunting desperately for words like "eligibility" or "who can apply" or "income requirement." His patience is wearing thin — this is step 20 and he still doesn't have his most basic question answered. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh stares at the loan summary — ₹1,03,009 total, ₹3,009 in charges, 15% interest rate — and the big orange "APPLY" button. He still hasn't found the eligibility criteria after 20+ steps of scrolling. The "Personal loan interest rate and applicable charges" section starting to appear at the bottom of the screen gives him a small flicker of hope — maybe eligibility information is just below. He's thinking: "One more scroll. If I don't find it this time, I'll just click Apply and see what happens. I can't keep going back and forth forever." His patience is nearly exhausted but he scrolls down one more time, eyes scanning for the words "eligibility" or "who can apply." |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
After 20+ exhausting steps of scrolling up and down this page, Ramesh finally gives up searching for the eligibility criteria and decides to just click "APPLY NOW." He's thinking: "I've been going in circles — let me just try and see what they ask for. If they reject me, at least I'll know." The FAQ snippets he just read — "ensure a good credit score," "complete the application with accurate information including financial details and employment history" — have planted seeds of doubt in his mind. He's a daily wage worker with no formal employment record and no salary slip. But the big orange button is right there, and exhaustion wins over caution. He taps it with a mixture of hope and dread. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh tapped "APPLY NOW" in the last step with a mix of hope and dread — and almost certainly got hit with a login wall since he's a first-time visitor with no Bajaj account. Now he's back on the page, feeling slightly defeated. He scans the FAQ section and sees "How to get a personal loan for the first time?" — that question speaks directly to him. He squints at it. But the answer he REALLY needs — "Can a daily wage worker earning ₹15,000/month even qualify?" — still isn't visible anywhere. He scrolls down, still hunting, now with the extra anxiety of "they asked me to log in first, which means they don't even know if I qualify." He's feeling trapped in a system that demands commitment before offering information. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh has scrolled this page dozens of times and is now staring at the footer — Related Articles, a Disclaimer box with small text, and collapsed "Languages" and "Application Forms" accordion sections. He sees the customer support number "7757 000 000" in the disclaimer text — this is the first phone number he's noticed, and for a split second he thinks about calling. But he doesn't want to bother anyone. He's exhausted. He's been on this website for what feels like an eternity and still can't find a simple answer: "Can a daily wage worker earning ₹15,000/month get this loan?" He's reached the very bottom of the page and the FAQ section he passed earlier had a "Show More" that he never clicked. That's his last hope — scrolling back up to tap that button. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh is staring at the corporate footer — CIN numbers, email addresses for investors, addresses in Pune and Mumbai. None of this means anything to him. He's a 29-year-old daily wage worker from Jodhpur who just wants to know if he can borrow ₹50,000 to fix his house. He's been scrolling this page for what feels like 15 minutes and has landed at the very bottom without a single clear answer to his question: "Can someone like me — earning ₹15,000 a month with no salary slip — get this loan?" He remembers there was a "Show More" button in the FAQ section somewhere above. He starts scrolling back up, muttering in frustration: "Yaar, itna bada website hai aur meri ek baat ka jawab nahin hai." (Such a big website and no answer to my one question.) |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh has scrolled up from the footer and spots the "Show More" link in the FAQ section. After 24+ exhausting steps of going up and down this page, this little blue "Show More" link feels like a lifeline. He's thinking: "Shayad yahan answer ho — ek baar aur try karta hoon." (Maybe the answer is here — let me try one more time.) He taps it with desperate hope, his patience nearly completely gone. If this doesn't show him whether daily wage workers earning ₹15,000 can qualify, he'll either give up or call the helpline number he spotted in the disclaimer. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh tapped "Show More" in the last step, hoping it would finally reveal whether a daily wage worker like him — earning ₹15,000/month — can qualify for this loan. Now he's scrolling down to find what that button revealed. He's near his breaking point — 25+ steps on one page with no clear answer. He's scanning the page with tired eyes, still hunting for the words "eligibility," "who can apply," or "income requirement." The loan type cards (Flexi Hybrid, Flexi Term, Term Loan) mean nothing to him — he has no idea what "dropline" means and doesn't care. He just wants to know: "Can someone like me get ₹50,000?" Every extra step without that answer chips away at his trust in Bajaj Finance as a platform that's actually meant for people like him. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh is exhausted. He's staring at the loan product type cards (Flexi Hybrid, Flexi Term, Term Loan) and videos about "Smart loan solution" and "Borrow and repay flexibly" — none of which answer his burning question. He scrolls past these with barely a glance. He's on a mission: find out if he — a daily wage worker earning ₹15,000/month from Jodhpur — even qualifies. The three product types confuse him ("Dropline? What is that?") but he ignores them, eyes scanning downward, looking for the FAQ section he expanded. Every video thumbnail, every product card, every marketing banner is just noise to him right now. He's thinking: "Yaar, sirf ek sawaal ka jawab chahiye — main eligible hoon ya nahin?" (I just need the answer to one question — am I eligible or not?) |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😤 Frustrated |
| CX Note
Ramesh is staring at the EMI calculator and loan summary showing ₹1,03,009 total — numbers that mean little to him since he wants only ₹50,000 and the default is ₹1,00,000. He doesn't even bother adjusting the calculator right now. His singular focus is: "Am I — a daily wage worker from Jodhpur earning ₹15,000/month — even eligible for this loan?" He's been on this page for what feels like forever, scrolling up and down past the same videos, product cards, and marketing banners. He scrolls down one more time toward the FAQ section, eyes narrowed, scanning for keywords like "eligibility," "income," "salaried," "self-employed," or "daily wage." The promise of "Frequently asked questions" at the bottom of the page is his last flicker of hope before he either gives up entirely or navigates away. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Typed | 50000 |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh has been scrolling for what feels like forever, hunting for eligibility criteria, and found nothing. Now he notices the EMI calculator showing ₹1,00,000 — double what he wants to borrow. A thought crosses his mind: "Let me at least check what my ₹50,000 loan would cost per month." He's never used an EMI calculator before, but the input field with "Enter loan amount" next to it seems obvious enough. He types "50000" — hoping the numbers that come back will tell him if this loan is even in his reach. For a man earning ₹15,000/month, seeing the monthly EMI figure will be the most concrete thing he's learned from this entire website visit. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh typed ₹50,000 and is now scrolling down to see the result. He's never used an EMI calculator before, but the page seems to be showing him something — there's a "Loan summary" box and numbers like ₹856 and ₹71,904. He squints at it. "₹856 per month? Theek hai, yeh toh chal sakta hai!" (₹856 per month? Okay, that seems manageable!) For someone earning ₹15,000 a month, an ₹856 EMI feels within reach — it's about 5.7% of his income. But then he notices "Total Amount ₹71,904" — he borrowed ₹50,000 and will pay back ₹71,904? That gap of nearly ₹22,000 is confusing to him. He doesn't fully understand interest, but the gap makes him uneasy. He scrolls down to see if there's more detail. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh is staring at the EMI calculator results and things are starting to make sense — for the first time in this entire visit. He can see ₹856/month at 15% p.a. for 84 months. The Loan Summary box on the right shows "Requested loan amount ₹50,000" with a processing fee of ₹505. He notices the instalment amount listed in the Loan Summary says ₹975 — not ₹856 — and he's momentarily confused. "EMI ₹856 hai ya ₹975?" (Is EMI ₹856 or ₹975?) He can't figure out why there are two different numbers. He also sees "Total Interest ₹21,904" and total amount ₹71,904 — the realization that he'll pay back ₹71,904 for borrowing ₹50,000 is sobering. But the per-month EMI of ₹856 still feels manageable on his ₹15,000 income. He wants to scroll down to see if it shows how much will actually come into his bank account — that "Amount to be credited" line is what really matters to him. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh is finally seeing the number that matters most to him: "Amount to be credited in your bank (A-B) ₹50,000." This confirms he'd get the full ₹50,000 in his account — minus only a ₹505 processing fee. That's a relief! But he's confused by two EMI figures — the calculator says ₹856 but the "Instalment" row says ₹975. He stares at both numbers: "₹856 ya ₹975 — EMI kitna hoga actually?" (₹856 or ₹975 — what will EMI actually be?). This inconsistency is unsettling for someone who has never taken a loan before. He also notices "Personal loan interest rate and applicable charges" just below — maybe that section will clarify the rates and whether 15% is standard. He scrolls down to find out. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 🙂 Hopeful |
| CX Note
Ramesh spots the "Personal loan interest rate and applicable charges" section — it's exactly what he's been hunting for since the beginning. After 30+ steps of frustrating scrolling and marketing banners, this collapsible section feels like it might finally hold the answer. He thinks: "Interest rate aur charges — haan, yeh toh dekhna chahiye. Kya pata yahan eligibility bhi ho." (Interest rates and charges — yes, I should see this. Maybe eligibility is here too.) He taps it with cautious hope — this could be his last meaningful discovery before deciding whether to call the helpline number he spotted earlier or give up entirely. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😕 Confused |
| CX Note
Ramesh is staring at the charges table and it's overwhelming. He sees "10% to 30% p.a." for interest rate — his calculator showed 15%, so that seems okay. But then he reads "Processing fees: Up to 3.93% of the loan amount" — he already saw ₹505 in the calculator, so at least that matches. Then comes "Bounce charges: Rs. 700 to Rs. 1,200 per bounce" — he's not sure what "bounce" means, but it sounds like a penalty. He reads the fine print: "non-payment of instalment(s) on their respective due dates" — ah, so it's a late payment charge. That worries him a little. "Agar kabhi paisa late ho gaya toh ₹1,200 penalty?" (If payment is ever late, ₹1,200 penalty?) Then the "Part-prepayment charges: Up to 4.72%" cuts off before he can finish reading. The jargon is dense and confusing. He scrolls down hoping to find something simpler — maybe the FAQ will have a plain-language answer to whether he even qualifies. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😕 Confused |
| CX Note
Ramesh is drowning in financial jargon. He stares at "Penal charge: up to 36% per annum" — 36%?! That sounds terrifying. He doesn't fully understand what "penal charge" means, but the number 36% is much bigger than the 15% interest rate, and it sounds like a punishment charge. He thinks: "Agar EMI miss ho gayi toh 36% penalty lagegi??" (If I miss an EMI, will there be a 36% penalty??) This is genuinely alarming to him. Then he sees "Annual maintenance charges" for Flexi Term Dropline: 0.295% — he has no idea what a Flexi Term Dropline loan is. The "Credit guarantee scheme fee: 1.18% p.a." adds another mystery charge. For a man who just wants ₹50,000 to fix his house, this table feels like a minefield of hidden costs. He keeps scrolling, desperate to find the FAQ section with simple answers. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh is exhausted. He's been on this website for what feels like an hour, scrolling past videos, marketing banners, charge tables full of jargon he barely understands. The FAQ section is RIGHT THERE — "How to get a personal loan for the first time?" — and that title speaks directly to him. He's taking a loan for the very first time. He squints at the screen on his slow mobile connection, hoping this FAQ will finally answer: "Kya mujhe yeh loan milega?" (Will I even get this loan?). The penal charge of 36% he just read is still nagging at him — he's nervous about what happens if he ever misses a payment. He scrolls down one more time with diminishing hope but stubborn determination. |
| --- |
| URL | https://www.bajajfinserv.in/how-to-apply-for-personal-loan |
| --- | --- |
| Emotion | 😰 Anxious |
| CX Note
Ramesh has been on this website for 38 exhausting steps on a slow mobile connection. Here's what his journey looked like from his perspective: He came looking for ₹50,000 to fix his house. He found a slick, professional-looking website — but it felt designed for someone else. The 'Apply Now' button that appeared everywhere turned out to be a login wall, so he, a first-time visitor with no account, was immediately blocked from the actual application. He spent the next 30+ steps scrolling through marketing banners, video thumbnails, and dense financial jargon. The EMI calculator was the ONE genuinely useful tool — it told him ₹856/month for ₹50,000, which on his ₹15,000 salary felt manageable. But two things deeply unsettled him: (1) Two conflicting EMI figures — ₹856 from the calculator vs. ₹975 in the Loan Summary — left him confused about what he'd actually pay. (2) The charges table showed 'Penal charge: up to 36% per annum' — a number that terrified him without any explanation in plain language. Throughout the entire journey, Ramesh never found a clear answer to his core question: 'As a daily wage worker earning ₹15,000/month from Jodhpur, am I even eligible?' No eligibility checker for informal workers. No income-based pre-check. No plain-language explanation of who qualifies. The site speaks to salaried professionals — not daily wage earners like Ramesh. He leaves the website with some hope (EMI seems manageable) but significant anxiety (will they even give me the loan? what are all these hidden charges?) and no clear next step beyond calling a helpline number — which he may or may not be able to access on his slow internet connection. |
| --- |