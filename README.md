# Apartment CLI Tool

This is a command-line tool designed for scraping apartment listings and contact info from Google Maps and the web.

## 🔧 What it does
- Scrapes apartments from Google Maps Places API for a given city
- Extracts website URLs via Places API or Google Search fallback
- Attempts to open each website to extract:
 - Email addresses
 - Phone numbers
- Optionally writes the results to a local CSV
- Maintains a cache file per city to avoid redundant API usage

## 🏁 How to run
 ```bash
 python3 src/cli/apartment.py scrape --city "Evanston IL" --pages 2 --api-key <YOUR_GOOGLE_API_KEY>
 ```

## ✅ Example CSV Output

 ```
 place_id,name,address,phone,website,rating,contacted_timestamps,emails,phone,extracted_phones
 ChIJC4qWiajRD4gRsyADh38YCK8,The Vivian,"6807 N Sheridan Rd, Chicago, IL 60626, USA",(872) 256-9612,https://www.vivianchicago.com/?utm_source=GBP&utm_medium=organic&utm_knock=g&doorway=schedule,,,872-810-2614
 ChIJYWBVkDnQD4gRZiUOnBSss18,Stringerapartments.com,"507 Sherman Ave, Evanston, IL 60202, USA",(847) 866-7350,http://stringerapartments.com/,,,847-866-7350
 ...
 ```

## 🔑 Requirements
- You **must provide** a valid Google Maps API key with access to the Places API.
- Run with `--api-key` or set `GOOGLE_API_KEY` environment variable.

## 🧠 Considerations
- This tool does **not** cold email — it just collects data.
- It's intended as a foundational CLI for outreach research.
- Uses both `requests` and a headless Chrome Selenium fallback for robustness.

## 💡 Future Roadmap
- Cold email templating + Gmail/SMTP integration
- Cold calling integration via Twilio or Zoom APIs
- Add support for Yelp and Facebook scraping for additional leads

## 📁 Output Files
- `data/cache_<city>.json`: stores fetched listings and metadata
- `output_<city>.csv`: final CSV with all extracted data

## 💬 CLI Commands
Run `python3 src/cli/apartment.py --help` to see all commands:
 ```
 Commands:
   scrape     Scrape apartments in a city and optionally write results to a spreadsheet.
 ```

## 🧪 Example Use
 ```bash
 python3 src/cli/apartment.py scrape -c "Evanston IL" -p 3 -w -k <YOUR_KEY>
 ```