---
name: jobinja-apply
description: Automate job hunting on jobinja.ir with a "backdoor" outreach strategy — search AI/Data (or any) jobs, extract full job + company intel, find the company's LinkedIn page, hiring managers, and website, then draft a tailored outreach message/cover letter per job. Use whenever the user mentions jobinja, job hunting, applying to jobs, job search automation, finding AI/data jobs in Iran, or reaching out to companies/recruiters about a position.
---

# jobinja-apply

Find jobs on jobinja.ir and build a **backdoor application package** for each one:
instead of clicking jobinja's apply button, reach the company directly — LinkedIn
page, hiring manager/HR contacts, company website, email — with a tailored message.

## Prerequisites

Ask the user once per session (if not already known from memory/context):
- Their target keywords if not given (default: AI/ML/Data — run several searches:
  "machine learning", "هوش مصنوعی", "data scientist", "python", "deep learning", "داده")
- A short profile: current role, years of experience, key skills, notable projects.
  This feeds the tailored messages. If a resume file exists in the project, read it instead.

## Workflow

Run the bundled scraper (stdlib-only, no install needed):

```bash
SKILL_DIR=<this skill's directory>
python3 $SKILL_DIR/scripts/jobinja.py search "machine learning"          # list jobs (20/page)
python3 $SKILL_DIR/scripts/jobinja.py search "machine learning" --page 2
python3 $SKILL_DIR/scripts/jobinja.py job <job_url>                      # full details via JSON-LD
python3 $SKILL_DIR/scripts/jobinja.py company <company_url>              # name, website, size, about
```

All output is JSON. Notes:
- `job` returns title, full description, salary (`baseSalary`, IRT/month), `datePosted`,
  location, and `hiringOrganization.sameAs` = **the company's official website** — the
  backdoor seed. Persian text is normal; titles mix Persian/English.
- Occasional TLS drops from jobinja are normal; the script retries once. If a call
  still fails, wait a couple of seconds and rerun.
- Be polite: ~1 request/second, don't crawl more pages than needed.

### Per job, do this

1. **Fetch details** with `job <url>`. Skip jobs that clearly don't match the user's
   profile (wrong domain, gender-restricted ads, on-site in a city the user excluded).
2. **Enrich the company** — in parallel where possible:
   - `company <company_url>` for size/about/website.
   - WebSearch: `<company name> site:linkedin.com/company` and
     `<company English name> linkedin` to find the LinkedIn company page.
   - WebSearch: `<company name> (CTO OR "engineering manager" OR "HR" OR recruiter) linkedin`
     to find 1–3 real people to contact. Prefer engineering leads over generic HR for
     technical roles.
   - WebFetch the company website's contact/about/careers page for an email address.
3. **Draft the outreach package** (see format below): a LinkedIn connection note
   (≤300 chars, LinkedIn's limit), a longer LinkedIn/email message, and a short
   cover letter — each tailored to THIS job's requirements and the user's actual
   matching skills. Write in the language of the job ad (Persian ad → Persian message,
   unless user prefers English). Never invent experience the user doesn't have.
4. **Present the package and pause — human in the loop, always.** Show the full
   package and ask: send email / skip / adjust. LinkedIn messages the user always
   sends themselves (automation there = account risk + ToS violation).

### Sending email (only after explicit user approval)

Requires one-time setup by the user: 2-Step Verification on their Google account,
then an app password from https://myaccount.google.com/apppasswords, exported as:

```bash
export GMAIL_ADDRESS="you@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

If these env vars are missing, tell the user how to set them up — don't hunt for
credentials elsewhere.

The approval gate is strict: show the user the **exact final text, recipient, and
subject**, and send only after they explicitly confirm *that* email. "Apply to all"
from earlier does not count — confirm each send. Then:

```bash
echo "<final body>" > /tmp/body.txt   # or Write the file
python3 $SKILL_DIR/scripts/jobinja.py email "person@company.com" \
  "Application: {Job title} — {User name}" /tmp/body.txt --attach resume.pdf
```

Keep it deliverable: plain text, at most one link, PDF resume attached, subject
naming the actual role. Space sends out — a few per day, never bursts. Only send
to addresses actually found, never guessed ones (bounces damage sender reputation).
Record each send in `jobinja-applied.md`.

### Output format per job

```markdown
## [N]. {Job title} — {Company}
- **Link**: {jobinja url} | **Posted**: {date} | **Salary**: {if listed}
- **Location/Type**: ... | **Company**: {size}, {one-line about}, {website}
- **Fit**: 2-3 lines on why this matches (or doesn't) the user's profile
- **Backdoor contacts**:
  - LinkedIn company: {url or "not found"}
  - People: {name — title — linkedin url}, ...
  - Email: {found address or "not found"}
### Connection note (≤300 chars)
### Full message / email
### Cover letter (short)
```

Track processed jobs in `jobinja-applied.md` in the working directory (job url, date,
status: emailed/contacted/skipped) so reruns resume instead of repeating — check it first.

## What NOT to do

- Never send an email without showing the final text + recipient and getting an
  explicit yes for that specific email.
- Don't log into jobinja or LinkedIn, don't scrape LinkedIn directly (use WebSearch),
  don't automate LinkedIn messaging.
- Don't fabricate contacts — a "not found" is better than a guessed email.
