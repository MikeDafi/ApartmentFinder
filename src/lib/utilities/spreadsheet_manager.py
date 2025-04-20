import csv
import json
import os


class SpreadsheetManager:
    def __init__(self, filename="apartments.csv"):
        self.filename = filename
        self.fieldnames = [
            "place_id", "name", "address", "phone", "website", "contacted_timestamps", "emails", "extracted_phones"
        ]

    def load_existing_place_ids(self):
        if not os.path.exists(self.filename):
            return set()
        with open(self.filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["place_id"] for row in reader}

    def append_rows(self, rows):
        write_mode = "a" if os.path.exists(self.filename) else "w"
        with open(self.filename, write_mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            if write_mode == "w":
                writer.writeheader()
            writer.writerows(rows)


def cache_file_path(city):
    slug = city.lower().replace(" ", "_")
    return CACHE_DIR / f"cache_{slug}.json"


def load_cache(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)