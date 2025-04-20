import requests
import time


class GoogleMapsClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.text_search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    def search_apartments(self, city, max_pages=3):
        results = []
        token = None
        for _ in range(max_pages):
            params = {
                "query": f"apartments in {city}",
                "key": self.api_key,
            }
            if token:
                params["pagetoken"] = token
                time.sleep(2)

            res = requests.get(self.text_search_url, params=params)
            res.raise_for_status()
            data = res.json()

            results.extend(data.get("results", []))
            token = data.get("next_page_token")
            if not token:
                break

        return results

    def get_place_details(self, place_id):
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,formatted_phone_number,website,rating,opening_hours",
            "key": self.api_key
        }
        res = requests.get(self.details_url, params=params)
        res.raise_for_status()
        return res.json().get("result", {})