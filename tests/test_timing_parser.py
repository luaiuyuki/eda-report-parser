import unittest
from unittest.mock import patch
from parsers.timing_parser import TimingParser

class TestTimingParser(unittest.TestCase):
    
    @patch('parsers.timing_parser.TimingParser.read_file')
    def test_simple_format(self, mock_read_file):
        """
        Kiểm thử việc parse định dạng file mẫu (Simple)
        Test parsing the simple sample format
        """
        mock_content = [
            "Startpoint: reg_A (rising edge-triggered flip-flop)\n",
            "Endpoint: reg_B (rising edge-triggered flip-flop)\n",
            "Path Group: clk\n",
            "Path Type: max\n",
            "  slack (MET)                                         9.68\n",
            "Startpoint: reg_C (rising edge-triggered flip-flop)\n",
            "Endpoint: reg_D (rising edge-triggered flip-flop)\n",
            "Path Group: clk\n",
            "  slack (VIOLATED)                                   -1.00\n"
        ]
        mock_read_file.return_value = mock_content
        
        parser = TimingParser("dummy_path.rpt")
        result = parser.parse()
        
        self.assertEqual(len(result), 2)
        
        # Kiểm tra path 1
        self.assertEqual(result[0]["Startpoint"], "reg_A")
        self.assertEqual(result[0]["Endpoint"], "reg_B")
        self.assertEqual(result[0]["Path Group"], "clk")
        self.assertEqual(result[0]["Status"], "MET")
        self.assertEqual(result[0]["Slack"], 9.68)
        self.assertEqual(result[0]["Format"], "SIMPLE")
        
        # Kiểm tra path 2
        self.assertEqual(result[1]["Startpoint"], "reg_C")
        self.assertEqual(result[1]["Endpoint"], "reg_D")
        self.assertEqual(result[1]["Status"], "VIOLATED")
        self.assertEqual(result[1]["Slack"], -1.0)
        
    @patch('parsers.timing_parser.TimingParser.read_file')
    def test_opensta_format(self, mock_read_file):
        """
        Kiểm thử việc parse định dạng chuẩn OpenSTA
        Test parsing the real OpenSTA format
        """
        mock_content = [
            "Startpoint: _648_ (rising edge-triggered flip-flop clocked by clk)\n",
            "Endpoint: _679_ (rising edge-triggered flip-flop clocked by clk)\n",
            "Path Group: clk\n",
            "          1.18   data required time\n",
            "         -0.51   data arrival time\n",
            "---------------------------------------------------------\n",
            "          0.67   slack (MET)\n"
        ]
        mock_read_file.return_value = mock_content
        
        parser = TimingParser("dummy_path.rpt")
        result = parser.parse()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Startpoint"], "_648_")
        self.assertEqual(result[0]["Endpoint"], "_679_")
        self.assertEqual(result[0]["Path Group"], "clk")
        self.assertEqual(result[0]["Status"], "MET")
        self.assertEqual(result[0]["Slack"], 0.67)
        self.assertEqual(result[0]["Format"], "OPENSTA")

if __name__ == '__main__':
    unittest.main()
