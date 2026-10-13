"""
community_hub/plugins/image_processor/main.py
Resize, compress, convert, crop, and inspect image formats.
Supports PIL/Pillow when installed, and provides pure-python format inspection fallbacks.
"""

import os
import struct
from typing import Dict, Any, Tuple, Optional


def get_image_info(file_path: str) -> Dict[str, Any]:
    """
    Get image format, dimensions (width, height), and file size.
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File '{file_path}' does not exist"}

    size_bytes = os.path.getsize(file_path)

    # Try Pillow if present
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            return {
                "success": True,
                "file_path": file_path,
                "size_bytes": size_bytes,
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height
            }
    except ImportError:
        pass
    except Exception as e:
        return {"success": False, "error": f"Image open failed: {str(e)}"}

    # Pure Python header detection for PNG, JPEG, GIF
    try:
        with open(file_path, "rb") as f:
            data = f.read(30)

        # PNG
        if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
            w, h = struct.unpack(">II", data[16:24])
            return {
                "success": True,
                "file_path": file_path,
                "size_bytes": size_bytes,
                "format": "PNG",
                "width": w,
                "height": h
            }
        # GIF
        elif data[:6] in (b"GIF87a", b"GIF89a"):
            w, h = struct.unpack("<HH", data[6:10])
            return {
                "success": True,
                "file_path": file_path,
                "size_bytes": size_bytes,
                "format": "GIF",
                "width": w,
                "height": h
            }
        # JPEG basic detection
        elif data.startswith(b"\xff\xd8"):
            return {
                "success": True,
                "file_path": file_path,
                "size_bytes": size_bytes,
                "format": "JPEG",
                "width": None,
                "height": None,
                "notice": "Exact dimensions require Pillow"
            }
        else:
            return {
                "success": True,
                "file_path": file_path,
                "size_bytes": size_bytes,
                "format": "unknown",
                "width": None,
                "height": None
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def resize_image(
    input_path: str,
    output_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    keep_aspect: bool = True
) -> Dict[str, Any]:
    """
    Resize an image to specified width and height.
    Requires Pillow.
    """
    try:
        from PIL import Image
    except ImportError:
        return {
            "success": False,
            "error": "Image resizing requires 'Pillow'. Install via `pip install Pillow`."
        }

    if not os.path.exists(input_path):
        return {"success": False, "error": f"File '{input_path}' not found."}

    try:
        with Image.open(input_path) as img:
            orig_w, orig_h = img.size

            if width and height and keep_aspect:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
                new_w, new_h = img.size
            elif width and height and not keep_aspect:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                new_w, new_h = width, height
            elif width and not height:
                ratio = width / float(orig_w)
                new_h = int(float(orig_h) * ratio)
                img = img.resize((width, new_h), Image.Resampling.LANCZOS)
                new_w = width
            elif height and not width:
                ratio = height / float(orig_h)
                new_w = int(float(orig_w) * ratio)
                img = img.resize((new_w, height), Image.Resampling.LANCZOS)
                new_h = height
            else:
                return {"success": False, "error": "Provide at least width or height."}

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            img.save(output_path)

            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "original_dimensions": [orig_w, orig_h],
                "new_dimensions": [new_w, new_h],
                "new_size_bytes": os.path.getsize(output_path)
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def convert_and_compress(
    input_path: str,
    output_path: str,
    format: str = "JPEG",
    quality: int = 85,
    optimize: bool = True
) -> Dict[str, Any]:
    """
    Convert image format (e.g. PNG to WEBP/JPEG) and compress quality.
    """
    try:
        from PIL import Image
    except ImportError:
        return {
            "success": False,
            "error": "Image compression requires 'Pillow'. Install via `pip install Pillow`."
        }

    if not os.path.exists(input_path):
        return {"success": False, "error": f"File '{input_path}' not found."}

    try:
        target_fmt = format.upper()
        with Image.open(input_path) as img:
            # If saving to JPEG, convert RGBA to RGB
            if target_fmt in ("JPEG", "JPG") and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            img.save(output_path, format=target_fmt, quality=quality, optimize=optimize)

            orig_size = os.path.getsize(input_path)
            new_size = os.path.getsize(output_path)
            savings_pct = round((1 - (new_size / orig_size)) * 100, 2) if orig_size > 0 else 0

            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "format": target_fmt,
                "original_size_bytes": orig_size,
                "compressed_size_bytes": new_size,
                "saved_percent": savings_pct
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
