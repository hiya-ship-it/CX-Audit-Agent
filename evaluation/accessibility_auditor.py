"""
DEPRECATED — Accessibility Auditor
-------------------------------------
This module has been merged into evaluation/design_evaluator.py.

The combined Design & Accessibility Evaluator (DesignEvaluator) now covers
WCAG 2.2 A/AA compliance alongside visual design craft in a single audit.

This stub re-exports AccessibilityAuditResult as an alias of DesignAuditResult
so any legacy import references in report_generator.py or main.py continue to
resolve during the transition. Do not write new code against this module.
"""
from evaluation.design_evaluator import DesignAuditResult as AccessibilityAuditResult  # noqa: F401

__all__ = ["AccessibilityAuditResult"]
