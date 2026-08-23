#!/usr/bin/env python3
"""Convert sentinel-scan mcp JSON results into SARIF or Markdown, and
apply a fail-on-severity gate for CI pipelines.

Used internally by the sentinel-scan-cli GitHub Action. Not part of the
public CLI surface.
"""
import argparse
import json
import sys

SEVERITY_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
SEVERITY_TO_SARIF_LEVEL = {"HIGH": "error", "MEDIUM": "warning", "LOW": "note"}


def to_sarif(data, manifest_path):
    rules = {}
    sarif_results = []
    for r in data["results"]:
        rule_id = r["heuristic"]
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": rule_id,
                "shortDescription": {"text": r["owasp_category"]},
                "helpUri": "https://github.com/Ventrova/sentinel-scan-cli",
                "properties": {"owasp_category": r["owasp_category"]},
            }
        sarif_results.append(
            {
                "ruleId": rule_id,
                "level": SEVERITY_TO_SARIF_LEVEL.get(r["severity"], "warning"),
                "message": {
                    "text": "[{}] {} on tool '{}': {}".format(
                        r["severity"], r["owasp_category"], r["tool"], r["recommendation"]
                    )
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": manifest_path},
                        }
                    }
                ],
                "partialFingerprints": {
                    "sentinelScan/heuristic": rule_id,
                    "sentinelScan/tool": r["tool"],
                },
                "properties": {"evidence": r["evidence"], "tool": r["tool"]},
            }
        )

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "sentinel-scan-cli",
                        "informationUri": "https://github.com/Ventrova/sentinel-scan-cli",
                        "version": data["summary"].get("version", "unknown"),
                        "rules": list(rules.values()),
                    }
                },
                "results": sarif_results,
            }
        ],
    }


def to_markdown(data, manifest_path):
    summary = data["summary"]
    lines = [
        "## sentinel-scan-cli MCP manifest report",
        "",
        "Manifest: `{}`".format(manifest_path),
        "",
        "| Tools scanned | Servers scanned | Findings | High | Medium | Low |",
        "|---|---|---|---|---|---|",
        "| {} | {} | {} | {} | {} | {} |".format(
            summary.get("num_tools_scanned", 0),
            summary.get("num_servers_scanned", 0),
            summary.get("num_findings", 0),
            summary.get("findings_by_severity", {}).get("HIGH", 0),
            summary.get("findings_by_severity", {}).get("MEDIUM", 0),
            summary.get("findings_by_severity", {}).get("LOW", 0),
        ),
        "",
    ]
    if not data["results"]:
        lines.append("No findings. :white_check_mark:")
        return "\n".join(lines) + "\n"

    lines.append("| Severity | OWASP category | Heuristic | Tool | Recommendation |")
    lines.append("|---|---|---|---|---|")
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    for r in sorted(data["results"], key=lambda r: order.get(r["severity"], 3)):
        lines.append(
            "| {} | {} | {} | `{}` | {} |".format(
                r["severity"],
                r["owasp_category"],
                r["heuristic"],
                r["tool"],
                r["recommendation"].replace("|", "\\|"),
            )
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Raw sentinel-scan mcp JSON results")
    parser.add_argument("--manifest", required=True, help="Path to the scanned manifest, for report context")
    parser.add_argument("--format", choices=["sarif", "markdown", "json"], required=True)
    parser.add_argument("--output", required=True, help="Where to write the converted report")
    parser.add_argument(
        "--fail-on-severity",
        choices=["high", "medium", "low", "none"],
        default="high",
        help="Exit non-zero if any finding meets or exceeds this severity",
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.format == "sarif":
        report = to_sarif(data, args.manifest)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    elif args.format == "markdown":
        report = to_markdown(data, args.manifest)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    summary = data["summary"]
    by_sev = summary.get("findings_by_severity", {})
    print("sentinel-scan mcp: {} finding(s) - HIGH={} MEDIUM={} LOW={}".format(
        summary.get("num_findings", 0), by_sev.get("HIGH", 0), by_sev.get("MEDIUM", 0), by_sev.get("LOW", 0)
    ))

    if args.fail_on_severity == "none":
        return 0

    threshold = SEVERITY_RANK[args.fail_on_severity.upper()]
    breach = any(SEVERITY_RANK.get(r["severity"], 0) >= threshold for r in data["results"])
    if breach:
        print(
            "::error::sentinel-scan found findings at or above severity '{}'".format(args.fail_on_severity.upper())
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
