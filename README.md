# Gas Price Scraper

Simple Python scrapers for GasWatchPH city pages, plus a merge script.

## Files

- manila/manila-gas-scraper.py: Scrapes Manila station prices and summary
- quezon_city/quezon-city-gas-scraper.py: Scrapes Quezon City station prices and summary
- merged/merge_city_data.py: Merges Manila and Quezon City CSV outputs
- merged/geocode_stations.py: Geocodes station rows into latitude/longitude

## Install

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

python -m pip install -r requirements.txt

3. Install Playwright browser:

python -m playwright install chromium

## Run

Scrape Manila:

python manila/manila-gas-scraper.py

Scrape Quezon City:

python quezon_city/quezon-city-gas-scraper.py

Merge both city outputs:

python merged/merge_city_data.py

## Get Coordinates (Latitude/Longitude)

Leaflet is a map library and needs coordinates. Use geocode_stations.py to convert station names into coordinates using OpenStreetMap Nominatim.

Geocode merged file (recommended):

python merged/geocode_stations.py

Geocode Manila-only file:

python merged/geocode_stations.py --input manila/manila_gas_prices.csv --output manila/manila_gas_prices_geocoded.csv --fixed-city Manila --city-column ""

Geocode Quezon City-only file:

python merged/geocode_stations.py --input quezon_city/quezon_city_gas_prices.csv --output quezon_city/quezon_city_gas_prices_geocoded.csv --fixed-city "Quezon City" --city-column ""

## Output Files

- manila/manila_gas_prices.csv
- manila/manila_gas_summary.csv
- manila/manila_gas_prices_geocoded.csv
- quezon_city/quezon_city_gas_prices.csv
- quezon_city/quezon_city_gas_summary.csv
- merged/merged_manila_quezon_city_gas_prices.csv
- merged/merged_manila_quezon_city_gas_summary.csv
- merged/merged_manila_quezon_city_gas_prices_geocoded.csv
