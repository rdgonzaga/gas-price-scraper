# Gas Price Scraper

Simple Python scrapers for GasWatchPH city pages, plus a merge script.

## Files

- manila-gas-scraper.py: Scrapes Manila station prices and summary
- quezon-city-gas-scraper.py: Scrapes Quezon City station prices and summary
- merge_city_data.py: Merges Manila and Quezon City CSV outputs

## Install

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

python -m pip install -r requirements.txt

3. Install Playwright browser:

python -m playwright install chromium

## Run

Scrape Manila:

python manila-gas-scraper.py

Scrape Quezon City:

python quezon-city-gas-scraper.py

Merge both city outputs:

python merge_city_data.py

## Get Coordinates (Latitude/Longitude)

Leaflet is a map library and needs coordinates. Use geocode_stations.py to convert station names into coordinates using OpenStreetMap Nominatim.

Geocode merged file (recommended):

python geocode_stations.py --input merged_manila_quezon_city_gas_prices.csv --output merged_manila_quezon_city_gas_prices_geocoded.csv

Geocode Manila-only file:

python geocode_stations.py --input manila_gas_prices.csv --output manila_gas_prices_geocoded.csv --fixed-city Manila --city-column ""

Geocode Quezon City-only file:

python geocode_stations.py --input quezon_city_gas_prices.csv --output quezon_city_gas_prices_geocoded.csv --fixed-city "Quezon City" --city-column ""

## Output Files

- manila_gas_prices.csv
- manila_gas_summary.csv
- quezon_city_gas_prices.csv
- quezon_city_gas_summary.csv
- merged_manila_quezon_city_gas_prices.csv
- merged_manila_quezon_city_gas_summary.csv
- merged_manila_quezon_city_gas_prices_geocoded.csv
