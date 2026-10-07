"""Step 4 - check DAX.
 (a) self_check: is OUR output well-formed?
 (b) compare_existing: what is wrong with the EXISTING conversion?"""
import re


def normalize(dax):
    """Ignore spaces/case and the Table[...] qualifier so styles can be compared."""
    dax = re.sub(r"\s+", "", dax.upper())
    dax = dax.replace("AVERAGE(", "AVG(")
    return re.sub(r"[A-Z_]+\[(\w+)\]", r"\1", dax)


def self_check(dax, table, columns, calc_names):
    problems = []
    if dax.count("(") != dax.count(")"):
        problems.append("unbalanced parentheses")
    if "{" in dax or re.search(r"\b(WINDOW_|RUNNING_|FIXED)", dax):
        problems.append("untranslated Tableau syntax left")
    for col in re.findall(rf"{table}\[(\w+)\]", dax):
        if col not in columns:
            problems.append(f"column {col} not in data")
    return problems


def compare_existing(source, existing, predicted, table):
    """Returns (is_correct, [reasons])."""
    if normalize(existing) == normalize(predicted):
        return True, []
    why = []
    if re.search(r"\b(SUM|AVERAGE|MIN|MAX|COUNT)\((?!%s\[)" % table, existing):
        why.append(f"columns are not qualified (use {table}[Column])")
    if re.search(r"\bAVG\(", existing):
        why.append("AVG is not a DAX function (use AVERAGE)")
    m1 = re.search(r"SUM\(\[(\w+)\]\)\s*/\s*SUM\(\[(\w+)\]\)", source)
    m2 = re.search(r"SUM\((?:\w+\[)?(\w+)\]?\)\s*/\s*SUM\((?:\w+\[)?(\w+)\]?\)", existing)
    if m1 and m2 and m1.groups() == m2.groups()[::-1]:
        why.append("numerator and denominator are swapped")
    if "FIXED" in source and "ALLEXCEPT" not in existing:
        why.append("FIXED LOD ignored (needs CALCULATE + ALLEXCEPT)")
    if re.search(r"WINDOW_|RUNNING_|RANK\(", source) and "ALLSELECTED" not in existing:
        why.append("table calculation ignored (needs ALLSELECTED)")
    if "'" in source and '"' not in existing:
        why.append("returns numbers instead of the text labels")
    if not why:
        why.append("does not match the translated Tableau logic")
    return False, why
