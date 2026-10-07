"""Step 3 - translate one Tableau formula into DAX using simple rules.
Each rule is a small function so it is easy to explain."""
import re

AGG = {"SUM": "SUM", "AVG": "AVERAGE", "MIN": "MIN", "MAX": "MAX",
       "COUNT": "COUNT", "COUNTD": "DISTINCTCOUNT"}


def find_call(text, name):
    """Find NAME( ... ) even when it contains nested brackets. Returns (start, end, inside)."""
    m = re.search(rf"\b{name}\(", text)
    if not m:
        return None
    depth = 0
    for i in range(m.end() - 1, len(text)):
        depth += (text[i] == "(") - (text[i] == ")")
        if depth == 0:
            return m.start(), i + 1, text[m.end():i]


def rule_aggregations(f, table):
    # SUM([Sales]) -> SUM(Table[Sales])
    return re.sub(r"\b(SUM|AVG|MIN|MAX|COUNTD|COUNT)\(\[(\w+)\]\)",
                  lambda m: f"{AGG[m.group(1)]}({table}[{m.group(2)}])", f)


def rule_fixed_lod(f, table):
    # {FIXED [Region] : expr} -> CALCULATE(expr, ALLEXCEPT(Table, Table[Region]))
    def convert(m):
        dims = ", ".join(f"{table}[{d}]" for d in re.findall(r"\[(\w+)\]", m.group(1)))
        return f"CALCULATE({m.group(2).strip()}, ALLEXCEPT({table}, {dims}))"
    return re.sub(r"\{FIXED\s+([^:]+):\s*([^}]+)\}", convert, f)


def rule_table_calcs(f, table, dim, notes):
    """WINDOW_SUM / RUNNING_SUM / RANK depend on an ordering dimension, which Tableau
    stores in the view. We are told it (or guess it) and record that as an assumption."""
    col = f"{table}[{dim}]"
    shapes = {
        "WINDOW_SUM": "CALCULATE({e}, ALLSELECTED(" + col + "))",
        "RUNNING_SUM": "CALCULATE({e}, FILTER(ALLSELECTED(" + col + "), " + col + " <= MAX(" + col + ")))",
        "RANK": "RANKX(ALLSELECTED(" + col + "), CALCULATE({e}), , DESC)",
    }
    for name, shape in shapes.items():
        while (hit := find_call(f, name)):
            start, end, inside = hit
            f = f[:start] + shape.format(e=inside) + f[end:]
            notes.append(f"{name} assumed to run along '{dim}'")
    return f


def rule_division(f, table):
    # a / b -> DIVIDE(a, b)   (DIVIDE returns blank instead of an error when b = 0)
    operand = rf"(?:\w+\({table}\[\w+\]\)|\[\w+\])"
    return re.sub(rf"({operand})\s*/\s*({operand})", r"DIVIDE(\1, \2)", f)


def rule_if(f):
    # IF cond THEN a ELSE b END -> IF(cond, a, b)
    f = re.sub(r"\bIF\s+(.*?)\s+THEN\s+(.*)\s+ELSE\s+(.*)\s+END\b", r"IF(\1, \2, \3)", f, flags=re.S)
    f = f.replace(" AND ", " && ").replace(" OR ", " || ")
    return re.sub(r"'([^']*)'", r'"\1"', f)       # 'High' -> "High"


def rule_fields(f, table, columns, calc_names, notes):
    # leftover [X]: another calculation -> measure reference, a column -> SELECTEDVALUE
    def convert(m):
        name = m.group(1)
        if name in calc_names:
            return f"[{name}]"
        if name in columns:
            return f"SELECTEDVALUE({table}[{name}])"
        notes.append(f"unknown field [{name}]")
        return m.group(0)
    return re.sub(r"(?<![\w\]])\[([^\]]+)\]", convert, f)


def translate(formula, table, columns, calc_names, dim):
    """Returns (dax, notes). notes = assumptions made, used to lower confidence."""
    notes = []
    f = formula.strip()
    f = rule_aggregations(f, table)
    f = rule_fixed_lod(f, table)
    f = rule_table_calcs(f, table, dim, notes)
    f = rule_division(f, table)
    f = rule_if(f)
    f = rule_fields(f, table, columns, calc_names, notes)
    return f, notes
