"""Test fixture: candidate embed never returns."""


def embed(image, message, key):
    while True:
        pass


def decode(attacked_image, key):
    return [0] * 32
