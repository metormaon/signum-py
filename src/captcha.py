from __future__ import print_function

import base64
import glob
import os
import secrets
from io import BytesIO
from os.path import basename
from typing import Dict, Set, Callable

import inflect as inflect
from PIL import Image


def require_singular(folder: str) -> Set[str]:
    return {folder}


def allow_plural(folder: str) -> Set[str]:
    return {folder, inflect.engine().plural(folder)}


def generate_captcha_challenge(image_root_folder: str = "captcha-images",
                               solutions_for_folder: Callable[[str], Set[str]] = allow_plural) -> (str, Set[str]):
    folders = glob.glob(image_root_folder + "/*")

    if not folders:
        raise ValueError("Bad or empty path: " + image_root_folder)

    if len(folders) == 1:
        raise ValueError("Root folder has only one subdirectory: " + image_root_folder)

    for folder in folders:
        file_count = 0

        for extension in ["*.gif", "*.jpg", "*.jpeg", "*.png", "*.tiff", "*.bmp"]:
            file_count += len(glob.glob1(folder, extension))

        if file_count < 3:
            raise ValueError("Not enough images in sub-directory " + folder)

    main_folder = secrets.choice(folders)

    secondary_folder = secrets.choice(folders)

    while secondary_folder == main_folder:
        secondary_folder = secrets.choice(folders)

    images = glob.glob(main_folder + "/*")

    selected_images = set()

    while len(selected_images) < 3:
        selected_images.add(secrets.choice(images))

    selected_images.add(secrets.choice(glob.glob(secondary_folder + "/*")))

    selected_list = list(selected_images)
    secrets.SystemRandom().shuffle(selected_list)

    result = Image.new("RGB", (400, 400))

    for index, file in enumerate(selected_images):
        path = os.path.expanduser(file)
        img = Image.open(path)
        img.thumbnail((200, 200), Image.ANTIALIAS)
        x = index // 2 * 200
        y = index % 2 * 200
        w, h = img.size
        result.paste(img, (x, y, x + w, y + h))

    data = BytesIO()
    result.save(data, "JPEG")
    data64 = base64.b64encode(data.getvalue())

    data_uri = u'data:img/jpeg;base64,' + data64.decode('utf-8')

    solutions = solutions_for_folder(basename(main_folder))

    return data_uri, solutions
