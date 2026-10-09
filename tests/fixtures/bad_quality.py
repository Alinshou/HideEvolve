"""Test fixture: destroys the image and violates PSNR."""


def embed(image, message, key):
    return image * 0


def decode(attacked_image, key):
    return [0] * 32
