"""Step 1 - read the input files (JSON, XML, CSV)."""
import csv
import io
import json
import xml.etree.ElementTree as ET


def read_clean(path):
    """Your files were saved with every line wrapped in quotes and inner quotes
    doubled (""). This undoes that, so normal parsers can read them."""
    lines = []
    for line in open(path, encoding="utf-8-sig").read().splitlines():
        line = line.rstrip()
        if len(line) >= 2 and line[0] == '"' and line[-1] == '"':
            line = line[1:-1].replace('""', '"')
        lines.append(line)
    return "\n".join(lines)


def load_json(path):
    return json.loads(read_clean(path))


def load_xml_calculations(path):
    """Return [{'name':..., 'formula':...}] from <calculation .../> tags."""
    root = ET.fromstring(read_clean(path))
    return [{"name": n.attrib.get("name", "XML_CALC"), "formula": n.attrib["formula"]}
            for n in root.iter("calculation")]


def load_csv_columns(path):
    """Column names of the sample data (so we know which [Fields] are real columns)."""
    return list(csv.DictReader(io.StringIO(read_clean(path))).fieldnames)
