"""Run:  python3 main.py        (reads the files in ./data, writes output.json)"""
import json
from app.parser import load_csv_columns, load_json, load_xml_calculations
from app.engine import migrate
from app.benchmark import run_benchmark

D = "data/"
TABLE = "Table"
columns = load_csv_columns(D + "sample_data.csv")
calcs = load_json(D + "tableau_calculations.json")
deps = load_json(D + "tableau_dependencies.json")
existing = {x["id"]: x["dax"] for x in load_json(D + "incorrect_dax.json")}
truth = {x["id"]: x["dax"] for x in load_json(D + "ground_truth.json")}
visuals = load_json(D + "visuals.json")
visual_of = {m: v for v in visuals for m in v["measures"]}

outputs, bench_cases = {}, []

# 1) the four calculations with existing DAX
for c in calcs:
    r = migrate([c], c["name"], existing[c["id"]], visual_of.get(c["name"], {}), TABLE, columns)
    outputs[c["id"]] = r
    bench_cases.append({"id": c["id"], "existing": existing[c["id"]],
                        "predicted": r["predicted_dax"], "truth": truth[c["id"]]})

# 2) multi-step dependency chain (Step1 -> Step2 -> FinalMetric)
outputs["dependencies"] = migrate(deps, "FinalMetric", None, {}, TABLE, columns)

# 3) calculations coming from the Tableau XML
for x in load_xml_calculations(D + "tableau_xml.xml"):
    outputs["xml:" + x["name"]] = migrate([x], x["name"], None, visual_of.get(x["name"], {}), TABLE, columns)

for key, r in outputs.items():
    print(f"\n== {key}  [{r['confidence_level']} {r['confidence_score']}]  corrected={r['is_corrected']}")
    print("   DAX    :", r["predicted_dax"])
    print("   visual :", r["visual_mapping"])
    for s, d in r["supporting_measures"].items():
        print(f"   needs  : [{s}] = {d}")
    for w in r["problems_in_existing_dax"]:
        print("   existing DAX problem:", w)

rows, summary = run_benchmark(bench_cases)
print("\n=== BEFORE vs AFTER (graded against ground_truth.json) ===")
for r in rows:
    print(f"{r['id']}: before={r['before']}  after={r['after']}  {r['note']}")
print(summary)

json.dump({"results": outputs, "benchmark": summary}, open("output.json", "w"), indent=2)
