import unittest
from unittest.mock import patch
from parsers.drc_parser import DRCParser

class TestDRCParser(unittest.TestCase):
    
    @patch('parsers.drc_parser.DRCParser.read_file')
    def test_simple_format(self, mock_read_file):
        """
        Kiểm thử việc parse định dạng file mẫu (Simple)
        Test parsing the simple sample format
        """
        mock_content = [
            "Rule: M1.S.1\n",
            "Description: Min spacing between M1 = 0.050\n",
            "Violation 1:\n",
            "  Layer: M1\n",
            "  Coordinate: (10.000, 20.000)\n"
        ]
        mock_read_file.return_value = mock_content
        
        parser = DRCParser("dummy_path.rpt")
        result = parser.parse()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Format"], "Simple")
        self.assertEqual(result[0]["Rule"], "M1.S.1")
        self.assertEqual(result[0]["Layer"], "M1")
        self.assertEqual(result[0]["X1"], 10.0)
        self.assertEqual(result[0]["Y1"], 20.0)
        
    @patch('parsers.drc_parser.DRCParser.read_file')
    def test_openroad_format(self, mock_read_file):
        """
        Kiểm thử việc parse định dạng chuẩn OpenROAD TritonRoute
        Test parsing the real OpenROAD TritonRoute format
        """
        mock_content = [
            "Total number of violations: 1\n",
            "violation type: Short\n",
            "  srcs: net36 net22\n",
            "  bbox = ( 48.29, 12.54 ) - ( 48.43, 12.96 ) on Layer metal2\n",
            "  bbox = ( 48.29, 12.54 ) - ( 48.43, 12.96 ) on Layer metal2\n"
        ]
        mock_read_file.return_value = mock_content
        
        parser = DRCParser("dummy_path.rpt")
        result = parser.parse()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Format"], "OpenROAD")
        self.assertEqual(result[0]["Rule"], "Short")
        self.assertEqual(result[0]["Sources"], "net36 net22")
        self.assertEqual(result[0]["Layer"], "metal2")
        self.assertEqual(result[0]["X1"], 48.29)
        self.assertEqual(result[0]["Y1"], 12.54)
        self.assertEqual(result[0]["X2"], 48.43)
        self.assertEqual(result[0]["Y2"], 12.96)

if __name__ == '__main__':
    unittest.main()
