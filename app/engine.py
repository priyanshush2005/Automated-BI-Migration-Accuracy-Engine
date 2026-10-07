"""The pipeline: dependencies -> translate -> validate -> visual -> confidence."""
import re

from .confidence import score_confidence
from .dependency import resolve_dependencies
from .translator import translate
from .validator import compare_existing, self_check
from .visual_mapper import map_visual


def pick_dimension(visual, formulas):
    """Table calcs need an ordering dimension. Use the visual's last dimension;
    otherwise guess from a FIXED clause; otherwise default to the first column."""
    if visual.get("dimensions"):
        return visual["dimensions"][-1], None
    m = re.search(r"FIXED\s+\[(\w+)\]", " ".join(formulas))
    if m:
        return m.group(1), f"no visual given: used FIXED dimension '{m.group(1)}'"
    return "Region", "no visual given: assumed dimension 'Region'"


def migrate(calcs, target, existing_dax, visual, table, columns):
    order = resolve_dependencies(calcs)
    formulas = {c["name"]: c["formula"] for c in calcs}
    dim, dim_note = pick_dimension(visual, formulas.values())

    translated, notes = {}, []
    for name in order:                                   # dependencies first
        translated[name], n = translate(formulas[name], table, columns, set(formulas), dim)
        notes += n
    if dim_note and any(k in " ".join(formulas.values()) for k in ("WINDOW_", "RUNNING_", "RANK(")):
        notes.append(dim_note)
    notes = list(dict.fromkeys(notes))                   # remove duplicates

    predicted = translated[target]
    problems = self_check(predicted, table, columns, set(formulas))
    vis = map_visual(visual)

    is_corrected, why = False, []
    if existing_dax:
        ok, why = compare_existing(formulas[target], existing_dax, predicted, table)
        is_corrected = not ok

    score, level, reasons = score_confidence(True, problems, vis, bool(existing_dax), notes)
    return {
        "predicted_dax": predicted,
        "visual_mapping": vis,
        "confidence_score": score,
        "is_corrected": is_corrected,
        "confidence_level": level,
        "confidence_reasons": reasons,
        "problems_in_existing_dax": why,
        "supporting_measures": {k: v for k, v in translated.items() if k != target},
    }
