# jobinja-apply

A [Claude Code](https://claude.com/claude-code) skill that automates job hunting on
[jobinja.ir](https://jobinja.ir) with a **backdoor outreach strategy**: instead of
clicking jobinja's apply button, it finds the company's LinkedIn page, hiring
managers, and email address, then drafts a tailored outreach package per job —
which **you** review and approve before anything is sent.

## What it does

For each matching job:

1. Scrapes the listing + full job details (title, description, salary, location)
2. Enriches the company: official website, size, LinkedIn page, 1–3 real people
   (CTO / engineering managers / HR) via web search
3. Drafts three tailored pieces: a LinkedIn connection note (≤300 chars), a full
   message/email, and a short cover letter
4. Shows you everything and pauses — **human in the loop, always**
5. On your explicit approval, sends the email via your Gmail (SMTP app password)

It never auto-sends, never guesses email addresses, never automates LinkedIn,
and logs everything to `jobinja-applied.md` so reruns resume where you left off.

## Install

```bash
git clone https://github.com/mhadiniknam/jobinja-apply ~/.claude/skills/jobinja-apply
```

Then in Claude Code: `/reload-skills` and say something like
*"find me AI jobs on jobinja"*.

## Email setup (optional, one-time)

To let the skill send approved emails through your Gmail:

1. Enable 2-Step Verification on your Google account
2. Create an app password at https://myaccount.google.com/apppasswords
3. Export both vars (e.g. in `~/.bashrc`):

```bash
export GMAIL_ADDRESS="you@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

Without these, the skill still works — it just hands you the drafts to send yourself.

## Standalone script usage

`scripts/jobinja.py` is stdlib-only Python (no installs) and works on its own:

```bash
python3 scripts/jobinja.py search "machine learning"            # list jobs (JSON)
python3 scripts/jobinja.py search "machine learning" --page 2
python3 scripts/jobinja.py job <job_url>                        # full details
python3 scripts/jobinja.py company <company_url>                # name/website/size
python3 scripts/jobinja.py email to@co.com "Subject" body.txt --attach cv.pdf
```
