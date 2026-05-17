import os
import argparse
import logging
from parsers.timing_parser import TimingParser
from parsers.drc_parser import DRCParser
from utils.csv_writer import CSVWriter
from utils.reporter import print_timing_summary, print_drc_summary

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EDALogAnalyzer")


def main():
    parser = argparse.ArgumentParser(
        description="EDA Report Parser: Extract data from Timing and DRC reports to CSV."
    )
    parser.add_argument('--timing', type=str,
                        help='Path to Timing Report file (e.g. data/opensta_timing.rpt)')
    parser.add_argument('--drc',    type=str,
                        help='Path to DRC Report file (e.g. data/real_drc.rpt)')
    parser.add_argument('--outdir', type=str, default='output',
                        help='Output directory for CSV files (default: output/)')

    args = parser.parse_args()

    if not args.timing and not args.drc:
        logger.error("Please provide at least one report file (--timing or --drc).")
        logger.info("Example: python main.py --timing data/opensta_timing.rpt")
        return

    # Create output directory if it does not exist
    os.makedirs(args.outdir, exist_ok=True)

    # ── 1. Process Timing Report ──────────────────────────────────────────────
    if args.timing:
        logger.info(f"Parsing Timing report: {args.timing}")
        try:
            t_parser    = TimingParser(args.timing)
            timing_data = t_parser.parse()

            out_file = os.path.join(args.outdir, 'timing_summary.csv')
            CSVWriter.write(out_file, timing_data)

            # Print summary statistics to terminal
            print_timing_summary(timing_data)

        except Exception as e:
            logger.error(f"Failed to process Timing report: {e}")

    # ── 2. Process DRC Report ─────────────────────────────────────────────────
    if args.drc:
        logger.info(f"Parsing DRC report: {args.drc}")
        try:
            drc_parser = DRCParser(args.drc)
            drc_data   = drc_parser.parse()

            out_file = os.path.join(args.outdir, 'drc_summary.csv')
            CSVWriter.write(out_file, drc_data)

            # Print summary statistics to terminal
            print_drc_summary(drc_data)

        except Exception as e:
            logger.error(f"Failed to process DRC report: {e}")


if __name__ == "__main__":
    main()
