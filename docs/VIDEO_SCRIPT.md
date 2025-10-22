# 3‑Minute Demo Video Script (Fast)

Use Windows Game Bar (Win+G) or Loom. Record in 1080p. Keep browser + one terminal visible.

## 0:00–0:25 Intro
- "Hi, I’m [Your Name]. This is the Autonomous Ocean Forecasting Agent."
- "Built on AWS Bedrock AgentCore + Amazon Nova Pro; multi‑agent: ingest → analyze → alert."
- "Goal: actionable maritime safety alerts from real ocean & weather data."

## 0:25–1:30 Live Demo
1) Open Amplify site (paste URL) → point to UI polish
   - “Notice the shimmering skeleton and the stepper showing how the agent works: Understanding → Fetching → Analyzing → Recommending.”
   - “It defaults to mock mode and can call a live API if available.”
2) Type a query: “Is it safe to sail from Cape Town to Mossel Bay tomorrow?” → Click Analyze
   - Call out the animated progress bar and step transitions while loading.
3) When results appear, highlight the cinematic reveal
   - Alert badge, animated risk bar fill, then a typewriter summary, and staggered factor cards.
   - Call out data sources (Open‑Meteo, Copernicus optional)
4) Optional: Paste your API Gateway URL into “API endpoint”, uncheck “Mock mode”, click Analyze
   - If it errors, show how it clearly falls back to mock and informs the user.

## 1:30–2:15 Architecture
- Switch to repo page and open `Architecture diagram/Architecture diagram.png`
- Explain: API Gateway → Lambda → Bedrock Agent → Action Group → Ingest Lambda → Open‑Meteo & S3
- Multi‑agent inside app: Supervisor (Bedrock), Data Ingestion, Risk Analysis (Nova Pro), Alert Generation

## 2:15–2:45 Impact & Differentiation
- "Reasoning LLM provides transparent decision-making, not just retrieval."
- "Autonomous: no human in the loop required."
- "Real impact: reduces maritime risk; accessible and scalable (serverless)."

## 2:45–3:00 Close
- Show SUBMISSION.md briefly (requirements checklist is green). 
- "Code and docs in GitHub (README, QUICKSTART, DEPLOYMENT)."
- "Thanks for watching!"

## Optional B‑roll (pre-capture)
- Local FastAPI `/docs` page
- Terminal calling `POST /query` and showing JSON response
- CloudFormation stack outputs / Agent PREPARED status in console
