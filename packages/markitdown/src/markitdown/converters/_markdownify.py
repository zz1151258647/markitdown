import re
import copy
import markdownify

from typing import Any, Optional
from urllib.parse import quote, unquote, urlparse, urlunparse
from bs4 import BeautifulSoup


class _CustomMarkdownify(markdownify.MarkdownConverter):
    """
    A custom version of markdownify's MarkdownConverter. Changes include:

    - Altering the default heading style to use '#', '##', etc.
    - Removing javascript hyperlinks.
    - Truncating images with large data:uri sources.
    - Ensuring URIs are properly escaped, and do not conflict with Markdown syntax
    - Fixing table header detection: first row with content is treated as header
      (mammoth outputs all-<td> tables, so we can't rely on <th> tags).
    - Numbering images sequentially as 图 1, 图 2, etc.
    """

    def __init__(self, **options: Any):
        options["heading_style"] = options.get("heading_style", markdownify.ATX)
        options["keep_data_uris"] = options.get("keep_data_uris", False)
        # Explicitly cast options to the expected type if necessary
        super().__init__(**options)
        self._image_counter = 0
        self._table_sep_added = False

    def convert_hn(
        self,
        n: int,
        el: Any,
        text: str,
        convert_as_inline: Optional[bool] = False,
        **kwargs,
    ) -> str:
        """Same as usual, but be sure to start with a new line"""
        if not convert_as_inline:
            if not re.search(r"^\n", text):
                return "\n" + super().convert_hn(n, el, text, convert_as_inline)  # type: ignore

        return super().convert_hn(n, el, text, convert_as_inline)  # type: ignore

    def convert_a(
        self,
        el: Any,
        text: str,
        convert_as_inline: Optional[bool] = False,
        **kwargs,
    ):
        """Same as usual converter, but removes Javascript links and escapes URIs."""
        prefix, suffix, text = markdownify.chomp(text)  # type: ignore
        if not text:
            return ""

        if el.find_parent("pre") is not None:
            return text

        href = el.get("href")
        title = el.get("title")

        # Escape URIs and skip non-http or file schemes
        if href:
            try:
                parsed_url = urlparse(href)  # type: ignore
                if parsed_url.scheme and parsed_url.scheme.lower() not in ["http", "https", "file"]:  # type: ignore
                    return "%s%s%s" % (prefix, text, suffix)
                href = urlunparse(parsed_url._replace(path=quote(unquote(parsed_url.path))))  # type: ignore
            except ValueError:  # It's not clear if this ever gets thrown
                return "%s%s%s" % (prefix, text, suffix)

        # For the replacement see #29: text nodes underscores are escaped
        if (
            self.options["autolinks"]
            and text.replace(r"\_", "_") == href
            and not title
            and not self.options["default_title"]
        ):
            # Shortcut syntax
            return "<%s>" % href
        if self.options["default_title"] and not title:
            title = href
        title_part = ' "%s"' % title.replace('"', r"\"") if title else ""
        return (
            "%s[%s](%s%s)%s" % (prefix, text, href, title_part, suffix)
            if href
            else text
        )

    def convert_img(
        self,
        el: Any,
        text: str,
        convert_as_inline: Optional[bool] = False,
        **kwargs,
    ) -> str:
        """Same as usual converter, but removes data URIs"""

        alt = el.attrs.get("alt", None) or ""
        src = el.attrs.get("src", None) or el.attrs.get("data-src", None) or ""
        title = el.attrs.get("title", None) or ""
        title_part = ' "%s"' % title.replace('"', r"\"") if title else ""
        # Remove all line breaks from alt
        alt = alt.replace("\n", " ")
        if (
            convert_as_inline
            and el.parent.name not in self.options["keep_inline_images_in"]
        ):
            return alt

        # Remove dataURIs
        if src.startswith("data:") and not self.options["keep_data_uris"]:
            src = src.split(",")[0] + "..."

        return "![%s](%s%s)" % (alt, src, title_part)

    def convert_input(
        self,
        el: Any,
        text: str,
        convert_as_inline: Optional[bool] = False,
        **kwargs: Any,
    ) -> str:
        """Convert checkboxes to Markdown [x]/[ ] syntax."""

        if el.get("type") == "checkbox":
            return "[x] " if el.has_attr("checked") else "[ ] "
        return ""



    def convert_table(self, el: Any, text: str, parent_tags: Any, **kwargs: Any) -> str:
        # Reset separator flag at start of each table
        self._table_sep_added = False
        return super().convert_table(el, text, parent_tags, **kwargs)

    def _expand_rowspan(self, table: Any) -> None:
        """
        Expand all rowspan cells into explicit cells so the HTML table becomes
        a regular rectangular grid (no missing cells due to rowspan).
        For merged cells in Word, the content is repeated in each row the cell spans.
        """
        try:
            rows = table.find_all("tr")
            if not rows:
                return

            # Calculate max columns by summing colspan of each row
            max_cols = 0
            for row in rows:
                cells = row.find_all(["td", "th"])
                col_count = sum(int(cell.get("colspan", 1) or 1) for cell in cells)
                max_cols = max(max_cols, col_count)

            if max_cols == 0:
                return

            # rowspan_state tracks ongoing rowspans: (content, rows_left)
            rowspan_state: list[Any] = [None] * max_cols
            grid: list[list[Any]] = []

            for row in rows:
                raw_cells = row.find_all(["td", "th"])
                if not raw_cells:
                    continue

                new_row_cells: list[Any] = [None] * max_cols
                new_state: list[Any] = [None] * max_cols
                filled_columns: set[int] = set()

                # First pass: for each column, output rowspan OR process new cell
                col = 0
                raw_idx = 0
                while col < max_cols:
                    # If there's an active rowspan at this column, output it first
                    if rowspan_state[col] is not None:
                        rows_left = rowspan_state[col][1] - 1
                        new_row_cells[col] = ("span", rowspan_state[col][0])
                        if rows_left > 0:
                            new_state[col] = (rowspan_state[col][0], rows_left)
                        rowspan_state[col] = None  # Clear after outputting
                        col += 1
                    elif raw_idx < len(raw_cells):
                        # No active rowspan, place new cell
                        cell = raw_cells[raw_idx]
                        raw_idx += 1
                        colspan = int(cell.get("colspan", 1) or 1)
                        rowspan = int(cell.get("rowspan", 1) or 1)
                        cell_html = cell.decode_contents()

                        # Handle all columns this cell spans (including colspan > 1)
                        for cs in range(colspan):
                            if col + cs >= max_cols:
                                break
                            filled_columns.add(col + cs)
                            new_row_cells[col + cs] = ("real", cell_html)
                            # Set rowspan state for next row
                            if rowspan > 1:
                                new_state[col + cs] = (cell_html, rowspan - 1)
                        col += colspan
                    else:
                        # No rowspan and no more cells
                        col += 1

                # Second pass: for filled columns with old rowspans, decrement
                # (these rowspans were replaced by new cells in this row)
                for c in filled_columns:
                    if rowspan_state[c] is not None:
                        rows_left = rowspan_state[c][1] - 1
                        if rows_left > 0 and new_state[c] is None:
                            new_state[c] = (rowspan_state[c][0], rows_left)
                        # If new_state[c] is already set (new cell has rowspan), keep it

                rowspan_state = new_state
                grid.append(new_row_cells)

            # Replace original rows with expanded grid
            for r in table.find_all("tr"):
                r.decompose()

            # Replace original rows with expanded grid
            for r in table.find_all("tr"):
                r.decompose()

            soup = BeautifulSoup("", "html.parser")
            for row_cells in grid:
                # Skip rows that have no real content
                has_content = any(cell is not None and cell[0] == "real" and cell[1].strip() for cell in row_cells)
                if not has_content:
                    continue

                new_tr = soup.new_tag("tr")
                for c in range(max_cols):
                    cell = row_cells[c]
                    td = soup.new_tag("td")
                    if cell is not None and cell[1].strip():
                        td.append(BeautifulSoup(cell[1], "html.parser"))
                    new_tr.append(td)
                table.append(new_tr)
        except Exception:
            # If rowspan expansion fails, fall back to original table
            pass

    def convert_tr(
        self,
        el: Any,
        text: str,
        parent_tags: Any,
        **kwargs: Any,
    ) -> str:
        """
        Override to fix table row conversion.
        - Removes the erroneous empty header row that markdownify adds for all-<td> tables
        - Ensures proper separator line placement
        """
        from markdownify import MarkdownConverter

        # Get all cells in this row
        cells = el.find_all(['td', 'th'])
        if not cells:
            return ''

        # Check if this is the first row
        is_first_row = el.find_previous_sibling("tr") is None

        # Check if row contains <th> cells
        is_headrow = all(cell.name == 'th' for cell in cells)

        # Calculate colspan
        full_colspan = 0
        for cell in cells:
            colspan = cell.get('colspan', '1')
            full_colspan += int(colspan) if colspan.isdigit() else 1

        # Build the markdown for this row
        # Get cell contents by converting each cell
        cell_contents = []
        for cell in cells:
            colspan = int(cell.get('colspan', '1') or '1')
            cell_text = cell.get_text(separator=' ', strip=True)
            cell_md = f" {cell_text} "
            # Handle colspan by repeating the cell markdown
            for _ in range(colspan):
                cell_contents.append(cell_md)

        row_text = '|' + '|'.join(cell_contents) + '|'

        # Build the result
        result_lines = []

        # Add separator line after header row (not before)
        if is_first_row:
            if is_headrow:
                # Standard case: <th> first row -> add separator below
                result_lines.append(row_text)
                result_lines.append('| ' + ' | '.join(['---'] * full_colspan) + ' |')
            else:
                # All-<td> case (mammoth): first row is header, add separator below
                result_lines.append(row_text)
                result_lines.append('| ' + ' | '.join(['---'] * full_colspan) + ' |')
                self._table_sep_added = True
        else:
            # Not first row
            if not self._table_sep_added:
                # Should not happen normally, but add separator if missing
                result_lines.append('| ' + ' | '.join(['---'] * full_colspan) + ' |')
                self._table_sep_added = True
            result_lines.append(row_text)

        return '\n'.join(result_lines) + '\n'

    def convert_strong(self, el: Any, text: str, parent_tags: Any, **kwargs: Any) -> str:
        """
        Override: when <img> is inside <strong>, skip ** wrapping.
        The text is typically empty (the <strong> only contains <img>).
        We return text as-is — convert_img will output the figure number.
        """
        # Check if any <img> is a direct or nested child
        if el.find("img") is not None:
            # No bold wrapping — convert_img will add the figure number
            # (text is usually empty since <strong> only contains <img>)
            return text
        return super().convert_strong(el, text, parent_tags, **kwargs)

    def convert_img(self, el: Any, text: str, parent_tags: Any, **kwargs: Any) -> str:
        """
        Same as usual converter, but:
        - Removes data URIs (truncates to ...)
        - Adds sequential figure number: 图 N (only when NOT inside <strong>)
        When inside <strong>, text (图 N) is handled by convert_strong via textify.
        """
        alt = el.attrs.get("alt", None) or ""
        src = el.attrs.get("src", None) or el.attrs.get("data-src", None) or ""
        title = el.attrs.get("title", None) or ""
        title_part = ' "%s"' % title.replace('"', r"\"") if title else ""

        # Remove all line breaks from alt
        alt = alt.replace("\n", " ")

        if (
            "_inline" in parent_tags
            and el.parent.name not in self.options["keep_inline_images_in"]
        ):
            return alt

        # Truncate data URIs
        if src.startswith("data:") and not self.options["keep_data_uris"]:
            src = "... (base64 image)"

        # Number images sequentially (disabled - just return the image tag)
        # self._image_counter += 1
        # fig_num = self._image_counter

        return f"![{alt}]({src}{title_part})"

    def convert_soup(self, soup: Any) -> str:
        # Reset counters for each top-level conversion
        self._image_counter = 0
        self._table_sep_added = False
        # Expand rowspan for all tables BEFORE processing, because convert_soup
        # caches children_to_convert before convert_table is called
        for table in soup.find_all("table"):
            self._expand_rowspan(table)
        return super().convert_soup(soup)  # type: ignore
