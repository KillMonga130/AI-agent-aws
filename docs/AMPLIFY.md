# Deploy the Demo on AWS Amplify (5 minutes)

This guide deploys the static demo in the `web/` folder to AWS Amplify Hosting.

## Prerequisites
- GitHub repo is public: https://github.com/KillMonga130/AI-agent-aws
- AWS account with Amplify Hosting enabled

## Steps

1) Connect repository
- Open AWS Console → Amplify → Hosting → Get started → "Connect app"
- Pick GitHub → authorize → select repo `AI-agent-aws` and branch `main`

2) Build settings
- Framework preset: "Static HTML"
- Build settings: leave default (no build step)
- Artifact (build) directory: set to `web`

3) Save and deploy
- Click "Save and deploy"
- First build takes ~1–2 minutes

4) Test the site
- Visit the provided Amplify domain, e.g. `https://main.<id>.amplifyapp.com`
- The page auto-loads mock data
- Optional: Enter your API Gateway URL in the "API endpoint" box and uncheck "Use mock data" to try live calls (if enabled)

5) (Optional) Preconfigure API endpoint
If you want the page to default to your API endpoint, add a rewrite variable:
- In the Amplify app → Rewrites and redirects → Add rule:
  - Source: `/api-endpoint` → Target: N/A (use for env var)
Or, simpler: append `?endpoint=<YOUR_API_URL>` to the site URL, e.g.
```
https://main.<id>.amplifyapp.com/?endpoint=https%3A%2F%2Faaabp3bu9h.execute-api.us-east-1.amazonaws.com%2FProd
```

## Notes
- The Bedrock Agent API may be blocked at the account level. The demo uses mock data by default and gracefully falls back to it when the API isn’t reachable.
- The architecture diagram is included in the repo under `Architecture diagram/`.
- You can customize text and styling in `web/index.html` and `web/styles.css`.
