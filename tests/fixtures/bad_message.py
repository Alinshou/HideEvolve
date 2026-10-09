"""Test fixture: decode cannot recover message from caller scope."""


def embed(image, message, key):
    return image.copy()


def decode(attacked_image, key):
    return original_message  # noqa: F821 - intentionally absent
