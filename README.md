# AI Compass

AI-assisted enterprise AI use case intake, risk triage, and governance recommendation tool. Describe a proposed AI use case, get a structured risk assessment, evaluation plan, and governance decision back.

## What it does

AI Compass takes a business AI use case — the problem, the proposed tool, data sensitivity, who's affected — and generates:

- **Risk assessment** across 7 categories: privacy, security, hallucination/reliability, bias/fairness, vendor dependency, cost exposure, and human oversight requirements
- **Evaluation plan** — test cases, success metrics, acceptance thresholds, red-team scenarios, and a UAT checklist
- **Governance decision** — approve, approve with controls, pilot only, reject, or escalate for Legal/Security review, with rationale and conditions
- **Downloadable evidence pack** — a Word document capturing the full assessment for audit purposes

## Why it exists

Enterprises adopting AI tools need a structured intake and governance process, but early-stage teams often improvise ad hoc reviews with no consistent criteria or audit trail. AI Compass applies the same structured reasoning a Responsible AI or Digital Risk review board would — risk triage, evaluation design, governance decisioning — and turns it into a repeatable, documented process in seconds rather than a multi-week manual review.

## Demo

![AI Compass intake form](static/screenshots/input.png)
![AI Compass governance decision](static/screenshots/results1.png)
![AI Compass risk assessment](static/screenshots/results2.png)
![AI Compass evaluation plan](static/screenshots/results3.png)

## Tech stack

- **Python / Flask** — web framework
- **Anthropic Claude API** — structured risk/governance analysis (claude-sonnet-5)
- **python-docx** — generates the downloadable Word evidence pack
- **Jinja2** — templating
- **HTML / CSS** — dark, clean UI

## Getting started

**1. Clone the repo**
```bash
git clone https://github.com/SWBDevHub/AI-Compass.git
cd AI-Compass
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key**

Create a `.env` file in the root:
```
ANTHROPIC_API_KEY=your_key_here
```

Get a key at [console.anthropic.com](https://console.anthropic.com)

**4. Run**
```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser. Click "Load demo scenario" for a ready-made example.

## Project structure

```
aicompass/
├── app.py                       # Flask routes, in-memory evaluation store
├── services/
│   ├── compass_service.py       # Claude API call, structured JSON prompt/parsing
│   └── docx_service.py          # Word evidence pack generation
├── templates/
│   ├── index.html               # Intake form
│   └── results.html             # Risk assessment, evaluation plan, governance decision
├── static/
│   └── style.css                # Dark UI styling
└── requirements.txt
```

## Skills demonstrated

- AI governance workflow design — intake, risk triage, evaluation planning, decisioning
- Structured prompt engineering — a single enforced JSON schema spanning three interdependent output sections
- Enterprise AI risk framing — privacy, security, reliability, bias/fairness, vendor dependency, cost, human oversight
- API integration — Anthropic Claude API
- Full-stack Python — Flask, Jinja2, REST routing, server-side state management without a database
- Document generation — python-docx for audit-ready evidence packs, built and streamed entirely in memory
- Responsible AI / audit evidence practices aligned with frameworks like NIST CSF 2.0 and ISO 27001

## Limitations & future work

This is a v0.1 prototype built for portfolio and learning purposes. It uses an in-memory store rather than a database, so evaluations are lost on server restart — an accepted scope tradeoff, not a bug.

Planned additions:
- SQLite persistence and a dashboard (approved / pending / high-risk use cases)
- Live multi-model comparison rather than a single-model analysis
- PDF export as an alternative to the Word evidence pack
- Multi-user roles and an approval history / audit trail

## Disclaimer

AI Compass produces AI-assisted governance recommendations. All outputs should be reviewed by qualified Legal, Security, and Compliance stakeholders before any approval, pilot, or rejection decision is acted on. Not a substitute for a formal AI governance process.
