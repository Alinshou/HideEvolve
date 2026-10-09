"""Deterministic, configured image attacks for the W02 evaluator."""

from io import BytesIO

import numpy as np
from PIL import Image


def apply_attack(image: np.ndarray, spec: dict) -> np.ndarray:
    operation = spec["operation"]
    if operation == "identity":
        return image.copy()
    picture = Image.fromarray(image)
    if operation == "jpeg":
        with BytesIO() as output:
            picture.save(output, format="JPEG", quality=int(spec["quality"]),
                         subsampling=int(spec["subsampling"]),
                         optimize=bool(spec["optimize"]), progressive=bool(spec["progressive"]))
            output.seek(0)
            with Image.open(output) as decoded:
                return np.asarray(decoded.convert("RGB"), dtype=np.uint8).copy()
    if operation == "rotate":
        result = picture.rotate(float(spec["degrees"]), Image.Resampling.BICUBIC,
                                expand=False, fillcolor=tuple(spec["fill_rgb"]))
        return np.asarray(result, dtype=np.uint8).copy()
    if operation == "scale":
        factor = float(spec["factor"])
        if not 0 < factor <= 2:
            raise ValueError("scale factor must be in (0, 2]")
        width, height = picture.size
        scaled = picture.resize((max(1, round(width * factor)), max(1, round(height * factor))),
                                Image.Resampling.BICUBIC)
        if factor < 1:
            canvas = Image.new("RGB", picture.size, tuple(spec["fill_rgb"]))
            canvas.paste(scaled, ((width-scaled.width)//2, (height-scaled.height)//2))
            result = canvas
        else:
            left = (scaled.width-width)//2
            top = (scaled.height-height)//2
            result = scaled.crop((left, top, left+width, top+height))
        return np.asarray(result, dtype=np.uint8).copy()
    raise ValueError(f"unknown attack operation: {operation}")
