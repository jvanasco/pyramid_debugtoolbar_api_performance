"""Helpers for exporting text fields to spreadsheet CSV files."""

from six import text_type


def sanitize_spreadsheet_cell(value):
    # type: (text_type) -> text_type
    """Prefix formula-like text with a spreadsheet text marker."""
    stripped = value.lstrip()
    if value.startswith((u"\t", u"\r", u"\n")) or stripped.startswith(
        (u"=", u"+", u"-", u"@", u"\uff1d", u"\uff0b", u"\uff0d", u"\uff20")
    ):
        return u"'" + value
    return value
