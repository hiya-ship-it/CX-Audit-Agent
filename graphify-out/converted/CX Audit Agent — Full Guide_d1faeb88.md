<!-- converted from CX Audit Agent — Full Guide.docx -->

CX Audit Agent
Complete Product Guide — What It Is, What It Does, How to Run It

────────────────────────────────────────────────────────────────────────────────

# 1.  What Has Been Built

The CX Audit Agent is an AI-powered customer experience testing system. It acts like a real user visiting a website or mobile app, navigates through it, records everything that works well or causes friction, and produces detailed audit reports with scores, findings, and recommendations — all without any manual testing.

It was built specifically to audit the Bajaj Finserv digital properties but the architecture is general enough to point at any website or Android app.

## Core Components Built
### 1.1  Web Audit Agent  (main.py)
Uses a Playwright-controlled browser (Chromium) and Claude AI to visit a target website. Claude sees the page content, decides what to click or type next, executes that action through the browser, and records the experience at every step. The agent runs autonomously until the persona's goal is achieved or the step limit is reached.
### 1.2  Mobile / App Audit Agent  (mobile_main.py)
Uses Appium + Android emulator and Claude AI to test the mobile experience. Claude receives a screenshot of the device screen, decides the next action (tap, swipe, type, back), and executes it on the real emulator. This covers both the Bajaj Finserv mobile website running in Chrome on Android and can be extended to a native Android app.
### 1.3  Persona System  (personas/bajaj_personas.md)
The agent does not test as a generic user. It tests as specific, realistic personas — each with a name, age, occupation, financial literacy level, goal, device type, and behavioural constraints. Multiple personas run in sequence so you get results from multiple user perspectives in one run.
Personas currently defined for Bajaj Finserv:
- Arjun Mehra — 32, salaried software engineer, researching gold loan rates
- Priya Nair — 28, freelance designer, checking personal loan eligibility
- Ramesh Patel — 55, small business owner, exploring business loan options
- Sunita Sharma — 45, homemaker, looking for fixed deposit information
- Vikram Singh — 38, government employee, comparing insurance products
### 1.4  CX Evaluator  (evaluation/cx_evaluator.py)
After each journey completes, Claude acts as a CX expert and scores the experience across seven dimensions on a scale of 0 to 10:
- Navigation & Findability
- Content Clarity
- Trust & Credibility
- Load & Performance
- Mobile Responsiveness
- Conversion Ease
- Emotional Tone
It also extracts friction points (high / medium / low severity), positive moments, and prioritised recommendations (P1 / P2 / P3).
### 1.5  Report Generator  (reporting/report_generator.py)
Produces three output formats after every run:
- Per-persona Markdown report  —  reports/{persona-slug}/report.md
- Per-persona JSON log  —  reports/{persona-slug}/journey_log.json
- Master summary report  —  reports/master_report.md  (aggregates all personas)
Mobile audit reports go to reports/mobile/ so they never overwrite web reports.
### 1.6  Dashboard  (dashboard/index.html)
A fully interactive web dashboard that displays all audit results visually. It reads the JSON logs and renders:
- Run history list with filter by audit type (web / app)
- CX scores per dimension with colour-coded bars
- Persona details tab — who was tested and their profile
- Friction points sorted by severity
- Recommendations sorted by priority (P1 first)
- Step-by-step execution log with success/fail status per step
- Screenshots tab showing captured screenshots per step
### 1.7  Web Server  (server.py)
A Flask API server that sits between the dashboard and the audit engine. It exposes REST endpoints so the dashboard can:
- List all past runs
- Fetch report data for any run
- Trigger a new web or app audit run from the browser
- Stream real-time status back to the UI while a run is in progress

────────────────────────────────────────────────────────────────────────────────

# 2.  What It Can Do

## 2.1  Audit Modes
### Web Audit — Logged Out
Visits the target website as an unauthenticated user. Tests the public-facing experience: navigation, product discovery, information clarity, and lead generation flows.
### Web Audit — Logged In
Visits the website with a test account already authenticated. Tests the post-login experience: dashboard usability, account management, and transactional flows.
### Mobile / App Audit — Chrome on Android
Opens the mobile website in Chrome on an Android emulator. Tests how the responsive web experience feels on a real Android device, including tap accuracy, scroll behaviour, and mobile-specific navigation patterns.
### Mobile / App Audit — Native Android App  (extendable)
By setting the app package name in config/app_config.yaml, the same agent can audit a native Android app installed on the emulator, using the exact same screenshot-based Claude decision loop.
## 2.2  Multi-Persona Testing
One command runs the audit for all defined personas sequentially. Each persona explores the site differently based on their goal and profile. The master report shows side-by-side comparisons across all personas.
## 2.3  Debug Mode
Run with --debug flag to test only the first persona with a maximum of 10 steps. Useful for verifying configuration before a full run.
## 2.4  Autonomous Navigation
The agent decides every action itself — what to click, what to type, when to scroll, when to declare success or failure. No scripts or selectors need to be maintained.
## 2.5  Observation Recording
As it navigates, the agent records friction observations (slow load, confusing label, broken link, hidden CTA) and delight observations (clear pricing, fast response, reassuring copy) in real time.
## 2.6  Screenshot Capture
Screenshots are saved at configurable points during the journey — on every step (verbose mode) or only on failure. Mobile audit always saves a screenshot per step. All screenshots are accessible from the dashboard Screenshots tab.
## 2.7  Retry and Resilience
If an action fails (element not found, page load timeout), the agent retries automatically up to the configured retry count before moving on. Failures are logged and included in the report.
## 2.8  Dashboard Filtering and History
The dashboard keeps a history of every run. You can filter by audit type (Web vs App), view individual persona reports, compare scores across runs, and drill down into any step.

────────────────────────────────────────────────────────────────────────────────

# 3.  Prerequisites — Install These Once

Before running anything, ensure the following are installed on your machine.
## 3.1  Python and Packages
- Install Python 3.11 or higher from python.org
- Open a terminal in the CX Audit Agent folder and install all Python packages:
pip install -r requirements.txt
- Install Playwright browsers:
playwright install chromium
- Install python-docx if not present (only needed to regenerate this document):
pip install python-docx
## 3.2  Android Emulator  (for mobile audit only)
- Install Android Studio from developer.android.com/studio
- Open Android Studio, go to Device Manager, create a virtual device:
- Select Pixel 6 or Pixel 6a
- Select API Level 33 or higher
- Finish and download the system image when prompted
- Note the Android SDK path — typically:
C:\Users\YourName\AppData\Local\Android\Sdk
## 3.3  Appium  (for mobile audit only)
- Install Node.js from nodejs.org
- Install Appium globally:
npm install -g appium
- Install the UiAutomator2 driver:
appium driver install uiautomator2
## 3.4  API Key
- Create a file called  .env  in the CX Audit Agent folder
- Add your Anthropic API key:
ANTHROPIC_API_KEY=sk-ant-your-key-here
You can get an API key from console.anthropic.com

────────────────────────────────────────────────────────────────────────────────

# 4.  How to Run — Web Audit

The web audit requires only Python, Playwright, and an Anthropic API key. No emulator needed.
## Step 1 — Open a terminal in the project folder
Open Command Prompt or PowerShell, then navigate to the folder:
cd "C:\Users\Hiya Bhandari\Desktop\Folders\CX Audit Agent"
## Step 2 — Run the web audit
### Option A — All personas, full run
python -X utf8 main.py
### Option B — Debug mode  (1 persona, 10 steps, fastest)
python -X utf8 main.py --debug
### Option C — Headless mode  (no visible browser window)
python -X utf8 main.py --no-headed
### Option D — Logged-in audit
python -X utf8 main.py --auth-mode logged_in
### Option E — Single persona by name
python -X utf8 main.py --persona "Arjun Mehra"
## How to run a logged-in audit
python -X utf8 main.py --auth-mode logged_in --login-url https://www.bajajfinserv.in/login --login-username 8826100789

## Step 3 — Watch the terminal
The terminal shows live progress: which persona is running, each step the agent takes, actions executed, and any failures. A summary table appears at the end with CX scores.
## Step 4 — Find your reports
After the run, reports are written to:
- reports/{persona-slug}/report.md  —  full Markdown report per persona
- reports/{persona-slug}/journey_log.json  —  raw JSON data used by the dashboard
- reports/master_report.md  —  combined summary of all personas

────────────────────────────────────────────────────────────────────────────────

# 5.  How to Run — Mobile / App Audit

The mobile audit requires the Android emulator and Appium in addition to Python.
## Step 1 — Start the Android emulator
Open Android Studio. In Device Manager, click the Play button next to your Pixel 6 device.
Or start it from terminal using the emulator command:
emulator -avd Pixel_6 -no-snapshot-load
Wait until the Android home screen is fully loaded before proceeding.
## Step 2 — Confirm the emulator is detected
Run this command to verify Android can see the device:
C:\Users\Hiya Bhandari\AppData\Local\Android\Sdk\platform-tools\adb.exe devices
You should see:  emulator-5554   device
## Step 3 — Start Appium with ANDROID_HOME set
This is the most important step. Appium needs to know where the Android SDK is. Open a new terminal window and run exactly this command:
set ANDROID_HOME=C:\Users\Hiya Bhandari\AppData\Local\Android\Sdk
set ANDROID_SDK_ROOT=C:\Users\Hiya Bhandari\AppData\Local\Android\Sdk
appium --port 4723 --allow-insecure uiautomator2:chromedriver_autodownload
Leave this terminal open. Appium must stay running for the entire duration of the mobile audit. You should see:  Appium REST http interface listener started on http://0.0.0.0:4723
## Step 4 — Run the mobile audit  (in a second terminal)
Open a second terminal window in the project folder and run:
### Option A — Debug mode  (1 persona, 10 steps)
python -X utf8 mobile_main.py --target-url https://www.bajajfinserv.in --auth-mode logged_out --debug
### Option B — Full run, all personas
python -X utf8 mobile_main.py --target-url https://www.bajajfinserv.in --auth-mode logged_out
### Option C — Single persona
python -X utf8 mobile_main.py --target-url https://www.bajajfinserv.in --persona "Arjun Mehra" --debug
## Step 5 — Watch the emulator and terminal
The emulator screen will show Chrome opening Bajaj Finserv. The terminal shows each step Claude decides to take — taps, swipes, observations, and the final score.
## Step 6 — Find your reports
Mobile reports are written to a separate folder to avoid overwriting web reports:
- reports/mobile/{persona-slug}/report.md
- reports/mobile/{persona-slug}/journey_log.json
- reports/mobile/master_report.md
- reports/mobile/manifest.json
- screenshots/mobile/{persona-slug}/step_001.png  (one screenshot per step)

────────────────────────────────────────────────────────────────────────────────

# 6.  How to View Results on the Dashboard

The dashboard is a web interface that displays all audit results visually. You can use it two ways: via the Flask server (recommended) or by opening the HTML file directly.
## Method A — Via the Flask Server  (recommended)
### Step 1 — Start the server
Open a terminal in the project folder and run:
python -X utf8 server.py
You should see:  Running on http://127.0.0.1:5000
### Step 2 — Open the dashboard
Open a browser and go to:
http://127.0.0.1:5000
The dashboard loads automatically. It reads all report data from the reports/ folder and displays every run in the Run History panel on the left.
### Step 3 — Trigger a new audit from the dashboard
Click the New Audit button in the top right of the dashboard. A dialog appears where you can:
- Choose audit type: Web or App
- Enter a target URL
- Select logged_out or logged_in
- Click Run
The server starts the audit in a background subprocess. The dashboard shows a running indicator. When complete, the new run appears in the history list.
## Method B — Open the HTML file directly  (offline, no server needed)
Navigate to the dashboard folder in File Explorer:
C:\Users\Hiya Bhandari\Desktop\Folders\CX Audit Agent\dashboard\index.html
Double-click index.html to open it in your default browser. In this mode, the dashboard can only read reports that are already in the dashboard/reports/ folder. To copy the latest reports there, run the following after an audit:
xcopy /E /I /Y "reports\arjun-mehra" "dashboard\reports\arjun-mehra"
xcopy /E /I /Y "reports\mobile\arjun-mehra" "dashboard\reports\arjun-mehra-mobile"

────────────────────────────────────────────────────────────────────────────────

# 7.  Navigating the Dashboard

## Run History Panel  (left side)
Lists every completed audit run. Each entry shows the persona name, audit type (Web / App), auth mode, and overall CX score. Click any run to load its full report on the right.
Use the filter buttons at the top to show only Web runs or only App runs.
## Report Panel  (right side — five tabs)
### Overview Tab
Shows the overall CX score, journey outcome (goal achieved / blocked / max steps reached), number of steps taken, and pages visited.
### Persona Tab
Shows who was tested: name, age, occupation, location, device, financial literacy level, intent, constraints, and success criteria.
### Scores Tab
Shows the seven CX dimension scores as bars. Each dimension has a numeric score out of 10 and the reasoning Claude used to arrive at that score.
### Friction & Recommendations Tab
Lists all friction points sorted by severity (red = high, yellow = medium, green = low). Below that, all recommendations sorted by priority (P1 = immediate action, P2 = important, P3 = nice to have).
### Steps Tab
Shows every action the agent took — the action type, the target element or URL, whether it succeeded or failed, and the CX note Claude recorded about that step.

────────────────────────────────────────────────────────────────────────────────

# 8.  Configuration Files

## config.py  —  Main Settings
Controls the web audit behaviour:
- TARGET_URL  —  the website to audit  (default: https://www.bajajfinserv.in)
- CLAUDE_MODEL  —  which Claude model to use
- MAX_STEPS  —  maximum steps before the agent stops  (default: 25)
- HEADLESS  —  whether to show the browser window or run silently
## config/app_config.yaml  —  Mobile Settings
Controls the mobile audit:
- deviceName  —  the emulator to connect to  (emulator-5554)
- browserName  —  set to Chrome for mobile web, or blank for native app
- appPackage / appActivity  —  for native app mode, the Android package and launch activity
- max_steps, action_delay_ms, element_timeout_secs  —  journey runtime settings
## personas/bajaj_personas.md  —  Persona Definitions
Each persona is defined in a Markdown block with fields for name, age, gender, occupation, location, device, financial_literacy, intent, constraints, behaviour, and success_criteria. Add or edit personas here to change who the agent tests as.
## .env  —  Secrets
Stores the API key. Never commit this file to version control.
ANTHROPIC_API_KEY=sk-ant-your-key-here

────────────────────────────────────────────────────────────────────────────────

# 9.  Quick Reference — All Commands at a Glance

## Web Audit Commands
python -X utf8 main.py                              # all personas
python -X utf8 main.py --debug                     # 1 persona, 10 steps
python -X utf8 main.py --no-headed                 # no browser window
python -X utf8 main.py --auth-mode logged_in       # logged-in audit
python -X utf8 main.py --persona "Arjun Mehra"     # single persona
## Mobile Audit Commands
# Step 1: Start emulator (Android Studio or terminal)
emulator -avd Pixel_6 -no-snapshot-load

# Step 2: Start Appium (run in its own terminal window)
set ANDROID_HOME=C:\Users\Hiya Bhandari\AppData\Local\Android\Sdk
appium --port 4723 --allow-insecure uiautomator2:chromedriver_autodownload

# Step 3: Run mobile audit
python -X utf8 mobile_main.py --target-url https://www.bajajfinserv.in --auth-mode logged_out --debug
python -X utf8 mobile_main.py --target-url https://www.bajajfinserv.in --auth-mode logged_out
## Dashboard / Server Commands
python -X utf8 server.py                           # start dashboard server
Then open:  http://127.0.0.1:5000  in a browser
## Verify Emulator Connection
C:\Users\Hiya Bhandari\AppData\Local\Android\Sdk\platform-tools\adb.exe devices

────────────────────────────────────────────────────────────────────────────────

# 10.  Folder Structure

CX Audit Agent/
  main.py                  Web audit entry point
  mobile_main.py           Mobile / app audit entry point
  server.py                Flask API server for the dashboard
  config.py                Global settings and constants
  .env                     API key  (create this yourself)
  requirements.txt         Python dependencies

  agents/                  AI agent logic
    controller.py          Main web journey loop
    decision_engine.py     Claude prompt and action parsing
    memory.py              Step-by-step state tracking

  browser/                 Playwright browser helpers
    controller.py          Click, type, scroll, navigate
    state_extractor.py     Extract page text and structure

  mobile/
    drivers/appium_driver.py   Appium session factory

  evaluation/
    cx_evaluator.py        Scores journey against CX dimensions

  reporting/
    report_generator.py    Writes Markdown + JSON reports

  parsers/
    persona_parser.py      Reads persona definitions from Markdown

  personas/
    bajaj_personas.md      Persona definitions

  config/
    app_config.yaml        Mobile / Appium configuration

  dashboard/               Frontend web dashboard
    index.html
    script.js
    styles.css
    reports/               Report data read by dashboard

  reports/                 Web audit output
  reports/mobile/          Mobile audit output
  screenshots/             Screenshots taken during audits
  logs/                    Raw step logs

────────────────────────────────────────────────────────────────────────────────

# 11.  Troubleshooting

## ANTHROPIC_API_KEY not found
Make sure the .env file exists in the project root folder and contains your key on the first line:
ANTHROPIC_API_KEY=sk-ant-your-key-here
## Appium cannot find Android SDK
You must set ANDROID_HOME before starting Appium. Use the set commands shown in Section 5 Step 3. Do not skip this step.
## emulator-5554 not found / adb devices shows nothing
The Android emulator is not running. Start it from Android Studio Device Manager before running the mobile audit.
## Playwright browser not found
Run this once:
playwright install chromium
## UnicodeEncodeError / emoji crashes on Windows
Always run Python with the -X utf8 flag as shown in all commands above. This is already handled — do not remove that flag.
## Port 4723 already in use
A previous Appium process is still running. Kill it:
taskkill /F /IM node.exe
Then restart Appium using the command in Section 5 Step 3.
## Dashboard shows no runs
If using the server (Method A), make sure the server is running and you are on http://127.0.0.1:5000. If using the HTML file directly (Method B), copy the report folders into dashboard/reports/ first.

────────────────────────────────────────────────────────────────────────────────
FOR LOGGED IN
python -X utf8 main.py --auth-mode logged_in --login-username 8826100789
Every-time guide to run the Mobile Audit

Step 1 — Double-click the launcher script
Go to your project folder and double-click start_mobile_audit.bat
It automatically does all three things for you:
Starts the Pixel 6 emulator
Connects adb
Starts the Appium server
Wait for it to say "All services started!" then press any key.

Step 2 — Wait for the emulator to fully boot
A separate window titled "Android Emulator" will open. Wait until you see the Android home screen inside it (takes ~30–60 seconds on first boot).

Step 3 — Open a terminal in the project folder
Right-click inside the CX Audit Agent folder → Open in Terminal (or open Command Prompt and cd to the folder).

Step 4 — Run the audit
# Quick test (1 persona, 10 steps — use this first to verify everything works)
python -X utf8 mobile_main.py --debug

# Full audit (all personas)
python -X utf8 mobile_main.py

# Specific persona only
python -X utf8 mobile_main.py --persona "First-Time"

What the 3 windows mean

If something goes wrong

Start emulator     →  start_mobile_audit.bat   (double-click)
Start dashboard    →  python server.py         (in terminal)
Open browser       →  http://localhost:5000
Launch audit       →  App Audit tab → fill form → Launch
View results       →  Run History tab → View
CX Audit Agent  |  Built with Claude AI + Playwright + Appium



| Window | What it is | Can you close it? |
| --- | --- | --- |
| Android Emulator | The Pixel 6 phone screen | ❌ No — keep open during audit |
| Appium Server | The bridge between Python and the phone | ❌ No — keep open during audit |
| Your terminal | Where you run mobile_main.py | This is where you work |
| Problem | Fix |
| --- | --- |
| emulator not recognized | Open a new terminal — old ones don't have the PATH update |
| adb: no devices | Run adb kill-server then adb start-server, wait 10s |
| Could not connect to Appium | Check the Appium window is open; if not, run appium in a new terminal |
| Emulator stuck on boot logo | Close it, wait 30s, re-run start_mobile_audit.bat |