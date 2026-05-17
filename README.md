# EDA Report Parser

A Python automation tool for parsing and extracting structured data from EDA (Electronic Design Automation) report files — specifically **Timing Reports** and **DRC (Design Rule Check) Reports** — and exporting the results to clean, analysis-ready **CSV files**.

After each analysis, the tool automatically prints a **summary statistics table** to the terminal, highlighting critical metrics such as Worst Negative Slack (WNS) and DRC violation counts per rule and layer.

This project demonstrates backend LSI automation skills, including object-oriented design, regular expression parsing, summary reporting, and command-line tooling.

---

## 🎯 Background & Motivation

In VLSI physical design workflows, EDA tools such as **Synopsys PrimeTime** and **Mentor Calibre** generate large text-based log files containing critical information:

- **Timing Reports**: Setup/Hold slack values for each timing path (Startpoint → Endpoint)
- **DRC Reports**: Design rule violations with layer and coordinate information

These files can contain **thousands of lines**, making manual inspection extremely time-consuming. This tool automates the extraction process, enabling engineers to quickly identify violations and integrate results into reporting pipelines.

---

## ✨ Features

- ✅ Parses **Timing Reports** — extracts Startpoint, Endpoint, Path Group, Status (MET/VIOLATED), and Slack value
- ✅ Parses **DRC Reports** — extracts Violation Type, Layer, Coordinates (X1/Y1 → X2/Y2), and Source nets
- ✅ **Auto-detects report format** — supports both simple and real OpenSTA/OpenROAD formats without configuration
- ✅ Prints **summary statistics table** after each analysis (WNS, TNS, violation counts by rule and layer)
- ✅ Exports all extracted data to **structured CSV files**
- ✅ Clean **Command-Line Interface (CLI)** using `argparse`
- ✅ Professional logging with Python's built-in `logging` module
- ✅ Fully modular and extensible via **Abstract Base Class** design

---

## 📂 Project Structure

```text
eda_log_analyzer/
│
├── parsers/                  # Text parsing logic (OOP design)
│   ├── __init__.py
│   ├── base_parser.py        # Abstract base class for all parsers
│   ├── timing_parser.py      # Parses Timing reports (simple + OpenSTA format)
│   └── drc_parser.py         # Parses DRC reports (simple + OpenROAD format)
│
├── utils/                    # Shared utilities
│   ├── __init__.py
│   ├── csv_writer.py         # Writes extracted data to CSV
│   └── reporter.py           # Prints summary statistics table to terminal
│
├── data/                     # Sample input report files for testing
│   ├── sample_timing.rpt     # Simple timing report (for learning)
│   ├── opensta_timing.rpt    # Realistic OpenSTA-format timing report
│   ├── sample_drc.rpt        # Simple DRC report (for learning)
│   └── real_drc.rpt          # Realistic OpenROAD-format DRC report
│
├── output/                   # Auto-generated CSV output directory
│   ├── timing_summary.csv
│   └── drc_summary.csv
│
├── main.py                   # CLI entry point
└── README.md
```

---

## ⚙️ Requirements

- **Python 3.6+**
- No external dependencies — uses only Python standard libraries (`re`, `csv`, `argparse`, `logging`, `os`, `abc`)

---

## 🚀 Usage

### Run from the `eda_log_analyzer/` directory

**Analyze a Timing Report:**
```bash
python main.py --timing data/sample_timing.rpt
```

**Analyze a DRC Report:**
```bash
python main.py --drc data/real_drc.rpt
```

**Analyze both at once:**
```bash
python main.py --timing data/opensta_timing.rpt --drc data/real_drc.rpt
```

**Specify a custom output directory:**
```bash
python main.py --timing data/opensta_timing.rpt --drc data/real_drc.rpt --outdir results/
```

**Show help:**
```bash
python main.py --help
```

---

## 🖥️ Terminal Output

After running, the tool prints a formatted summary directly in the terminal:

```
2026-05-17 - INFO - Parsing Timing report: data/opensta_timing.rpt
2026-05-17 - INFO - Successfully exported to: output/timing_summary.csv

  +--------------------------------------+
  |        TIMING ANALYSIS SUMMARY       |
  +--------------------------------------+
  |  Total Paths      : 3                |
  |  MET              : 2 (66.7%)        |
  |  VIOLATED         : 1                |
  +--------------------------------------+
  |  WNS (Worst Slack): -0.0100 ns       |
  |  TNS (Total Neg.) : -0.0100 ns       |
  +--------------------------------------+

  [!] Worst Violated Path:
      _715_  ->  _698_
      Slack = -0.01 ns  |  Group: clk

  +--------------------------------------+
  |         DRC VIOLATION SUMMARY        |
  +--------------------------------------+
  |  Total Violations : 5                |
  +--------------------------------------+
  |  By Rule Type:                       |
  |    [ 2x]  Short                      |
  |    [ 1x]  Metal spacing              |
  |    [ 1x]  Via enclosure              |
  |    [ 1x]  Metal width                |
  +--------------------------------------+
  |  By Layer:                           |
  |    [ 2x]  metal2                     |
  |    [ 2x]  metal1                     |
  |    [ 1x]  metal3                     |
  +--------------------------------------+
```

---

## 📊 CSV Output Format

### `timing_summary.csv`

| Format  | Startpoint | Endpoint | Path Group | Status   | Slack |
|---------|------------|----------|------------|----------|-------|
| OPENSTA | _648_      | _679_    | clk        | MET      | 0.67  |
| OPENSTA | _715_      | _698_    | clk        | VIOLATED | -0.01 |

- **Status = MET**: The timing path meets the requirement (slack ≥ 0)
- **Status = VIOLATED**: The timing path fails — slack is negative (critical issue)
- **Slack**: Time margin in nanoseconds. Negative = violation, positive = margin

### `drc_summary.csv`

| Format   | Rule          | Layer  | X1    | Y1    | X2    | Y2    | Sources       |
|----------|---------------|--------|-------|-------|-------|-------|---------------|
| OpenROAD | Short         | metal2 | 48.29 | 12.54 | 48.43 | 12.96 | net36 net22   |
| OpenROAD | Metal spacing | metal1 | 10.26 | 5.32  | 10.40 | 5.60  | _367_/ZN ...  |

- **Rule**: The type of design rule violation (e.g., Short, Metal spacing, Via enclosure)
- **Layer**: The metal/via layer where the violation occurred
- **X1/Y1 → X2/Y2**: Bounding box coordinates of the violation (in micrometers)
- **Sources**: Net or cell pin names involved in the violation

---

## 🏗️ Design Highlights

### Object-Oriented Architecture
All parsers inherit from `BaseParser`, an abstract base class that enforces the `parse()` interface. This makes it trivial to add support for new report types (e.g., LVS, Power/IR-Drop) without modifying existing code — following the **Open/Closed Principle**.

```python
# Adding a new parser is as simple as:
class LVSParser(BaseParser):
    def parse(self) -> List[Dict[str, Any]]:
        ...  # Implement extraction logic here
```

### Automatic Format Detection
Both parsers automatically detect whether the input file uses a simple or real-tool format by scanning the first few lines for format-specific patterns, requiring zero configuration from the user.

---

## 🔭 Potential Extensions

Due to the modular OOP design, this tool can be extended to support:
- LVS (Layout vs. Schematic) reports
- Power / IR-Drop reports (e.g., from Cadence Voltus or Apache RedHawk)
- Congestion reports from Global Routing
- Batch processing of multiple report files in one run
- Integration with data visualization tools (e.g., pandas, matplotlib)

---

## 📁 Sample Data Sources

The realistic sample files in `data/` are modeled after output from open-source EDA tools:
- **OpenSTA** (Static Timing Analysis): Part of the [OpenROAD Project](https://github.com/The-OpenROAD-Project/OpenROAD)
- **TritonRoute** (Detail Router / DRC): Part of the [OpenROAD-flow-scripts](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts)

---

