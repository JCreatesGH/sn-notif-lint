"""notiflint: lint ServiceNow notification / email templates for broken refs."""
from .parse import extract_refs, Ref
from .lint import lint_template, Finding, Template
from .suggest import closest, levenshtein
__all__ = ["extract_refs", "Ref", "lint_template", "Finding", "Template",
           "closest", "levenshtein"]
__version__ = "0.2.0"
