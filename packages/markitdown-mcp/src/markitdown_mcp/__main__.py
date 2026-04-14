import contextlib
import sys
import os
from collections.abc import AsyncIterator
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send
from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from markitdown import MarkItDown
import uvicorn

# Initialize FastMCP server for MarkItDown (SSE)
mcp = FastMCP("markitdown")


def _convert_uri(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Internal helper to convert a URI to markdown.

    Args:
        uri: The URI of the resource to convert (http:, https:, file: or data:).
        extract_images: Whether to extract images from the document to a folder.
        images_output_dir: Output directory for extracted images.
        images_prefix: Prefix for extracted image filenames.
        output_markdown_path: If provided, save the markdown to this file path.
    """
    result = MarkItDown(enable_plugins=check_plugins_enabled()).convert_uri(
        uri,
        extract_images=extract_images,
        images_output_dir=images_output_dir,
        images_prefix=images_prefix,
    )

    if output_markdown_path:
        os.makedirs(os.path.dirname(output_markdown_path) or ".", exist_ok=True)
        with open(output_markdown_path, "w", encoding="utf-8") as f:
            f.write(result.markdown)

    return result.markdown


@mcp.tool()
async def docx_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert DOCX (Word) files to markdown. Supports extracting images.

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract images from the document (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def pdf_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert PDF files to markdown. Supports extracting images.

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract images from the document (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def xlsx_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert XLSX (Excel) files to markdown. Supports extracting embedded images.

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract images from the document (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def pptx_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert PPTX (PowerPoint) files to markdown. Supports extracting images.

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract images from the document (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def html_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert HTML files to markdown. Supports extracting images.

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract images from the document (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def image_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert image files to markdown (using OCR). Supports PNG, JPG, GIF, BMP, WEBP.

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract/OCR images (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def text_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert plain text files to markdown.

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract images (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def markdown_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert Markdown files (outputs as-is with image extraction if needed).

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract images (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def epub_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert EPUB ebooks to markdown. Supports extracting images.

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract images from the document (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def csv_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert CSV files to markdown tables.

    Args:
        uri: The URI of the resource (http:, https:, file: or data:).
        extract_images: Whether to extract images (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


@mcp.tool()
async def convert_to_markdown(
    uri: str,
    extract_images: bool = True,
    images_output_dir: str = "./images",
    images_prefix: str = "img",
    output_markdown_path: str = None,
) -> str:
    """Convert any supported file (docx, pdf, xlsx, pptx, html, image, text, epub, csv, etc.) to markdown.

    This is a universal converter that auto-detects the file type.

    Args:
        uri: The URI of the resource to convert (http:, https:, file: or data:).
        extract_images: Whether to extract images from the document (default: True).
        images_output_dir: Output directory for extracted images (default: ./images).
        images_prefix: Prefix for extracted image filenames (default: img).
        output_markdown_path: If provided, save the markdown to this file path.
    """
    return _convert_uri(uri, extract_images, images_output_dir, images_prefix, output_markdown_path)


def check_plugins_enabled() -> bool:
    return os.getenv("MARKITDOWN_ENABLE_PLUGINS", "false").strip().lower() in (
        "true",
        "1",
        "yes",
    )


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    sse = SseServerTransport("/messages/")
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            print("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                print("Application shutting down...")

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/mcp", app=handle_streamable_http),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        lifespan=lifespan,
    )


# Main entry point
def main():
    import argparse

    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="Run a MarkItDown MCP server")

    parser.add_argument(
        "--http",
        action="store_true",
        help="Run the server with Streamable HTTP and SSE transport rather than STDIO (default: False)",
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="(Deprecated) An alias for --http (default: False)",
    )
    parser.add_argument(
        "--host", default=None, help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help="Port to listen on (default: 3001)"
    )
    args = parser.parse_args()

    use_http = args.http or args.sse

    if not use_http and (args.host or args.port):
        parser.error(
            "Host and port arguments are only valid when using streamable HTTP or SSE transport (see: --http)."
        )
        sys.exit(1)

    if use_http:
        host = args.host if args.host else "127.0.0.1"
        if args.host and args.host not in ("127.0.0.1", "localhost"):
            print(
                "\n"
                "WARNING: The server is being bound to a non-localhost interface "
                f"({host}).\n"
                "This exposes the server to other machines on the network or Internet.\n"
                "The server has NO authentication and runs with your user's privileges.\n"
                "Any process or user that can reach this interface can read files and\n"
                "fetch network resources accessible to this user.\n"
                "Only proceed if you understand the security implications.\n",
                file=sys.stderr,
            )
        starlette_app = create_starlette_app(mcp_server, debug=True)
        uvicorn.run(
            starlette_app,
            host=host,
            port=args.port if args.port else 3001,
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
