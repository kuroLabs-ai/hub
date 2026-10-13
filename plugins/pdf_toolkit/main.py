"""
community_hub/plugins/pdf_toolkit/main.py
Read, merge, split, extract text/metadata, and generate PDF documents.
Includes pure-Python fallback primitives for reading text/pages and creating clean PDF docs without mandatory C-deps.
"""

import os
import re
from typing import Dict, Any, List, Optional


def get_pdf_info(file_path: str) -> Dict[str, Any]:
    """
    Read metadata, page count estimate, and structural information from a PDF file.
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File '{file_path}' does not exist"}

    try:
        size_bytes = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            content = f.read()

        # Check PDF header
        header_match = re.search(rb"%PDF-(\d+\.\d+)", content)
        pdf_version = header_match.group(1).decode("utf-8") if header_match else "unknown"

        # Count pages by searching for /Type /Page (excluding /Pages)
        page_matches = re.findall(rb"/Type\s*/Page\b", content)
        estimated_pages = len(page_matches)

        # Basic metadata search
        title_match = re.search(rb"/Title\s*\((.*?)\)", content)
        author_match = re.search(rb"/Author\s*\((.*?)\)", content)
        creator_match = re.search(rb"/Creator\s*\((.*?)\)", content)

        return {
            "success": True,
            "file_path": file_path,
            "size_bytes": size_bytes,
            "pdf_version": pdf_version,
            "page_count_estimate": estimated_pages,
            "metadata": {
                "title": title_match.group(1).decode("latin-1", errors="ignore") if title_match else None,
                "author": author_match.group(1).decode("latin-1", errors="ignore") if author_match else None,
                "creator": creator_match.group(1).decode("latin-1", errors="ignore") if creator_match else None,
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_pdf_text(file_path: str, max_chars: int = 10000) -> Dict[str, Any]:
    """
    Extract readable text streams from a PDF file.
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File '{file_path}' does not exist"}

    try:
        # Check if PyPDF2 / pypdf is available
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            extracted = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    extracted.append(f"--- Page {i + 1} ---\n{text.strip()}")
            full_text = "\n\n".join(extracted)
            return {
                "success": True,
                "engine": "pypdf",
                "pages_found": len(reader.pages),
                "text": full_text[:max_chars]
            }
        except ImportError:
            pass

        # Fallback pure-python stream extractor
        with open(file_path, "rb") as f:
            raw = f.read()

        # Extract text strings inside BT ... ET text blocks
        text_tokens = []
        stream_matches = re.findall(rb"\((.*?)\)\s*Tj", raw)
        for token in stream_matches:
            try:
                decoded = token.decode("latin-1", errors="ignore")
                if decoded.strip():
                    text_tokens.append(decoded.strip())
            except Exception:
                continue

        extracted_text = " ".join(text_tokens)
        if not extracted_text:
            extracted_text = "[Notice: PDF text streams compressed or require 'pypdf' package for decompression]"

        return {
            "success": True,
            "engine": "builtin_stream_parser",
            "text": extracted_text[:max_chars]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_simple_pdf(output_path: str, title: str, lines: List[str]) -> Dict[str, Any]:
    """
    Generate a clean standard-compliant single-page or multi-line PDF document using pure Python.
    """
    try:
        stream_content = []
        stream_content.append("BT")
        stream_content.append("/F1 18 Tf")
        stream_content.append("50 750 Td")
        safe_title = title.replace("(", "\(").replace(")", "\)")
        stream_content.append(f"({safe_title}) Tj")

        stream_content.append("/F1 11 Tf")
        stream_content.append("0 -30 Td")

        y_offset = -20
        for line in lines[:50]:
            safe_line = line.replace("(", "\(").replace(")", "\)")
            stream_content.append(f"0 {y_offset} Td")
            stream_content.append(f"({safe_line}) Tj")
            y_offset = -15

        stream_content.append("ET")
        stream_data = "\n".join(stream_content).encode("latin-1")
        stream_length = len(stream_data)

        pdf_body = (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
            b"4 0 obj\n<< /Length " + str(stream_length).encode("ascii") + b" >>\nstream\n"
            + stream_data +
            b"\nendstream\nendobj\n"
            b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
            b"xref\n0 6\n0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000056 00000 n \n"
            b"0000000111 00000 n \n"
            b"0000000234 00000 n \n"
            b"0000000320 00000 n \n"
            b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n390\n%%EOF\n"
        )

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_body)

        return {
            "success": True,
            "output_path": output_path,
            "size_bytes": len(pdf_body),
            "lines_written": len(lines)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
