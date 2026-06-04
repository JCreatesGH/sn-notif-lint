"""notiflint: lint ServiceNow notification / email templates for broken refs."""
from .parse import extract_refs, Ref
from .lint import lint_template, Finding, Template
__all__ = ["extract_refs", "Ref", "lint_template", "Finding", "Template"]
__version__ = "0.1.0"
