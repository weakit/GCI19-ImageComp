#!/usr/bin/env python3
import os
import mimetypes
from PIL import Image
from io import BytesIO

RDIR = "./"
SDIR = "compressed/"
maxW = 400  # max width
maxH = 300  # max height
maxS = 64000  # max filesize (in bytes)
VERBOSE = True


def calc_quality(img):
    """Calculate JPEG Quality"""
    # Pretty much tries to guess it.

    f = BytesIO()
    quality = 100
    img.save(f, format='JPEG', quality=quality)

    while f.tell() > maxS:
        quality -= 10
        f = BytesIO()
        img.save(f, format='JPEG', quality=quality)
    
    # possible optimization

    quality += 10
    f = BytesIO()
    img.save(f, format='JPEG', quality=quality)

    while f.tell() > maxS:
        quality -= 1
        f = BytesIO()
        img.save(f, format='JPEG', quality=quality)
    
    return quality


def read_image(name):
    """Reads an image file"""
    return Image.open(os.path.join(RDIR, name)).convert("RGB")


def calc_size(w0, h0):
    """Calculate new image size"""
    if h0 <= maxH and w0 <= maxW:
        return w0, h0
    if h0 > maxH:
        w, h = (maxH / h0) * w0, maxH
    if w > maxW:
        w, h = maxW, (maxW / w) * h
    return round(w), round(h)


def resize(img, w, h):
    """Resizes the image"""
    return img.resize((w, h), resample=Image.LANCZOS)


def byte(num):
    """Converts Data Units"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def compress(file):
    img = read_image(file)
    smol = resize(img, *calc_size(*img.size))
    smol.save(os.path.join(RDIR, SDIR, file), format="JPEG", quality=calc_quality(smol))
    if VERBOSE:
        print(file, '\t', byte(os.stat(os.path.join(RDIR, file)).st_size), '->', byte(os.stat(os.path.join(RDIR, SDIR, file)).st_size))


def mkdir():
    """Make directory to save files in."""
    path = os.path.join(RDIR, SDIR)
    if not os.path.exists(path):
        os.mkdir(path)


def get_images():
    """Gets the list of images in the directory"""
    files = os.listdir(RDIR)
    images = list()
    for f in files:
        if mimetypes.guess_type(f)[0]:
            if mimetypes.guess_type(f)[0].startswith("image"):
                images.append(f)
    return images


if __name__ == "__main__":
    dir = input("Enter directory with images (enter to use working dir.): ")
    if dir:
        if os.path.exists(dir):
            RDIR = dir
        else:
            print("Invalid directory.")
            exit(1)
    images = get_images()
    if images:
        mkdir()
        for image in images:
            compress(image)
