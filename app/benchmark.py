"""Step 7 - before vs after accuracy against the ground truth."""
from .validator import normalize


def run_benchmark(cases):
    """cases: [{id, existing, predicted, truth}]"""
    rows, before, after, usable = [], 0, 0, 0
    for c in cases:
        if "..." in c["truth"]:                          # truth is a placeholder, cannot grade
            rows.append({**c, "before": None, "after": None, "note": "ground truth incomplete"})
            continue
        b = normalize(c["existing"]) == normalize(c["truth"])
        a = normalize(c["predicted"]) == normalize(c["truth"])
        usable += 1
        before += b
        after += a
        rows.append({**c, "before": b, "after": a, "note": ""})
    return rows, {"graded": usable, "before_correct": before, "after_correct": after}
