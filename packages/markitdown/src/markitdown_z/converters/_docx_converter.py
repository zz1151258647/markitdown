import sys
import io
import os
import base64
import re
import zipfile
from warnings import warn

from typing import BinaryIO, Any

from ._html_converter import HtmlConverter
from ..converter_utils.docx.pre_process import pre_process_docx
from .._base_converter import DocumentConverterResult
from .._stream_info import StreamInfo
from .._exceptions import MissingDependencyException, MISSING_DEPENDENCY_MESSAGE

# Try loading optional (but in this case, required) dependencies
# Save reporting of any exceptions for later
_dependency_exc_info = None
try:
    import mammoth

except ImportError:
    # Preserve the error and stack trace for later
    _dependency_exc_info = sys.exc_info()


ACCEPTED_MIME_TYPE_PREFIXES = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]

ACCEPTED_FILE_EXTENSIONS = [".docx"]


class DocxConverter(HtmlConverter):
    """
    Converts DOCX files to Markdown. Style information (e.g.m headings) and tables are preserved where possible.
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

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def _fix_html_tables(self, html_content: str) -> str:
        """
        Fix HTML table structure for better markdown conversion.
        - Wraps table rows in <tbody> if missing
        - Removes <p> tags inside <td>/<th> cells
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            for table in soup.find_all("table"):
                # Check if tbody exists
                has_tbody = table.find("tbody") is not None

                if not has_tbody:
                    # Wrap all <tr> elements in <tbody>
                    rows = table.find_all("tr", recursive=False)
                    if rows:
                        tbody = soup.new_tag("tbody")
                        for row in rows:
                            row.extract()
                            tbody.append(row)
                        table.append(tbody)

                # Remove <p> tags inside <td> and <th>
                for cell in table.find_all(["td", "th"]):
                    for p in cell.find_all("p", recursive=False):
                        p.unwrap()
                    # Also handle nested p tags by unwrapping them all
                    for p in cell.find_all("p"):
                        p.unwrap()

            return str(soup)
        except Exception:
            return html_content

    def _extract_images_from_base64(self, html_content: str, output_dir: str, prefix: str = "image") -> tuple:
        """
        Extract base64 encoded images from HTML and save them to files.
        Images are saved to a subdirectory 'images/' within output_dir.
        Returns a tuple of (modified_html_content, images_subdir).
        """
        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        image_counter = 1

        def replace_and_save(match):
            nonlocal image_counter
            img_tag = match.group(0)
            data_match = re.search(r'src="data:image/([^;]+);base64,([^"]+)"', img_tag)
            if data_match:
                mime_type = data_match.group(1)
                base64_data = data_match.group(2)
                ext = self._get_extension_from_mime(mime_type)
                filename = f"{prefix}{image_counter}{ext}"
                filepath = os.path.join(images_dir, filename)

                # Decode and save the image
                try:
                    image_data = base64.b64decode(base64_data)
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                except Exception:
                    pass

                # Replace the src with relative path to images subdirectory
                new_src = f"images/{filename}"
                img_tag = re.sub(r'src="data:image/[^"]+"', f'src="{new_src}"', img_tag)
                image_counter += 1
            return img_tag

        # Replace all base64 img tags and save images
        result = re.sub(r'<img[^>]*src="data:image/[^>]+>', replace_and_save, html_content)
        return result, "images"

    def _get_extension_from_mime(self, mime_type: str) -> str:
        """Get file extension from MIME type."""
        mime_to_ext = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
        }
        return mime_to_ext.get(mime_type, '.png')

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Check: the dependencies
        if _dependency_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".docx",
                    feature="docx",
                )
            ) from _dependency_exc_info[
                1
            ].with_traceback(  # type: ignore[union-attr]
                _dependency_exc_info[2]
            )

        # Check for image extraction options
        extract_images = kwargs.pop('extract_images', False)
        images_output_dir = kwargs.pop('images_output_dir', None)
        images_prefix = kwargs.pop('images_prefix', 'image')
        images_relative_path = kwargs.pop('images_relative_path', None)

        style_map = kwargs.get("style_map", None)
        pre_process_stream = pre_process_docx(file_stream)

        # Convert to HTML using mammoth
        html_result = mammoth.convert_to_html(pre_process_stream, style_map=style_map)
        html_content = html_result.value

        # Fix table structure: mammoth sometimes outputs tables without proper tbody
        # and with <p> tags inside <td> which can cause issues with markdownify
        html_content = self._fix_html_tables(html_content)

        # Extract images if requested
        if extract_images and images_output_dir:
            # Extract base64 images from HTML and save to files
            # Images are saved to output_dir/images/ subdirectory
            html_content, images_subdir = self._extract_images_from_base64(
                html_content, images_output_dir, images_prefix
            )
            # images_subdir is "images", path is already embedded as "images/imgN.png"

        return self._html_converter.convert_string(
            html_content,
            **kwargs,
        )
