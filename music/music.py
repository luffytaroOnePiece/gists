#!/usr/bin/env python3
import json
import os
import uuid
from datetime import datetime

METADATA_FILE = "metadata.json"
FILTERS_FILE = "filters.json"

# -------------------------
# CDN BASE URLS
# -------------------------
AUDIO_CDN_BASE = "https://cdn.jsdelivr.net/gh/luffytaroOnePiece/audio/main/"
COVER_CDN_BASE = "https://cdn.jsdelivr.net/gh/luffytaroOnePiece/coverimages/main/"

AUDIO_EXT = ".mp3"
COVER_SUFFIX = "-C"
COVER_EXT = ".jpg"

# -------------------------
# PREDEFINED OPTIONS
# -------------------------
LANGUAGES = [
    "English", "Telugu", "Hindi", "Tamil",
    "Kannada", "Malayalam", "Japanese", "Other"
]

GENRES = [
    "Romance", "Mass", "Melody", "Dance", "Sad",
    "Devotional", "Villain", "Item", "Anime"
]

YOUTUBE_QUALITIES = [
    "144p", "240p", "360p", "480p", "720p",
    "1080p", "1440p", "2160p", "4320p"
]

def load_metadata():
    if not os.path.exists(METADATA_FILE):
        return {"songs": []}

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            print("metadata.json invalid. Creating new.")
            return {"songs": []}

    if "songs" not in data or not isinstance(data["songs"], list):
        data["songs"] = []

    return data


def load_filters():
    """Load existing filters.json or create empty structure."""
    if not os.path.exists(FILTERS_FILE):
        return {
            "languages": [],
            "genres": [],
            "years": [],
            "singers": [],
            "musicBy": [],
            "albums": []
        }

    with open(FILTERS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            print("filters.json invalid. Creating new.")
            return {
                "languages": [],
                "genres": [],
                "years": [],
                "singers": [],
                "musicBy": [],
                "albums": []
            }

    for key in ["languages", "genres", "years", "singers", "musicBy", "albums"]:
        if key not in data or not isinstance(data[key], list):
            data[key] = []

    return data


def save_metadata(db):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("\nSaved metadata.json")


def save_filters(filters):
    # dedupe + sort
    filters["languages"] = sorted(set(filters["languages"]))
    filters["genres"] = sorted(set(filters["genres"]))
    filters["years"] = sorted(set(filters["years"]))
    filters["singers"] = sorted(set(filters["singers"]))
    filters["musicBy"] = sorted(set(filters["musicBy"]))
    filters["albums"] = sorted(set(filters["albums"]))

    with open(FILTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(filters, f, indent=2, ensure_ascii=False)
    print("Saved filters.json")


# -------------------------
# INPUT HELPERS
# -------------------------
def prompt_required(label):
    while True:
        val = input(label).strip()
        if val:
            return val
        print("This field is required.")


def prompt_optional(label):
    return input(label).strip()


def prompt_choice(title, options):
    print(f"\n{title}")
    for i, opt in enumerate(options, start=1):
        print(f" {i}) {opt}")
    print(" 0) Other")

    while True:
        sel = input("Choose: ").strip()
        if sel.isdigit():
            sel = int(sel)
            if sel == 0:
                val = input("Enter custom value: ").strip()
                return val
            if 1 <= sel <= len(options):
                return options[sel - 1]
        print("Invalid. Try again.")


def split_list(text):
    return [x.strip() for x in text.split(",") if x.strip()]


# -------------------------
# CORE LOGIC
# -------------------------
def build_song_entry():
    print("\n--- NEW SONG ---")

    title = prompt_required("Title: ")

    # MULTIPLE SINGERS
    singers_raw = prompt_required("Singers (comma separated): ")
    singers = split_list(singers_raw)

    music_by = prompt_optional("Music by (optional): ")

    language = prompt_choice("Language:", LANGUAGES)

    year_in = input(f"Year [{datetime.now().year}]: ").strip()
    year = int(year_in) if year_in else datetime.now().year

    base_name = prompt_required("Base name for audio & images (ex: NTCH): ")
    album_name = prompt_optional("Album name (optional, for file naming): ")

    # CDN URLs
    audio_url = f"{AUDIO_CDN_BASE}{base_name}{AUDIO_EXT}"
    cover_image = f"{COVER_CDN_BASE}{base_name}{COVER_SUFFIX}{COVER_EXT}"
    album_image = f"{COVER_CDN_BASE}{album_name}{COVER_EXT}"

    album = prompt_optional("Album (optional): ")

    genre = prompt_choice("Genre:", GENRES)

    youtube_url = prompt_optional("YouTube URL (optional): ")
    youtube_format = None
    if youtube_url:
        youtube_format = prompt_choice("YouTube Quality:", YOUTUBE_QUALITIES)

    song = {
        "id": str(uuid.uuid4()),
        "title": title,
        "singers": singers,
        "language": language,
        "year": year,
        "audioUrl": audio_url,
        "coverImage": cover_image,
        "albumImage": album_image
    }

    if album:
        song["album"] = album
    if genre:
        song["genre"] = genre
    if music_by:
        song["musicBy"] = music_by
    if youtube_url:
        song["youtube"] = {"url": youtube_url, "formats": youtube_format}

    return song


def update_filters(filters, song):
    """Update filters dict with unique values from this song."""
    if "language" in song and song["language"]:
        filters["languages"].append(song["language"])

    if "genre" in song and song["genre"]:
        filters["genres"].append(song["genre"])

    if "year" in song and song["year"]:
        filters["years"].append(song["year"])

    if "singers" in song and isinstance(song["singers"], list):
        filters["singers"].extend(song["singers"])

    if "musicBy" in song and song["musicBy"]:
        filters["musicBy"].append(song["musicBy"])

    if "album" in song and song["album"]:
        filters["albums"].append(song["album"])

    return filters


def main():
    db = load_metadata()
    filters = load_filters()

    song = build_song_entry()
    db["songs"].append(song)
    filters = update_filters(filters, song)

    print("\n--- Song Added ---")
    print(json.dumps(song, indent=2, ensure_ascii=False))

    save_metadata(db)
    save_filters(filters)


if __name__ == "__main__":
    main()
