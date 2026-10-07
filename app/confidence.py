"""Step 6 - confidence score with human-readable reasons.
Start from points for what went well, subtract for assumptions."""


def score_confidence(deps_ok, self_check_problems, visual, existing_checked, notes):
    score, reasons = 0.0, []
    if deps_ok:
        score += 0.25
        reasons.append("dependencies resolved (+0.25)")
    if not self_check_problems:
        score += 0.45
        reasons.append("DAX passed syntax/column self-check (+0.45)")
    else:
        reasons.append("self-check failed: " + "; ".join(self_check_problems))
    if visual not in ("needs manual review", "no visual provided"):
        score += 0.10
        reasons.append("visual type recognised (+0.10)")
    if existing_checked:
        score += 0.10
        reasons.append("compared against existing DAX (+0.10)")
    for n in notes:
        score -= 0.10
        reasons.append(f"assumption: {n} (-0.10)")
    score = round(max(0.0, min(1.0, score)), 2)
    level = "HIGH" if score >= 0.80 else "MEDIUM" if score >= 0.60 else "LOW"
    return score, level, reasons
