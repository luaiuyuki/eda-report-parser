import os
import argparse
import logging
from parsers.timing_parser import TimingParser
from parsers.drc_parser import DRCParser
from utils.csv_writer import CSVWriter

# Cấu hình logging chuyên nghiệp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EDALogAnalyzer")

def main():
    # Khởi tạo CLI Argument Parser
    parser = argparse.ArgumentParser(
        description="EDA Log Analyzer: Trích xuất dữ liệu từ Timing và DRC reports ra CSV."
    )
    parser.add_argument('--timing', type=str, help='Đường dẫn tới file Timing Report (VD: PrimeTime)')
    parser.add_argument('--drc', type=str, help='Đường dẫn tới file DRC Report (VD: Calibre)')
    parser.add_argument('--outdir', type=str, default='output', help='Thư mục chứa file CSV đầu ra (Mặc định: output/)')
    
    args = parser.parse_args()
    
    if not args.timing and not args.drc:
        logger.error("Vui lòng cung cấp ít nhất một file báo cáo để phân tích (dùng cờ --timing hoặc --drc).")
        logger.info("Ví dụ: python main.py --timing data/sample_timing.rpt")
        return
        
    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs(args.outdir, exist_ok=True)
    
    # 1. Xử lý File Timing
    if args.timing:
        logger.info(f"Bắt đầu phân tích Timing report: {args.timing}")
        try:
            t_parser = TimingParser(args.timing)
            timing_data = t_parser.parse()
            out_file = os.path.join(args.outdir, 'timing_summary.csv')
            CSVWriter.write(out_file, timing_data)
        except Exception as e:
            logger.error(f"Lỗi khi xử lý file Timing: {e}")

    # 2. Xử lý File DRC
    if args.drc:
        logger.info(f"Bắt đầu phân tích DRC report: {args.drc}")
        try:
            drc_parser = DRCParser(args.drc)
            drc_data = drc_parser.parse()
            out_file = os.path.join(args.outdir, 'drc_summary.csv')
            CSVWriter.write(out_file, drc_data)
        except Exception as e:
            logger.error(f"Lỗi khi xử lý file DRC: {e}")

if __name__ == "__main__":
    main()
