import csv
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CSVWriter:
    """
    Utility class để ghi dữ liệu ra file CSV một cách linh hoạt.
    Utility class to write extracted data flexibly into CSV format.
    """
    @staticmethod
    def write(filepath: str, data: List[Dict[str, Any]]) -> None:
        if not data:
            logger.warning(f"Không có dữ liệu để ghi vào / No data to write to {filepath}")
            return
            
        try:
            # Tự động lấy headers từ dictionary keys
            headers = data[0].keys()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
                
            logger.info(f"Đã xuất dữ liệu thành công / Successfully exported to: {filepath}")
        except IOError as e:
            logger.error(f"Lỗi khi ghi file / Error writing file {filepath}: {e}")
