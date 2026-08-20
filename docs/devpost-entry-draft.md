# Devpost entry draft — do not submit without entrant approval

## Project name

Homeowner Quote Clarity Agent

## Tagline

Evidence-linked comparison of mismatched home-repair quotes without ranking contractors.

## Category

The Taskmaster

## Inspiration

Homeowners frequently receive quotations that appear comparable but use different tax bases, allowances, exclusions, schedules, and warranty language. The difficult work is not generating more prose; it is preserving what each contractor actually stated, exposing what is missing, and producing neutral questions without inventing certainty.

## What it does

The current local prototype runs a deterministic offline workflow over three original fictional repair quotations and one adversarial attachment. It inventories the evidence, creates a source-linked structured record, normalizes comparable scope categories, preserves allowances and unknowns, identifies omissions, quarantines a simulated prompt-injection instruction, and produces a comparison plus contractor-specific clarification questions.

It deliberately does not rank contractors, judge price fairness, assess legal or technical compliance, send messages, sign anything, or make payments.

## How we built it

We first built a deterministic Python evidence engine so quoted totals, tax basis, scope states, and source anchors remain authoritative. Google ADK 2.1.0 coordinator and sub-agent definitions plus a private FastAPI demonstration endpoint are prepared for the required Gemini and Cloud Run verification:

1. the manifest agent verifies that only bundled fictional fixtures are used;
2. the evidence agent invokes a deterministic source-linked comparison engine; and
3. the safety agent verifies evidence presence, injection quarantine, and non-decision boundaries.

The ADK tree and an in-memory session initialize locally without a model call. Gemini execution and Cloud Run deployment have not yet been performed or verified. Each deterministic fact includes a source filename, line number, and SHA-256 excerpt hash.

## Technologies used

- Google Agent Development Kit 2.1.0 — local definitions and initialization only
- Python 3.12
- FastAPI and Uvicorn
- deterministic Python evidence and validation layer

Planned and required integrations, pending verification: Gemini 3.5 Flash and Google Cloud Run.

## Data sources

Only four original fictional text fixtures bundled in the repository. No real homeowner, contractor, address, quotation, or customer information is used. No web data source is accessed by the agent.

## Challenges

The central challenge was keeping the model useful without allowing it to become the source of truth. We separated orchestration and bounded summarization from deterministic extraction, made unknowns first-class, and treated document text as untrusted evidence. We also designed the public demo to accept no arbitrary uploads or URLs.

## Accomplishments

- byte-deterministic report generation;
- traceable evidence hashes for every stated fact;
- explicit handling of VAT basis, allowances, options, exclusions, and unknowns;
- prompt-injection quarantine that does not reproduce the malicious instruction;
- ADK agent definitions and an initialization smoke test without a model call; and
- a private Cloud Run deployment configuration with an explicit model-run gate and scale-to-zero target.

## What we learned

Agentic systems are more trustworthy when model responsibilities are narrower, evidence contracts are typed, and failure is visible. A useful homeowner tool should make uncertainty easier to act on, not hide it behind a recommendation.

## What's next

After the competition, any real-data pilot would require a separate privacy and security review, authenticated uploads, retention controls, stronger model evaluation, and jurisdiction-specific professional boundaries. Those features are intentionally outside this synthetic demonstration.

## Disclosure

This project was implemented during the contest period with AI-assisted research, coding, testing, documentation, and browser assistance. Two local planning documents informed the requirements and architecture. A separate synthetic construction-closeout demonstration influenced the emphasis on evidence labels, but its code, prompts, fixtures, branding, and outputs were not incorporated. All competition fixtures are original and fictional.

## Links still required

- Public repository URL: https://github.com/Andrew-JS19/homeowner-quote-clarity-agent
- Hosted Cloud Run URL or deployment proof: blocked until approved event credits are visibly active
- Architecture image: `docs/architecture-devpost.png`
- Demo video URL: local private-review draft complete; public upload pending entrant approval
