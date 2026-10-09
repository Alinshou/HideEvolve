"""Keyed 8x8 blue-channel DCT/QIM, for contract smoke tests only."""

import numpy as np
from scipy.fft import dctn, idctn

BITS = 32
BLOCK = 8
GRID = 256 // BLOCK
DELTA = 32.0


def _blocks(key):
    seed = int.from_bytes(key, "big")
    return np.random.default_rng(seed).choice(GRID * GRID, size=BITS, replace=False)


def _coset(value, bit):
    return DELTA * (2 * np.rint((value / DELTA - bit) / 2) + bit)


def embed(image, message, key):
    result = image.copy()
    for block, bit in zip(_blocks(key), message):
        row, col = divmod(int(block), GRID)
        part = result[row * BLOCK:(row + 1) * BLOCK, col * BLOCK:(col + 1) * BLOCK, 2].astype(np.float64)
        coeff = dctn(part, norm="ortho")
        coeff[2, 3] = _coset(coeff[2, 3], int(bit))
        encoded = idctn(coeff, norm="ortho")
        result[row * BLOCK:(row + 1) * BLOCK, col * BLOCK:(col + 1) * BLOCK, 2] = np.clip(np.rint(encoded), 0, 255).astype(np.uint8)
    return result


def decode(attacked_image, key):
    bits = []
    for block in _blocks(key):
        row, col = divmod(int(block), GRID)
        part = attacked_image[row * BLOCK:(row + 1) * BLOCK, col * BLOCK:(col + 1) * BLOCK, 2].astype(np.float64)
        value = dctn(part, norm="ortho")[2, 3]
        bits.append(int(np.rint(value / DELTA)) & 1)
    return np.asarray(bits, dtype=np.uint8)
