<!-- converted from CX Audit Run Guide.docx -->

🧠 End-to-End Guide: Add Personas + Run CX Audit (Properly)
This guide will walk you step-by-step to:
Add your own personas
Run a full CX audit across all personas
View and use the results
No coding knowledge assumed.

📌 PART 1: ADD YOUR PERSONAS
🟢 Step 1: Locate the persona file
Go to your project folder:
CX Audit Agent/
Then open:
personas/bajaj_personas.md

🟢 Step 2: Understand the format (VERY IMPORTANT)
Each persona must follow this exact structure:
## Persona: Persona Name
- Age: 28
- Background: Short description
- Intent: Clear goal (MANDATORY)
- Constraints: Optional but useful
👉 The Intent is the most important field
This drives the entire journey.

🟢 Step 3: Add your own personas
You can add as many as you want.
✅ Example (good personas)
## Persona: Urgent Loan Seeker
- Age: 32
- Background: Freelancer with irregular income
- Intent: Get instant approval for a ₹1.5 lakh loan
- Constraints: Low patience, needs quick decision

## Persona: EMI Explorer
- Age: 25
- Background: First job, exploring financing options
- Intent: Compare EMI options for gadgets
- Constraints: Confused by financial jargon

## Persona: Existing Customer - EMI Check
- Age: 40
- Background: Business owner with active loan
- Intent: Check EMI details and prepay loan
- Constraints: Time-sensitive

⚠️ Common mistakes to avoid
❌ Wrong:
Persona: Loan User
✅ Correct:
## Persona: Loan User

❌ Missing intent:
- Intent:
👉 This will break the system

❌ Too vague:
- Intent: Explore website
👉 Always make intent specific and actionable

🟢 Step 4: Save the file
Press:
Ctrl + S
👉 Done. Personas are now loaded automatically.

🚀 PART 2: RUN CX AUDIT (PROPER WAY)
🟡 Step 1: Open terminal
Inside your project folder:
Click address bar
Type:
cmd
Press Enter

🟡 Step 2: (Optional but recommended) Quick test
Run one persona:
python main.py --persona "Urgent Loan Seeker" --max-steps 30
👉 This ensures everything is working

🟡 Step 3: Run ALL personas (FULL CX AUDIT)
Now run:
python main.py --max-steps 30
👉 This will:
Load all personas from .md
Run journeys one-by-one
Perform CX evaluation
Generate reports

🟡 Step 4: Faster run (optional)
Skip evaluation first:
python main.py --max-steps 30 --skip-eval
Then run full later.

📊 PART 3: VIEW RESULTS
📁 Go to:
CX Audit Agent/reports/

🔵 1. Persona-level report
Example:
reports/urgent-loan-seeker/report.md
👉 Contains:
Journey summary
Friction points
CX insights
Recommendations

🔵 2. Master report (IMPORTANT)
reports/master_report.md
👉 Shows:
All personas
CX scores
Summary insights

🔵 3. Screenshots (visual proof)
screenshots/
👉 Shows:
Each step visually
What agent clicked / saw

🔵 4. Logs (advanced)
logs/
👉 Raw data of all actions (optional)

🧠 BEST PRACTICES (IMPORTANT)
✅ Use 4–6 strong personas
Not too many, not too few

✅ Make intents realistic
Think like real users:
“Apply for ₹2L loan”
“Check EMI”
“Compare options”

✅ Use 25–35 steps
--max-steps 30
👉 Ideal for deep journeys

❌ Avoid debug mode for real runs
--debug ❌
👉 Only for testing

⚡ FINAL QUICK FLOW
Edit:
personas/bajaj_personas.md
Add personas (correct format)
Save file
Run:
python main.py --max-steps 30
Open:
reports/master_report.md

🚀 YOU ARE NOW READY
You can now:
Simulate multiple users
Run deep CX journeys
Generate real insights
This is a production-level CX audit workflow.


📊 CX Dashboard – Usage Guide (Step-by-Step)
This section explains how to open, use, and refresh your CX Audit Dashboard whenever you want to view results.

🧠 WHAT IS THE DASHBOARD?
The dashboard is a local web interface that:
Reads CX audit outputs from:
reports/
logs/
screenshots/
Displays:
Persona-wise results
CX scores
Reports in a clean UI
⚠️ Important:
The dashboard is not always running. You must start it manually whenever you want to view it.

🚀 HOW TO OPEN THE DASHBOARD
🟢 Step 1: Go to project folder
Navigate to:
CX Audit Agent/

🟢 Step 2: Open terminal
Inside the folder:
Click the address bar
Type:
cmd
Press Enter

🟢 Step 3: Start dashboard server
Run:
cd dashboard
python -m http.server 8765
👉 This starts a local server

🟢 Step 4: Open dashboard in browser
Open:
http://localhost:8765
👉 Your CX Dashboard will load

🔄 HOW TO REFRESH DATA
Whenever you:
Run new CX audits
Add new personas
Generate new reports
👉 The dashboard automatically uses updated data
All you need to do:
Press F5 (Refresh)

🧭 DAILY USAGE FLOW
Follow this sequence for regular usage:

Step 1: Run CX audit
python main.py --max-steps 30

Step 2: Start dashboard
cd dashboard
python -m http.server 8765

Step 3: Open dashboard
http://localhost:8765

Step 4: Refresh to see latest results
Press F5

⚠️ IMPORTANT RULES
✅ Do this
Keep terminal open while using dashboard
Refresh browser after new runs
Ensure correct folder path (dashboard/)

❌ Avoid this
Closing terminal → dashboard will stop
Running server from wrong folder
Changing port unless necessary

⚡ OPTIONAL: ONE-CLICK START (RECOMMENDED)
You can simplify the process using a .bat file.

🟢 Step 1: Create file
Inside dashboard/, create:
start_dashboard.bat

🟢 Step 2: Add this content
cd /d %~dp0
python -m http.server 8765
pause

🟢 Step 3: Run dashboard
Double-click:
start_dashboard.bat
👉 Dashboard server starts instantly

🟢 Step 4: Open browser
http://localhost:8765

🧠 HOW IT WORKS (SIMPLE EXPLANATION)
Dashboard → reads → reports folder → displays UI
No internet required
No backend needed
Fully local system

📌 QUICK SUMMARY
To open CX Dashboard:
1. Go to dashboard folder
2. Run: python -m http.server 8765
3. Open: http://localhost:8765
4. Refresh browser to see latest results

🚀 YOU ARE READY
You can now:
View CX audits anytime
Present results in a clean UI
Track persona-wise insights easily

