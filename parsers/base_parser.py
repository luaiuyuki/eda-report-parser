from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os

class BaseParser(ABC):
    """
    Lớp cơ sở trừu tượng cho tất cả các log parser.
    Abstract base class for all log parsers.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data: List[Dict[str, Any]] = []

    def read_file(self) -> List[str]:
        """
        Đọc nội dung file.
        Reads the content of the file.
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File không tồn tại / File not found: {self.filepath}")
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return f.readlines()

    @abstractmethod
    def parse(self) -> List[Dict[str, Any]]:
        """
        Hàm trừu tượng để phân tích logic. Cần được implement bởi class con.
        Abstract method for parsing logic. Must be implemented by subclasses.
        """
        pass
