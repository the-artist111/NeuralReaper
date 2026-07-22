#!/usr/bin/env python3
"""
FALSE POSITIVE FILTERING ENGINE
Reduces noise from vulnerability scanners by filtering out
known-bad signatures, low-confidence matches, and common FPs.
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FilterRule:
    """A false-positive filter rule."""
    name: str
    pattern: str           # Regex to match FP signatures
    tool: str              # Which tool this applies to (nuclei/sqlmap/etc)
    severity: str          # info/low/medium/high/critical
    reason: str            # Why this is considered a false positive
    confidence: float      # 0.0-1.0, how sure we are this is FP


# ── KNOWN FALSE POSITIVE SIGNATURES ──
# These are patterns that frequently trigger in scanners but are
# typically benign in real-world deployments.

NUCLEI_FP_RULES: List[FilterRule] = [
    # Info-level tech detection — not a vulnerability
    FilterRule(
        name="tech-detect-generic",
        pattern=r"\[tech-detect:[^\]]+\]",
        tool="nuclei",
        severity="info",
        reason="Technology fingerprinting is informational, not a vulnerability",
        confidence=0.95
    ),

    # WordPress readme — extremely common, rarely exploitable
    FilterRule(
        name="wordpress-readme",
        pattern=r"\[wordpress-readme\]",
        tool="nuclei",
        severity="info",
        reason="WordPress readme files are public by design and rarely indicate vulnerability",
        confidence=0.98
    ),

    # robots.txt disclosure — standard web practice
    FilterRule(
        name="robots-txt",
        pattern=r"\[robots-txt:[^\]]+\]",
        tool="nuclei",
        severity="info",
        reason="robots.txt is intentionally public; content may be sensitive but file presence is not a vuln",
        confidence=0.95
    ),

    # Favicon hash matches — purely informational
    FilterRule(
        name="favicon-hash",
        pattern=r"\[favicon-detect:[^\]]+\]",
        tool="nuclei",
        severity="info",
        reason="Favicon detection is technology fingerprinting, not a vulnerability",
        confidence=0.99
    ),

    # WAF detection — not a vulnerability
    FilterRule(
        name="waf-detect",
        pattern=r"\[waf-detect:[^\]]+\]",
        tool="nuclei",
        severity="info",
        reason="WAF detection is defensive infrastructure fingerprinting",
        confidence=0.95
    ),

    # Missing headers on static assets
    FilterRule(
        name="missing-headers-static",
        pattern=r"\[missing-[^\]]+\].*\.(js|css|png|jpg|gif|woff|svg)",
        tool="nuclei",
        severity="low",
        reason="Security headers on static assets have limited security impact",
        confidence=0.85
    ),
]

SQLMAP_FP_RULES: List[FilterRule] = [
    # Time-based SQLi on heavily loaded servers
    FilterRule(
        name="time-based-fp",
        pattern=r"\(time-based\).*\blatency\b|\bresponse time\b",
        tool="sqlmap",
        severity="medium",
        reason="Time-based detections on loaded servers often produce false positives",
        confidence=0.65
    ),

    # Boolean-based with minimal diff
    FilterRule(
        name="boolean-minimal",
        pattern=r"\(boolean-based\).*\bdiff:\s*\d+\b",
        tool="sqlmap",
        severity="medium",
        reason="Boolean-based detection with minimal content difference needs manual verification",
        confidence=0.55
    ),
]


class FalsePositiveFilter:
    """
    Reduces scanner noise by applying known false-positive rules.

    Usage:
        fp_filter = FalsePositiveFilter()
        clean_results = fp_filter.filter_nuclei(raw_nuclei_output)
        clean_results = fp_filter.filter_sqlmap(raw_sqlmap_output)
    """

    def __init__(self, min_confidence: float = 0.70):
        self.min_confidence = min_confidence
        self.fp_log: List[Dict] = []
        self.stats = {"total": 0, "filtered": 0, "kept": 0}

    def _apply_rules(self, line: str, rules: List[FilterRule]) -> Tuple[bool, Optional[FilterRule]]:
        """Check if a line matches any FP rule. Returns (is_fp, matched_rule)."""
        for rule in rules:
            if rule.confidence < self.min_confidence:
                continue
            if re.search(rule.pattern, line, re.IGNORECASE):
                return True, rule
        return False, None

    def filter_nuclei(self, raw_output: str) -> str:
        """Filter Nuclei output for known false positives."""
        lines = raw_output.splitlines()
        kept = []

        for line in lines:
            self.stats["total"] += 1
            is_fp, rule = self._apply_rules(line, NUCLEI_FP_RULES)

            if is_fp and rule:
                self.stats["filtered"] += 1
                self.fp_log.append({
                    "tool": "nuclei",
                    "line": line[:200],
                    "rule": rule.name,
                    "reason": rule.reason,
                    "confidence": rule.confidence
                })
            else:
                self.stats["kept"] += 1
                kept.append(line)

        return "\n".join(kept)

    def filter_sqlmap(self, raw_output: str) -> str:
        """Filter SQLMap output for known false positives."""
        lines = raw_output.splitlines()
        kept = []

        for line in lines:
            self.stats["total"] += 1
            is_fp, rule = self._apply_rules(line, SQLMAP_FP_RULES)

            if is_fp and rule:
                self.stats["filtered"] += 1
                self.fp_log.append({
                    "tool": "sqlmap",
                    "line": line[:200],
                    "rule": rule.name,
                    "reason": rule.reason,
                    "confidence": rule.confidence
                })
            else:
                self.stats["kept"] += 1
                kept.append(line)

        return "\n".join(kept)

    def get_report(self) -> str:
        """Generate a false-positive filtering report."""
        lines = [
            "=== FALSE POSITIVE FILTER REPORT ===",
            f"Total findings processed: {self.stats['total']}",
            f"Filtered as false positive: {self.stats['filtered']}",
            f"Kept for review: {self.stats['kept']}",
            f"Reduction rate: {(self.stats['filtered']/max(self.stats['total'],1)*100):.1f}%",
            "",
            "=== FILTERED ITEMS ===",
        ]
        for entry in self.fp_log:
            lines.append(f"[{entry['tool']}] {entry['rule']} (confidence: {entry['confidence']})")
            lines.append(f"  Reason: {entry['reason']}")
            lines.append(f"  Line: {entry['line'][:100]}...")
            lines.append("")
        return "\n".join(lines)


# ── MCP TOOL WRAPPERS ──
# Add these as @mcp.tool() functions in your server.py

def fp_filter_nuclei(raw_output: str = "", min_confidence: float = 0.70) -> str:
    """Filter Nuclei output to remove common false positives."""
    fp_filter = FalsePositiveFilter(min_confidence=min_confidence)
    filtered = fp_filter.filter_nuclei(raw_output)
    report = fp_filter.get_report()
    return f"{filtered}\n\n{report}"

def fp_filter_sqlmap(raw_output: str = "", min_confidence: float = 0.60) -> str:
    """Filter SQLMap output to remove common false positives."""
    fp_filter = FalsePositiveFilter(min_confidence=min_confidence)
    filtered = fp_filter.filter_sqlmap(raw_output)
    report = fp_filter.get_report()
    return f"{filtered}\n\n{report}"

def fp_add_custom_rule(name: str = "", pattern: str = "", tool: str = "nuclei", 
                       severity: str = "low", reason: str = "", confidence: float = 0.80) -> str:
    """Add a custom false-positive rule at runtime."""
    rule = FilterRule(name, pattern, tool, severity, reason, confidence)
    if tool == "nuclei":
        NUCLEI_FP_RULES.append(rule)
    elif tool == "sqlmap":
        SQLMAP_FP_RULES.append(rule)
    return f"[+] Added FP rule '{name}' for {tool} (confidence: {confidence})"


def fp_show_rules(tool: str = "all") -> str:
    """Show all active false-positive rules."""
    lines = ["=== ACTIVE FALSE POSITIVE RULES ===", ""]
    rules = []
    if tool in ("all", "nuclei"):
        rules.extend([(r, "nuclei") for r in NUCLEI_FP_RULES])
    if tool in ("all", "sqlmap"):
        rules.extend([(r, "sqlmap") for r in SQLMAP_FP_RULES])

    for rule, t in rules:
        lines.append(f"[{t}] {rule.name} (confidence: {rule.confidence})")
        lines.append(f"  Pattern: {rule.pattern[:60]}...")
        lines.append(f"  Reason: {rule.reason}")
        lines.append("")
    return "\n".join(lines)
