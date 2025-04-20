import typer
from src.lib.apartment_functionalities.apartment_scraper import ApartmentScraper

app = typer.Typer(help="Apartment CLI tool. E.g. to scrape listings and optionally write to a spreadsheet")

@app.command("scrape")
def scrape_apartments(
        city: str = typer.Option(..., "--city", "-c", help="City to search (e.g. Evanston IL)"),
        pages: int = typer.Option(1, "--pages", "-p", min=1, max=10, help="How many pages to search (max 10)"),
        write: bool = typer.Option(False, "--write", "-w", help="Skip prompt and write directly"),
        google_api_key: str = typer.Option(..., "--api-key", "-k", help="Google Maps API key"),
):
    """
    Scrape apartments in a city and optionally write results to a spreadsheet.
    """
    scraper = ApartmentScraper(city=city, pages=pages, write=write, google_api_key=google_api_key)
    scraper.scrape()

@app.command("get_author")
def get_author():
    """
    Get the author of the script.
    """
    print("Author: Michael Askndafi")

if __name__ == "__main__":
    app()