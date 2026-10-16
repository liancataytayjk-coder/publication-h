"""Check references against Crossref before citing them.

Usage:
  python crossref_check.py "Rice prices and income distribution in Thailand" "The economic effects of energy price shocks"
  python crossref_check.py --bib paper/references.bib     # checks every title in a .bib file

Prints the top matches (title, authors, journal, volume(issue), pages, year, DOI)
so you can compare them with the citation. Flag any reference with no match in
the .bib `note` field and in the submission checklist; never invent details.
"""

import re
import sys
import time
import urllib.parse

import requests


def lookup(q, rows=2):
    url = "https://api.crossref.org/works?rows=%d&query.bibliographic=%s" % (rows, urllib.parse.quote(q))
    r = requests.get(url, timeout=30, headers={"User-Agent": "reference-check (mailto:none@example.org)"})
    r.raise_for_status()
    for it in r.json()["message"]["items"]:
        authors = ", ".join(a.get("family", "?") for a in it.get("author", [])[:5])
        year = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        print(f"  - {(it.get('title') or ['?'])[0]} | {authors} | {(it.get('container-title') or [''])[0]} "
              f"{it.get('volume', '')}({it.get('issue', '')}) {it.get('page', '')} | {year} | doi:{it.get('DOI')}")


def main(argv):
    if argv[:1] == ["--bib"]:
        titles = re.findall(r"^\s*title\s*=\s*[{\"](.+?)[}\"],?\s*$", open(argv[1]).read(), flags=re.M)
    else:
        titles = argv
    for t in titles:
        t = re.sub(r"[{}\\]", "", t)
        print(t)
        try:
            lookup(t)
        except Exception as e:  # noqa: BLE001
            print("  ! lookup failed:", e)
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
