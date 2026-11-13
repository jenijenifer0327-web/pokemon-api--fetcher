import requests
import json
import os
from datetime import datetime, timezone, timedelta

# Project settings
API_URL = "https://pokeapi.co/api/v2/pokemon/"
CACHE_FILE = "cache.json"
CACHE_EXPIRY = 300  # 5 minutes


# Load cache from JSON file
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            print("Cache file is invalid. Creating a new cache.")
    return {}


# Save cache into JSON file
def save_cache(cache):
    try:
        with open(CACHE_FILE, "w") as file:
            json.dump(cache, file, indent=4)
    except OSError as error:
        print("Unable to save cache:", error)


# Check whether cache is valid
def get_cached_data(pokemon_name):
    cache = load_cache()

    if pokemon_name in cache:
        cached_time = datetime.fromisoformat(
            cache[pokemon_name]["timestamp"]
        )

        current_time = datetime.now(timezone.utc)
        expiry_time = cached_time + timedelta(seconds=CACHE_EXPIRY)

        if current_time < expiry_time:
            print("\nData loaded from CACHE!")
            return cache[pokemon_name]["data"]

        else:
            print("\nCache expired. Fetching fresh data...")
    return None


# Fetch data from API
def fetch_pokemon(pokemon_name):
    cached_data = get_cached_data(pokemon_name)

    if cached_data is not None:
        return cached_data

    try:
        print("\nFetching data from API...")

        url = API_URL + pokemon_name.lower()
        response = requests.get(url, timeout=10)

        if response.status_code == 404:
            print("Pokemon not found!")
            return None

        response.raise_for_status()

        data = response.json()

        # Extract required details
        pokemon_info = {
            "name": data["name"],
            "id": data["id"],
            "height": data["height"],
            "weight": data["weight"],
            "types": [
                item["type"]["name"]
                for item in data["types"]
            ],
            "abilities": [
                item["ability"]["name"]
                for item in data["abilities"]
            ]
        }

        # Save data into cache
        cache = load_cache()

        cache[pokemon_name.lower()] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": pokemon_info
        }

        save_cache(cache)

        return pokemon_info

    except requests.exceptions.Timeout:
        print("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        print("Internet connection error!")
    except requests.exceptions.HTTPError as error:
        print("HTTP error:", error)
    except requests.exceptions.RequestException as error:
        print("API request failed:", error)
    except (ValueError, KeyError, TypeError) as error:
        print("Unable to process API data:", error)

    return None


# Display Pokemon details
def display_pokemon(data):
    if data is None:
        return

    print("\n========== POKEMON DETAILS ==========")

    print("Name      :", data["name"].capitalize())
    print("ID        :", data["id"])
    print("Height    :", data["height"])
    print("Weight    :", data["weight"])
    print("Types     :", ", ".join(data["types"]))
    print("Abilities :", ", ".join(data["abilities"]))

    print("=====================================")


# Main program
def main():
    print("================================")
    print("   POKEMON API FETCHER")
    print("================================")

    while True:
        print("\n1. Search Pokemon")
        print("2. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            pokemon_name = input(
                "Enter Pokemon name: "
            ).strip().lower()

            if not pokemon_name:
                print("Please enter a Pokemon name!")
                continue

            data = fetch_pokemon(pokemon_name)
            display_pokemon(data)

        elif choice == "2":
            print("Thank you for using Pokemon API Fetcher!")
            break

        else:
            print("Invalid choice! Please select 1 or 2.")


if __name__ == "__main__":
    main()
