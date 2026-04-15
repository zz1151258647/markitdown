import sys
import re
from typing import BinaryIO, Any, Optional
from ._html_converter import HtmlConverter
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._exceptions import MissingDependencyException, MISSING_DEPENDENCY_MESSAGE
from .._stream_info import StreamInfo

# Try loading optional (but in this case, required) dependencies
# Save reporting of any exceptions for later
_xlsx_dependency_exc_info = None
_xlsx_openpyxl_exc_info = None
try:
    import pandas as pd
except ImportError:
    _xlsx_dependency_exc_info = sys.exc_info()

try:
    import openpyxl
    from openpyxl.utils import get_column_letter
except ImportError:
    _xlsx_openpyxl_exc_info = sys.exc_info()

_xls_dependency_exc_info = None
try:
    import pandas as pd  # noqa: F811
    import xlrd  # noqa: F401
except ImportError:
    _xls_dependency_exc_info = sys.exc_info()

ACCEPTED_XLSX_MIME_TYPE_PREFIXES = [
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
]
ACCEPTED_XLSX_FILE_EXTENSIONS = [".xlsx"]

ACCEPTED_XLS_MIME_TYPE_PREFIXES = [
    "application/vnd.ms-excel",
    "application/excel",
]
ACCEPTED_XLS_FILE_EXTENSIONS = [".xls"]


def _fill_merged_cells(ws) -> list[list]:
    """
    Read worksheet and fill merged cell values.
    Returns a 2D list with merged cells filled in.
    """
    if _xlsx_openpyxl_exc_info is not None:
        raise MissingDependencyException(
            MISSING_DEPENDENCY_MESSAGE.format(
                converter="XlsxConverter",
                extension=".xlsx",
                feature="openpyxl (for merged cell support)",
            )
        ) from _xlsx_openpyxl_exc_info[1].with_traceback(
            _xlsx_openpyxl_exc_info[2]
        )

    # Read all cells including their actual values (merged cells return None for non-top-left)
    data = []
    for row_idx, row in enumerate(ws.iter_rows(), start=1):
        row_data = []
        for col_idx, cell in enumerate(row, start=1):
            row_data.append(cell.value)
        data.append(row_data)

    # Process merged cells: fill non-top-left cells with top-left value
    for merged_range in ws.merged_cells.ranges:
        min_col, min_row = merged_range.bounds[0], merged_range.bounds[1]
        max_col, max_row = merged_range.bounds[2], merged_range.bounds[3]
        top_left_value = ws.cell(row=min_row, column=min_col).value

        # Fill all cells in the merged range with the top-left value
        # Only if they don't already have a value
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                row_idx = row - 1
                col_idx = col - 1
                # Only fill if current cell is None and top_left has a value
                if data[row_idx][col_idx] is None and top_left_value is not None:
                    data[row_idx][col_idx] = top_left_value

    return data


def _clean_dataframe(df, headers: Optional[list] = None) -> tuple[list, list]:
    """
    Clean dataframe:
    1. Forward-fill NaN values in first few columns (for merged cells in hierarchy columns)
    2. Remove rows where key columns are all NaN
    3. Clean up NaN strings and newlines
    Returns (cleaned_rows, headers)
    """
    import pandas as pd

    df = df.copy()

    # Replace pandas NA/NaN with None for proper handling
    df = df.replace({pd.NA: None, float('nan'): None})

    # Forward fill NaN values for the first 4 columns (typically hierarchy columns)
    # This handles merged cells where sub-items inherit parent value
    for col in range(min(4, len(df.columns))):
        df.iloc[:, col] = df.iloc[:, col].ffill()

    # Get headers from first row if not provided
    if headers is None:
        headers = df.iloc[0].tolist() if len(df) > 0 else []
        df = df.iloc[1:]  # Remove header row from data

    # Remove rows where all data columns (after first 4 hierarchy columns) are None
    # But keep rows that have at least some content
    if len(df) > 0:
        # Define threshold: at least one value in columns 4+ must be non-None
        data_cols = df.iloc[:, 4:] if len(df.columns) > 4 else df
        mask = data_cols.apply(lambda row: any(v is not None for v in row), axis=1)
        df = df[mask]

    # Convert to list of lists
    rows = df.values.tolist()

    # Clean up each cell
    cleaned_rows = []
    for row in rows:
        cleaned_row = []
        for cell in row:
            if cell is None or (isinstance(cell, float) and str(cell) == 'nan'):
                cleaned_row.append("")
            elif isinstance(cell, str):
                # Replace literal \n with spaces or proper line breaks
                # Keep newlines but clean up excessive ones
                cell = cell.strip()
                cleaned_row.append(cell)
            else:
                cleaned_row.append(str(cell))
        cleaned_rows.append(cleaned_row)

    # Clean headers
    cleaned_headers = []
    for h in headers:
        if h is None or (isinstance(h, float) and str(h) == 'nan'):
            cleaned_headers.append("")
        elif isinstance(h, str):
            cleaned_headers.append(h.strip())
        else:
            cleaned_headers.append(str(h))

    return cleaned_rows, cleaned_headers


def _dataframe_to_markdown(df, sheet_name: str) -> str:
    """
    Convert a cleaned dataframe to markdown table format.
    Handles headers, rows, and properly escapes pipe characters.
    """
    import pandas as pd

    if df.empty:
        return ""

    # Build markdown table
    lines = []

    # Header row
    header_line = "| " + " | ".join(str(h) for h in df.columns) + " |"
    separator_line = "| " + " | ".join("---" for _ in df.columns) + " |"

    lines.append(header_line)
    lines.append(separator_line)

    # Data rows
    for _, row in df.iterrows():
        cells = []
        for val in row:
            if pd.isna(val) or val is None:
                cells.append("")
            else:
                # Escape pipe characters in cell content
                # Replace newlines with <br> to preserve line breaks in markdown table cells
                val_str = str(val).strip()
                val_str = val_str.replace("|", "\\|")
                val_str = val_str.replace("\n", "<br>")
                cells.append(val_str)
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


class XlsxConverter(DocumentConverter):
    """
    Converts XLSX files to Markdown, with each sheet presented as a separate Markdown table.
    Handles merged cells, removes empty rows, and cleans up NaN values.
    """

    def __init__(self):
        super().__init__()
        self._html_converter = HtmlConverter()

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_XLSX_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_XLSX_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Check the dependencies
        if _xlsx_dependency_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".xlsx",
                    feature="xlsx",
                )
            ) from _xlsx_dependency_exc_info[
                1
            ].with_traceback(  # type: ignore[union-attr]
                _xlsx_dependency_exc_info[2]
            )

        if _xlsx_openpyxl_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".xlsx",
                    feature="xlsx (openpyxl required for full support)",
                )
            ) from _xlsx_openpyxl_exc_info[1].with_traceback(
                _xlsx_openpyxl_exc_info[2]
            )

        import pandas as pd

        # Read file into openpyxl to handle merged cells
        file_stream.seek(0)
        wb = openpyxl.load_workbook(file_stream, data_only=True)

        md_content = ""

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            data = _fill_merged_cells(ws)

            if not data:
                continue

            md_content += f"## {sheet_name}\n"

            # Convert to DataFrame
            # Find the header row (first row with enough non-empty values in key columns)
            # Skip rows where all values are identical (likely a title row spanning merged cells)
            header_row_idx = 0
            for i, row in enumerate(data):
                # Check if this row looks like a header
                # A header row typically has multiple non-None values in the first few columns
                non_empty = sum(1 for cell in row[:min(5, len(row))] if cell is not None and str(cell).strip())
                if non_empty >= 2:
                    # Skip rows where all non-empty values are identical
                    # (these are title rows from merged cells, not actual headers)
                    non_empty_values = [cell for cell in row[:min(5, len(row))] if cell is not None and str(cell).strip()]
                    if len(non_empty_values) > 0 and len(set(str(v) for v in non_empty_values)) > 1:
                        header_row_idx = i
                        break

            # Build headers, using column index if header value is None or empty
            headers = []
            for idx, h in enumerate(data[header_row_idx]):
                if h is None or str(h).strip() == "":
                    headers.append(f"Column_{idx+1}")
                else:
                    headers.append(str(h))
            rows_data = data[header_row_idx + 1:]

            # Create DataFrame
            df = pd.DataFrame(rows_data, columns=headers)

            # Clean the dataframe
            df = df.replace({pd.NA: None, float('nan'): None})

            # Forward fill for hierarchy columns (first 4 columns)
            for col in range(min(4, len(df.columns))):
                df.iloc[:, col] = df.iloc[:, col].ffill()

            # Remove rows that are completely empty or only have NaN values
            if len(df) > 0:
                # Check if ALL columns are None/empty
                all_none_mask = df.apply(lambda row: all(
                    v is None or (isinstance(v, str) and v.strip() == "") for v in row
                ), axis=1)
                df = df[~all_none_mask]

                # Also remove rows where the first column is None/empty
                # AND all other columns have the same value (sub-header rows from merged cells)
                if len(df) > 0 and len(df.columns) >= 2:
                    # Get non-empty values in row (excluding first column)
                    def is_sub_header_row(row):
                        if row.iloc[0] is not None and str(row.iloc[0]).strip() != "":
                            return False  # First col has value, not a sub-header
                        # Check if other columns have content
                        other_values = [row.iloc[i] for i in range(1, len(row)) if row.iloc[i] is not None and str(row.iloc[i]).strip() != ""]
                        if not other_values:
                            return True  # No other content
                        # Check if all non-empty values are the same
                        if len(set(str(v) for v in other_values)) == 1:
                            return True  # All same value, this is a sub-header
                        return False

                    mask = df.apply(lambda row: not is_sub_header_row(row), axis=1)
                    df = df[mask]

                # Remove rows where the first column (usually row identifier) is None
                # but only if ALL data columns are also empty
                if len(df.columns) > 4:
                    data_cols = df.iloc[:, 4:]
                    mask = data_cols.apply(lambda row: any(
                        v is not None and str(v).strip() != "" for v in row
                    ), axis=1)
                    df = df[mask]

            # Generate markdown
            if not df.empty:
                md_table = _dataframe_to_markdown(df, sheet_name)
                md_content += md_table + "\n\n"

        wb.close()

        return DocumentConverterResult(markdown=md_content.strip())


class XlsConverter(DocumentConverter):
    """
    Converts XLS files to Markdown, with each sheet presented as a separate Markdown table.
    """

    def __init__(self):
        super().__init__()
        self._html_converter = HtmlConverter()

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_XLS_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_XLS_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Load the dependencies
        if _xls_dependency_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".xls",
                    feature="xls",
                )
            ) from _xls_dependency_exc_info[
                1
            ].with_traceback(  # type: ignore[union-attr]
                _xls_dependency_exc_info[2]
            )

        sheets = pd.read_excel(file_stream, sheet_name=None, engine="xlrd")
        md_content = ""
        for s in sheets:
            md_content += f"## {s}\n"
            html_content = sheets[s].to_html(index=False)
            md_content += (
                self._html_converter.convert_string(
                    html_content, **kwargs
                ).markdown.strip()
                + "\n\n"
            )

        return DocumentConverterResult(markdown=md_content.strip())
