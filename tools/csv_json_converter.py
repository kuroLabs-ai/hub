"""
community_hub/tools/csv_json_converter.py
Bidirectional streaming converter between CSV/TSV data and JSON/JSONL format.
Supports delimiter auto-detection, schema inspection, custom indentation, and type coercion.
"""

import os
import csv
import json
import io
from typing import Dict, Any, List, Optional, Union


def _detect_delimiter(sample: str) -> str:
    """Auto-detect delimiter (comma, tab, semicolon, pipe)."""
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample[:2048])
        return dialect.delimiter
    except Exception:
        # Fallback heuristic
        counts = {",": sample.count(","), "\t": sample.count("\t"), ";": sample.count(";"), "|": sample.count("|")}
        best = max(counts, key=counts.get)
        return best if counts[best] > 0 else ","


def _coerce_val(val: str) -> Any:
    """Attempt clean conversion of string to int, float, bool, or null."""
    v = val.strip()
    if not v:
        return None
    if v.lower() in ("true", "yes"):
        return True
    if v.lower() in ("false", "no"):
        return False
    if v.lower() in ("null", "none", "nan"):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return val


def csv_to_json(
    input_data: str,
    is_file_path: bool = False,
    output_path: Optional[str] = None,
    output_format: str = "json",  # "json" or "jsonl"
    coerce_types: bool = True
) -> Dict[str, Any]:
    """Convert CSV or TSV text/file to structured JSON/JSONL."""
    try:
        if is_file_path:
            with open(input_data, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        else:
            content = input_data

        if not content.strip():
            return {"success": False, "error": "Input CSV data is empty."}

        delim = _detect_delimiter(content)
        reader = csv.DictReader(io.StringIO(content), delimiter=delim)
        rows: List[Dict[str, Any]] = []

        for row in reader:
            parsed_row = {}
            for k, v in row.items():
                clean_k = (k or "").strip()
                parsed_row[clean_k] = _coerce_val(v) if coerce_types else v
            rows.append(parsed_row)

        if output_format == "jsonl":
            result_str = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
        else:
            result_str = json.dumps(rows, indent=2, ensure_ascii=False)

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result_str)

        return {
            "success": True,
            "detected_delimiter": delim,
            "rows_count": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
            "output_path": output_path,
            "data": rows if not output_path else None,
            "preview": rows[:5]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def json_to_csv(
    input_data: Union[str, List[Dict[str, Any]]],
    is_file_path: bool = False,
    output_path: Optional[str] = None,
    delimiter: str = ","
) -> Dict[str, Any]:
    """Convert JSON array or JSONL to CSV format."""
    try:
        records: List[Dict[str, Any]] = []

        if isinstance(input_data, list):
            records = input_data
        elif is_file_path:
            with open(input_data, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read().strip()
            # Check JSONL vs JSON
            if raw.startswith("["):
                records = json.loads(raw)
            else:
                records = [json.loads(line) for line in raw.splitlines() if line.strip()]
        else:
            raw = input_data.strip()
            if raw.startswith("["):
                records = json.loads(raw)
            else:
                records = [json.loads(line) for line in raw.splitlines() if line.strip()]

        if not records or not isinstance(records, list):
            return {"success": False, "error": "Input must be a JSON array of objects."}

        # Collect all unique fieldnames across records
        fieldnames = []
        for r in records:
            if isinstance(r, dict):
                for k in r.keys():
                    if k not in fieldnames:
                        fieldnames.append(k)

        out_buffer = io.StringIO()
        writer = csv.DictWriter(out_buffer, fieldnames=fieldnames, delimiter=delimiter, lineterminator="\n")
        writer.writeheader()

        for r in records:
            if isinstance(r, dict):
                writer.writerow(r)

        csv_str = out_buffer.getvalue()

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(csv_str)

        return {
            "success": True,
            "rows_count": len(records),
            "columns": fieldnames,
            "output_path": output_path,
            "csv_text": csv_str if not output_path else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def csv_json_converter(
    mode: str,  # "csv_to_json" or "json_to_csv"
    input_data: Any,
    is_file_path: bool = False,
    output_path: Optional[str] = None,
    output_format: str = "json"
) -> Dict[str, Any]:
    """
    Main entrypoint: Converts data between CSV and JSON/JSONL.
    """
    if mode == "csv_to_json":
        return csv_to_json(
            input_data=input_data,
            is_file_path=is_file_path,
            output_path=output_path,
            output_format=output_format
        )
    elif mode == "json_to_csv":
        return json_to_csv(
            input_data=input_data,
            is_file_path=is_file_path,
            output_path=output_path
        )
    else:
        return {"success": False, "error": f"Unknown mode '{mode}'. Choose 'csv_to_json' or 'json_to_csv'."}
