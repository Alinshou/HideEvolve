"""Test fixture: candidate attempts to read an external image."""


def embed(image, message, key):
    return image.copy()


def decode(attacked_image, key):
    with open(r"C:\Users\21882\VS.project\Foundation Model Agent\data\raw\coco\val2017\000000000139.jpg", "rb") as file:
        file.read(1)
    return [0] * 32
