"""Step 5 - Tableau visual type -> Power BI visual (simple lookup)."""
VISUALS = {
    "bar": "clustered column chart", "line": "line chart", "area": "area chart",
    "pie": "pie chart", "scatter": "scatter chart", "text": "table",
    "table": "table", "map": "map", "heatmap": "matrix", "kpi": "card",
}


def map_visual(visual):
    kind = str(visual.get("tableau_visual") or visual.get("visual_type") or "").lower()
    if not kind:
        return "no visual provided"
    return VISUALS.get(kind, "needs manual review")
