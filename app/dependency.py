"""Step 2 - decide the order to translate calculations.
If B uses [A], A must be translated first (a topological sort)."""
import re


def resolve_dependencies(calcs):
    formulas = {c["name"]: c["formula"] for c in calcs}
    order, done = [], set()

    def visit(name, path=()):
        if name in done:
            return
        if name in path:
            raise ValueError(f"Circular dependency: {' -> '.join(path + (name,))}")
        for ref in re.findall(r"\[([^\]]+)\]", formulas[name]):
            if ref in formulas:          # a reference to another calculation
                visit(ref, path + (name,))
        done.add(name)
        order.append(name)

    for name in formulas:
        visit(name)
    return order
