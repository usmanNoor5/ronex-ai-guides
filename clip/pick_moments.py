#!/usr/bin/env python3
"""Step 2: propose candidate moments from a transcript.

Splits the transcript into sentences, slides a window of sentences whose length
is close to --length seconds, scores each window with simple heuristics
(numbers, questions, emphasis words, speaking pace), and prints the best
non-overlapping ones. It is a shortlist: review every candidate yourself
(or with an AI assistant) before cutting.

Usage: python pick_moments.py transcript.json --length 30 --top 5 [--out moments.json]
"""
import argparse, json, re

EMPHASIS = {"never", "always", "mistake", "secret", "problem", "important", "stop",
            "actually", "biggest", "best", "worst", "why", "how", "first", "key",
            "wrong", "surprising", "nobody", "everyone", "free", "new"}


def sentences(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[.?!]$", w["w"].strip()):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def score(ws):
    txt = " ".join(w["w"].strip() for w in ws)
    low = [re.sub(r"\W", "", w["w"].lower()) for w in ws]
    dur = ws[-1]["e"] - ws[0]["s"]
    s = 2.0 * sum(c.isdigit() for c in txt) / max(len(txt), 1) * 10
    s += 1.5 * txt.count("?")
    s += 1.0 * sum(t in EMPHASIS for t in low)
    pace = len(ws) / max(dur, 1)
    s += 1.0 if 2.2 <= pace <= 3.6 else 0
    return round(s, 2), txt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--length", type=float, default=30, help="target seconds")
    ap.add_argument("--tol", type=float, default=0.25, help="allowed +/- fraction")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--out")
    a = ap.parse_args()

    words = json.load(open(a.transcript))["words"]
    sents = sentences(words)
    cands = []
    for i in range(len(sents)):
        ws = []
        for j in range(i, len(sents)):
            ws += sents[j]
            dur = ws[-1]["e"] - ws[0]["s"]
            if dur > a.length * (1 + a.tol):
                break
            if dur >= a.length * (1 - a.tol):
                sc, txt = score(ws)
                cands.append({"start": ws[0]["s"], "end": ws[-1]["e"], "score": sc, "text": txt})
    cands.sort(key=lambda c: -c["score"])
    picked = []
    for c in cands:
        if all(c["end"] <= p["start"] or c["start"] >= p["end"] for p in picked):
            picked.append(c)
        if len(picked) == a.top:
            break
    for n, c in enumerate(picked, 1):
        print(f"#{n} {c['start']:.2f}-{c['end']:.2f} score={c['score']}  {c['text'][:110]}")
    if a.out:
        json.dump(picked, open(a.out, "w"), indent=2)


if __name__ == "__main__":
    main()
