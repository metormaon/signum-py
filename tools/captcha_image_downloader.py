# -*- coding: utf-8 -*-
from os import path

from google_images_download import google_images_download

for keyword in [
    "dog", "cat", "bird", "elephant", "fork", "knife", "spoon", "carrot", "orange", "turnip", "tomato", "potato",
    "water", "hair", "table", "chair", "house", "factory", "microwave", "cigarette", "ashtray", "brush", "battery",
    "comb", "box", "book", "bag", "calendar", "computer", "lipstick", "pencil", "perfume", "telephone", "television",
    "headset", "angry", "apple", "armour", "baby", "bag", "ball", "bank", "basket", "bath", "bear", "bean", "bell",
    "blue", "bottle", "bread", "bridge", "bus", "cake", "candle", "car", "card", "cheese", "chicken", "chocolate",
    "circle", "clock", "cloud", "coffee", "coat", "coin", "cook", "corn", "cup", "dance", "deer", "desk", "door",
    "dress", "duck", "happy", "smile", "yellow", "ear", "earth", "mars", "saturn", "jupiter", "egg", "eight", "one",
    "two", "three", "four", "five", "six", "seven", "nine", "ten", "electricity", "piano", "guitar", "flute", "drum",
    "exit", "dark", "excited", "surprise", "eye", "nose", "mouth", "leg", "hand", "face", "family", "farm", "fat",
    "fear", "finger", "fire", "flag", "flower", "fly", "food", "football", "forest", "fox", "friend", "garden", "game",
    "gate"
]:

    if not path.exists("../captcha-images/" + keyword):
        response = google_images_download.googleimagesdownload()

        arguments = {"keywords": keyword,
                     "limit": 15,
                     "print_urls": True,
                     "usage_rights": "labeled-for-reuse",
                     "output_directory": "../captcha-images",
                     "safe_search": True,
                     "format": "jpg",
                     "size": "medium"
                     }

        paths = response.download(arguments)
        print(paths)
    else:
        print("Skipping " + keyword)
