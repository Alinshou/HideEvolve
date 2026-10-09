"""Test fixture: candidate crashes."""


def embed(image, message, key):
    raise RuntimeError("intentional test failure")


def decode(attacked_image, key):
    return [0] * 32
