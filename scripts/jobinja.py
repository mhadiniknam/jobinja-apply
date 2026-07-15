#!/usr/bin/env python3
"""Scrape jobinja.ir job listings, job details, and company pages. Stdlib only.

Usage:
  jobinja.py search "machine learning" [--page N]   # list jobs for keyword
  jobinja.py job <job_url>                          # job details (JSON-LD)
  jobinja.py company <company_url>                  # company name/site/size
  jobinja.py email <to> <subject> <body_file> [--attach cv.pdf]
      # send via Gmail SMTP; needs GMAIL_ADDRESS + GMAIL_APP_PASSWORD env vars
Output: JSON on stdout.
"""
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/126.0"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    # ponytail: jobinja's TLS endpoint occasionally drops connections; one retry is enough
    for attempt in (1, 2):
        try:
            return urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
        except Exception:
            if attempt == 2:
                raise


def search(keyword, page=1):
    q = urllib.parse.quote(keyword)
    url = f"https://jobinja.ir/jobs?filters%5Bkeywords%5D%5B0%5D={q}&page={page}"
    h = fetch(url)
    items = []
    for block in re.findall(
        r'class="o-listView__item .*?(?=class="o-listView__item |<footer|$)', h, re.S
    ):
        m = re.search(
            r'class="c-jobListView__titleLink"[^>]*href="([^"]+)"[^>]*>\s*(.*?)\s*</a>',
            block, re.S,
        )
        if not m:
            continue
        metas = [
            html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
            for t in re.findall(r'<li class="c-jobListView__metaItem">(.*?)</li>', block, re.S)
        ]
        job_url = html.unescape(m.group(1)).split("?")[0]
        items.append({
            "title": html.unescape(m.group(2)).strip(),
            "url": job_url,
            "company_url": job_url.split("/jobs/")[0],
            "meta": metas,  # company, location, contract type
        })
    return items


def job(url):
    h = fetch(url)
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    d = json.loads(m.group(1)) if m else {}
    d["description"] = html.unescape(re.sub(r"<[^>]+>", "\n", d.get("description", ""))).strip()
    d["url"] = url
    d["company_url"] = url.split("/jobs/")[0]
    return d


def company(url):
    h = fetch(url)
    name = re.search(r'class="c-companyHeader__name">\s*(.*?)\s*<', h, re.S)
    website = re.search(
        r'class="c-companyHeader__metaLink"[^>]*href="(?!https://jobinja)([^"]+)"', h
    )
    metas = re.findall(r'<span class="c-companyHeader__metaItem">([^<]+)</span>', h)
    about = re.search(r'<div class="o-box__text[^"]*">\s*(.*?)\s*</div>', h, re.S)
    return {
        "name": html.unescape(name.group(1)).strip() if name else None,
        "website": website.group(1) if website else None,
        "size": next((m.strip() for m in metas if "نفر" in m), None),
        "about": html.unescape(re.sub(r"<[^>]+>", " ", about.group(1))).strip()[:1500] if about else None,
        "jobinja_url": url,
    }


def email(to, subject, body_file, attach=None):
    import mimetypes
    import smtplib
    from email.message import EmailMessage

    sender = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not sender or not password:
        sys.exit("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD env vars first "
                 "(app password: https://myaccount.google.com/apppasswords)")
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = sender, to, subject
    msg.set_content(open(body_file, encoding="utf-8").read())
    if attach:
        ctype = mimetypes.guess_type(attach)[0] or "application/octet-stream"
        maintype, subtype = ctype.split("/")
        with open(attach, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype,
                               filename=os.path.basename(attach))
    # ponytail: port 587+STARTTLS, not 465 — 465 is blocked on some Iranian ISPs
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as s:
        s.starttls()
        s.login(sender, password)
        s.send_message(msg)
    return {"sent": True, "to": to, "subject": subject}


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":
        page = int(sys.argv[sys.argv.index("--page") + 1]) if "--page" in sys.argv else 1
        out = search(sys.argv[2], page)
    elif cmd == "job":
        out = job(sys.argv[2])
    elif cmd == "company":
        out = company(sys.argv[2])
    elif cmd == "email":
        attach = sys.argv[sys.argv.index("--attach") + 1] if "--attach" in sys.argv else None
        out = email(sys.argv[2], sys.argv[3], sys.argv[4], attach)
    else:
        sys.exit(__doc__)
    print(json.dumps(out, ensure_ascii=False, indent=1))
