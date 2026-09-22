"""Summarize client-produced JSONL. No interpolation; nearest-rank percentile."""
import argparse
import json
import math
from pathlib import Path

def percentile(values, p):
    if not values or not 0 < p <= 100:
        raise ValueError("non-empty values and 0 < p <= 100 required")
    values = sorted(values)
    return values[max(0, math.ceil(p/100*len(values))-1)]

def summarize(rows):
    if not rows:
        raise ValueError("empty input")
    accepted = [r for r in rows if r.get("accepted") is True]
    out = {"records": len(rows), "accepted_records": len(accepted)}
    for key in ("accept_latency_ms","completion_ms"):
        vals=[float(r[key]) for r in accepted if key in r]
        if vals:
            out[key]={"n":len(vals),"p50":percentile(vals,50),
                      "p95":percentile(vals,95),"p99":percentile(vals,99),
                      "max":max(vals)}
    out["success_records"]=sum(r.get("success") is True for r in rows)
    out["warning"]="Rejected/unknown attempts absent unless separately recorded."
    return out

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("jsonl",type=Path)
    args=parser.parse_args()
    rows=[json.loads(line) for line in args.jsonl.read_text().splitlines() if line.strip()]
    print(json.dumps(summarize(rows),indent=2))
