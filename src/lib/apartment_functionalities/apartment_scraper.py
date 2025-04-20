import logging
from pathlib import Path
import json
from typer import confirm
from rich.console import Console
from rich.table import Table
from lib.utilities.spreadsheet_manager import SpreadsheetManager
from lib.utilities.google_maps import GoogleMapsClient
from lib.utilities.website_resolver import WebsiteResolver
from lib.utilities.info_resolver_website import InfoResolverWebsite



class ApartmentScraper:
    def __init__(self, city: str, pages: int, write: bool, google_api_key: str):
        self.city = city
        self.pages = pages
        self.write = write
        self.google_api_key = google_api_key
        self.maps = GoogleMapsClient(google_api_key)
        self.sheet = SpreadsheetManager()
        self.website_resolver = WebsiteResolver()
        self.info_finder = InfoResolverWebsite()
        self.cache_path = self._get_cache_file_path()
        self.cache = self._load_cache()
        self.console = Console()

    def _get_cache_file_path(self):
        slug = self.city.lower().replace(" ", "_")
        path = Path("data") / f"cache_{slug}.json"
        path.parent.mkdir(exist_ok=True)
        return path

    def _load_cache(self):
        if self.cache_path.exists():
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=2)

    def _fetch_search_results(self):
        try:
            return self.maps.search_apartments(self.city, self.pages)
        except Exception as e:
            self.console.print(f"[red]❌ Error during text search:[/red] {e}")
            return []

    def _fetch_and_cache_details(self, new_places):
        for place in new_places:
            pid = place["place_id"]
            self.console.print(f"📥 Fetching: [bold]{place['name']}[/bold]...")
            try:
                details = self.maps.get_place_details(pid)
            except Exception as e:
                self.console.print(f"[red]❌ Failed to get details for {pid}[/red]: {e}")
                continue

            websites = self.website_resolver.resolve(details.get("name")) if not details.get("website") else [details.get("website")]
            contacted = ';'.join(self.cache[pid]["contacted_timestamps"]) if pid in self.cache and "contacted_timestamps" in self.cache[pid] else ''

            info = self.info_finder.resolve(websites)
            self.cache[pid] = {
                "place_id": pid,
                "name": details.get("name", ""),
                "address": details.get("formatted_address", ""),
                "phone": details.get("formatted_phone_number", ""),
                "website": ';'.join(websites),
                "contacted_timestamps": contacted,
                "emails": ';'.join(info["emails"]),
                "extracted_phones": ';'.join(info["phones"]),
            }
            self._save_cache()

    def _filter_new_places(self, search_results):
        old_places = {place["place_id"] for place in search_results if place["place_id"] in self.cache}
        if old_places:
            logging.info(f"Ignoring these old places as they've already been found: {old_places}")
        return [place for place in search_results if place["place_id"] not in old_places]

    def _preview_results(self, to_write):
        table = Table(title="New Apartments to Add")
        table.add_column("Name", style="cyan")
        table.add_column("Address", style="green")
        table.add_column("Website", style="magenta")

        for row in to_write:
            table.add_row(row["name"], row["address"], (';'.join(row["website"]) if isinstance(row["website"], list) else row["website"]) or "")

        self.console.print(f"\n📝 [bold]{len(to_write)}[/bold] new apartments found:")
        self.console.print(table)

    def _confirm_write(self):
        return confirm("Do you want to write these results to the spreadsheet?")

    def scrape(self):
        self.console.print(f"\n🔍 Searching for apartments in [bold cyan]{self.city}[/bold cyan]...")

        search_results = self._fetch_search_results()
        if not search_results:
            return

        existing_ids = self.sheet.load_existing_place_ids()
        new_places = self._filter_new_places(search_results)
        self._fetch_and_cache_details(new_places)

        to_write = [v for k, v in self.cache.items() if k not in existing_ids]

        if not to_write:
            self.console.print("\n✅ All results are already stored. Nothing new to write.")
            return

        self._preview_results(to_write)

        if not self.write:
            if not self._confirm_write():
                self.console.print("🚫 Cancelled. You can rerun later, data is cached.")
                return

        self.sheet.append_rows(to_write)
        self.console.print(f"\n✅ [green]{len(to_write)}[/green] new apartments written to [bold]{self.sheet.filename}[/bold].")
        self.console.print(f"📦 Cached data stored in: [dim]{self.cache_path}[/dim]")
