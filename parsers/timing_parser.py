import re
from typing import List, Dict, Any
from .base_parser import BaseParser

class TimingParser(BaseParser):
    """
    Parser linh hoạt để phân tích file Timing Report.
    Hỗ trợ 2 định dạng:
      1. Định dạng mẫu đơn giản (sample_timing.rpt)
      2. Định dạng chuẩn OpenSTA / OpenROAD (opensta_timing.rpt)

    Flexible parser for Timing Report files.
    Supports 2 formats:
      1. Simple sample format (sample_timing.rpt)
      2. Real OpenSTA/OpenROAD format (opensta_timing.rpt)
    """

    # --- Patterns chung cho cả 2 định dạng ---
    _STARTPOINT  = re.compile(r"Startpoint:\s+(\S+)")
    _ENDPOINT    = re.compile(r"Endpoint:\s+(\S+)")
    _PATH_GROUP  = re.compile(r"Path Group:\s+(\S+)")

    # --- Định dạng 1: Simple ---
    # slack (MET)                                         9.68
    _SIMPLE_SLACK = re.compile(r"slack\s+\((VIOLATED|MET)\)\s+([\-\d\.]+)")

    # --- Định dạng 2: OpenSTA ---
    # Số cuối dòng phân cách là giá trị slack:
    #           0.67   slack (MET)
    #          -0.01   slack (VIOLATED)
    _OPSTA_SLACK  = re.compile(r"([\-\d\.]+)\s+slack\s+\((VIOLATED|MET)\)")

    def _detect_format(self, lines: List[str]) -> str:
        """
        Tự động nhận dạng định dạng timing report.
        Auto-detects the format of the timing report file.
        """
        for line in lines[:50]:
            # OpenSTA puts value BEFORE "slack"
            if self._OPSTA_SLACK.search(line):
                return "opensta"
            # Simple format puts value AFTER "slack (STATUS)"
            if self._SIMPLE_SLACK.search(line):
                return "simple"
        return "simple"

    def parse(self) -> List[Dict[str, Any]]:
        lines = self.read_file()
        fmt = self._detect_format(lines)
        return self._parse_paths(lines, fmt)

    def _parse_paths(self, lines: List[str], fmt: str) -> List[Dict[str, Any]]:
        """
        Phân tích các timing path từ file theo định dạng đã phát hiện.
        Parses timing paths according to the detected format.
        """
        current: Dict[str, Any] = {}

        for line in lines:
            stripped = line.strip()

            # 1. Startpoint — bắt đầu một record mới
            sp_m = self._STARTPOINT.search(stripped)
            if sp_m:
                if current and "Slack" in current:
                    self.data.append(current)
                current = {
                    "Format":     fmt.upper(),
                    "Startpoint": sp_m.group(1),
                    "Endpoint":   "",
                    "Path Group": "",
                    "Status":     "",
                    "Slack":      None,
                }
                continue

            if not current:
                continue

            # 2. Endpoint
            ep_m = self._ENDPOINT.search(stripped)
            if ep_m:
                current["Endpoint"] = ep_m.group(1)
                continue

            # 3. Path Group
            pg_m = self._PATH_GROUP.search(stripped)
            if pg_m:
                current["Path Group"] = pg_m.group(1)
                continue

            # 4. Slack — theo đúng định dạng
            if fmt == "opensta":
                slack_m = self._OPSTA_SLACK.search(stripped)
                if slack_m:
                    current["Slack"]  = float(slack_m.group(1))
                    current["Status"] = slack_m.group(2)
                    self.data.append(current)
                    current = {}
            else:
                slack_m = self._SIMPLE_SLACK.search(stripped)
                if slack_m:
                    current["Status"] = slack_m.group(1)
                    current["Slack"]  = float(slack_m.group(2))
                    self.data.append(current)
                    current = {}

        # Ghi record cuối nếu còn
        if current and "Slack" in current and current["Slack"] is not None:
            self.data.append(current)

        return self.data
