"""Keyed spatial blue-channel LSB, for contract smoke tests only."""

import numpy as np

BITS = 32


def _positions(key):
    seed = int.from_bytes(key, "big")
    return np.random.default_rng(seed).choice(256 * 256, size=BITS, replace=False)


def embed(image, message, key):
    result = image.copy()
    blue = result[:, :, 2].reshape(-1)
    for position, bit in zip(_positions(key), message):
        blue[position] = (int(blue[position]) & 0xFE) | int(bit)
    return result


def decode(attacked_image, key):
    blue = attacked_image[:, :, 2].reshape(-1)
    return np.asarray([blue[position] & 1 for position in _positions(key)], dtype=np.uint8)
