"""Topic scan for Afterclap (see research/TOPIC-RESEARCH-2026-10-14.md).

  python3 -I topic_scan.py suggest "why are pencils" "why is ketchup"
      -> YouTube autocomplete (ranked suggestions, no volumes)
  python3 -I topic_scan.py search "why are pencils yellow"
      -> top YouTube search results: videos (title | channel | views | length | age) and Shorts (title, views)

Light manual use only (a few dozen queries a week). Scrapes public HTML, so it can break
when YouTube changes its page; the compliant fallback is YouTube Data API v3 search.list.
"""
import sys, json, re, subprocess, urllib.parse

def curl(url):
    return subprocess.run(["curl", "-sS", "-m", "20", "-A", "Mozilla/5.0",
                           "-H", "Accept-Language: en-US", url],
                          capture_output=True, text=True).stdout

def suggest(q):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q="
           + urllib.parse.quote(q))
    try:
        return json.loads(curl(url))[1]
    except Exception:
        return []

def walk(o, out):
    if isinstance(o, dict):
        if "videoRenderer" in o:
            v = o["videoRenderer"]
            out.append(("V",
                        "".join(r.get("text", "") for r in v.get("title", {}).get("runs", [])),
                        "".join(r.get("text", "") for r in v.get("ownerText", {}).get("runs", [])),
                        v.get("viewCountText", {}).get("simpleText", ""),
                        v.get("lengthText", {}).get("simpleText", ""),
                        v.get("publishedTimeText", {}).get("simpleText", "")))
        elif "shortsLockupViewModel" in o:
            out.append(("S", o["shortsLockupViewModel"].get("accessibilityText", "")))
        for v in o.values():
            walk(v, out)
    elif isinstance(o, list):
        for x in o:
            walk(x, out)

def search(q, n=9):
    h = curl("https://www.youtube.com/results?search_query=" + urllib.parse.quote(q))
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", h, re.S)
    out = []
    if m:
        walk(json.loads(m.group(1)), out)
    seen, rows = set(), []
    for r in out:
        if r[1][:80] in seen:
            continue
        seen.add(r[1][:80])
        rows.append(r)
    return rows[:n]

if __name__ == "__main__":
    mode, qs = sys.argv[1], sys.argv[2:]
    for q in qs:
        print("##", q)
        if mode == "suggest":
            print("  " + " | ".join(suggest(q)))
        else:
            for r in search(q):
                print("  " + " | ".join(r)[:170])
