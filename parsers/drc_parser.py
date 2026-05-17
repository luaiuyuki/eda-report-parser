import re
from typing import List, Dict, Any
from .base_parser import BaseParser

class DRCParser(BaseParser):
    """
    Parser linh hoạt để phân tích file DRC Report.
    Hỗ trợ 2 định dạng:
      1. Định dạng mẫu đơn giản (Rule/Layer/Coordinate)
      2. Định dạng chuẩn OpenROAD TritonRoute (violation type / srcs / bbox)

    Flexible parser for DRC Report files.
    Supports 2 formats:
      1. Simple sample format (Rule/Layer/Coordinate)
      2. Real OpenROAD TritonRoute format (violation type / srcs / bbox)
    """

    # --- Định dạng 1: Mẫu đơn giản (sample_drc.rpt) ---
    # Rule: M1.S.1
    _SIMPLE_RULE    = re.compile(r"Rule:\s+(.+)")
    _SIMPLE_LAYER   = re.compile(r"Layer:\s+(.+)")
    _SIMPLE_COORD   = re.compile(r"Coordinate:\s+\(([\d\.]+),\s*([\d\.]+)\)")

    # --- Định dạng 2: OpenROAD TritonRoute (real_drc.rpt) ---
    # violation type: Short
    _OPR_VTYPE  = re.compile(r"violation type:\s+(.+)")
    # srcs: net36 net22
    _OPR_SRCS   = re.compile(r"srcs:\s+(.+)")
    # bbox = ( 48.29, 12.54 ) - ( 48.43, 12.96 ) on Layer metal2
    _OPR_BBOX   = re.compile(
        r"bbox\s*=\s*\(\s*([\d\.]+),\s*([\d\.]+)\s*\)\s*-\s*\(\s*([\d\.]+),\s*([\d\.]+)\s*\)\s+on Layer\s+(\S+)"
    )
    # Total number of violations: 5
    _OPR_TOTAL  = re.compile(r"Total number of violations:\s+(\d+)")

    def _detect_format(self, lines: List[str]) -> str:
        """
        Tự động nhận dạng định dạng của file DRC.
        Auto-detects the format of the DRC report file.
        """
        for line in lines[:30]:
            if self._OPR_VTYPE.search(line):
                return "openroad"
        return "simple"

    def parse(self) -> List[Dict[str, Any]]:
        lines = self.read_file()
        fmt = self._detect_format(lines)

        if fmt == "openroad":
            return self._parse_openroad(lines)
        else:
            return self._parse_simple(lines)

    def _parse_simple(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Phân tích định dạng đơn giản: Rule / Layer / Coordinate.
        Parses the simple format: Rule / Layer / Coordinate.
        """
        current_rule = "UNKNOWN"
        current_layer = "UNKNOWN"

        for line in lines:
            line = line.strip()
            rule_m = self._SIMPLE_RULE.search(line)
            if rule_m:
                current_rule = rule_m.group(1)
                continue

            layer_m = self._SIMPLE_LAYER.search(line)
            if layer_m:
                current_layer = layer_m.group(1)
                continue

            coord_m = self._SIMPLE_COORD.search(line)
            if coord_m:
                self.data.append({
                    "Format":       "Simple",
                    "Rule":         current_rule,
                    "Layer":        current_layer,
                    "X1":           float(coord_m.group(1)),
                    "Y1":           float(coord_m.group(2)),
                    "X2":           "",
                    "Y2":           "",
                    "Sources":      "",
                })

        return self.data

    def _parse_openroad(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Phân tích định dạng OpenROAD TritonRoute:
        violation type / srcs / bbox ... on Layer.
        Parses the real OpenROAD TritonRoute format.
        """
        total_violations = 0
        current_vtype = "UNKNOWN"
        current_srcs  = ""
        bbox_count    = 0   # mỗi violation có 2 dòng bbox, chỉ lấy dòng đầu

        for line in lines:
            line = line.strip()

            # Đọc tổng số violations từ header
            total_m = self._OPR_TOTAL.search(line)
            if total_m:
                total_violations = int(total_m.group(1))
                continue

            # Match: violation type
            vtype_m = self._OPR_VTYPE.search(line)
            if vtype_m:
                current_vtype = vtype_m.group(1).strip()
                current_srcs  = ""
                bbox_count    = 0
                continue

            # Match: srcs
            srcs_m = self._OPR_SRCS.search(line)
            if srcs_m:
                current_srcs = srcs_m.group(1).strip()
                continue

            # Match: bbox (chỉ lấy dòng bbox đầu tiên của mỗi violation)
            bbox_m = self._OPR_BBOX.search(line)
            if bbox_m and bbox_count == 0:
                self.data.append({
                    "Format":              "OpenROAD",
                    "Rule":               current_vtype,
                    "Layer":              bbox_m.group(5),
                    "X1":                 float(bbox_m.group(1)),
                    "Y1":                 float(bbox_m.group(2)),
                    "X2":                 float(bbox_m.group(3)),
                    "Y2":                 float(bbox_m.group(4)),
                    "Sources":            current_srcs,
                })
                bbox_count += 1
            elif bbox_m:
                bbox_count = 0  # Reset cho violation tiếp theo

        return self.data
