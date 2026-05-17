from typing import List, Dict, Any

def print_timing_summary(data: List[Dict[str, Any]]) -> None:
    """
    Calculates and prints a formatted summary table for Timing report data.
    Tính toán và in bảng tóm tắt cho dữ liệu Timing report.
    """
    if not data:
        print("  [No timing data to summarize]")
        return

    total   = len(data)
    violated = [r for r in data if r.get("Status") == "VIOLATED"]
    met      = [r for r in data if r.get("Status") == "MET"]

    n_violated = len(violated)
    n_met      = len(met)
    pct_met    = (n_met / total * 100) if total > 0 else 0

    # Worst Negative Slack (WNS) — most negative slack among violated paths
    slack_values = [r["Slack"] for r in violated if r.get("Slack") is not None]
    wns = min(slack_values) if slack_values else None

    # Total Negative Slack (TNS) — sum of all negative slacks
    tns = sum(slack_values) if slack_values else 0.0

    w = 38  # box width
    sep = "  +" + "-" * w + "+"
    print()
    print(sep)
    print("  |" + "  TIMING ANALYSIS SUMMARY".center(w) + "|")
    print(sep)
    print("  |" + f"  Total Paths      : {total:<18}".ljust(w) + "|")
    print("  |" + f"  MET              : {n_met} ({pct_met:.1f}%)".ljust(w) + "|")
    print("  |" + f"  VIOLATED         : {n_violated}".ljust(w) + "|")
    print(sep)

    if wns is not None:
        print("  |" + f"  WNS (Worst Slack): {wns:.4f} ns".ljust(w) + "|")
        print("  |" + f"  TNS (Total Neg.) : {tns:.4f} ns".ljust(w) + "|")
    else:
        print("  |" + "  WNS              : N/A (all paths MET)".ljust(w) + "|")

    print(sep)
    print()

    # Print the worst violated path if any
    if violated:
        worst = min(violated, key=lambda r: r.get("Slack", 0))
        print(f"  [!] Worst Violated Path:")
        print(f"      {worst.get('Startpoint', '?')}  ->  {worst.get('Endpoint', '?')}")
        print(f"      Slack = {worst.get('Slack')} ns  |  Group: {worst.get('Path Group', '?')}")
        print()


def print_drc_summary(data: List[Dict[str, Any]]) -> None:
    """
    Calculates and prints a formatted summary table for DRC report data.
    Tính toán và in bảng tóm tắt cho dữ liệu DRC report.
    """
    if not data:
        print("  [No DRC data to summarize]")
        return

    total = len(data)

    # Count violations per rule type
    rule_counts: Dict[str, int] = {}
    for record in data:
        rule = record.get("Rule", "UNKNOWN")
        rule_counts[rule] = rule_counts.get(rule, 0) + 1

    # Count violations per layer
    layer_counts: Dict[str, int] = {}
    for record in data:
        layer = record.get("Layer", "UNKNOWN")
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    w = 38
    sep = "  +" + "-" * w + "+"
    print()
    print(sep)
    print("  |" + "  DRC VIOLATION SUMMARY".center(w) + "|")
    print(sep)
    print("  |" + f"  Total Violations : {total:<18}".ljust(w) + "|")
    print(sep)
    print("  |" + "  By Rule Type:".ljust(w) + "|")
    for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
        line = f"    [{count:>2}x]  {rule}"
        print("  |" + line[:w].ljust(w) + "|")
    print(sep)
    print("  |" + "  By Layer:".ljust(w) + "|")
    for layer, count in sorted(layer_counts.items(), key=lambda x: -x[1]):
        line = f"    [{count:>2}x]  {layer}"
        print("  |" + line[:w].ljust(w) + "|")
    print(sep)
    print()
