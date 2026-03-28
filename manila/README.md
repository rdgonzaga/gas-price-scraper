# Manila Gas Scraper

This folder contains the Manila scraping and geocoding workflow.

## Files

- manila-gas-scraper.py: Scrapes latest Manila gas station prices and summary
- manila_geocode_stations.py: Geocodes Manila station names to latitude/longitude
- manila_gas_prices.csv: Scraped station prices output
- manila_gas_summary.csv: Scraped summary output
- manila_gas_prices_geocoded.csv: Geocoded output

## Requirements / Installation

Run these from the project root (`gas-price-scraper`):

1. Install Python dependencies from `requirements.txt`:

python -m pip install -r requirements.txt

2. Install Playwright browser (required for scraping):

python -m playwright install chromium

## Run Manila Scraper

From project root:

python manila/manila-gas-scraper.py

This generates:

- manila/manila_gas_prices.csv
- manila/manila_gas_summary.csv

## Run Manila Geocoder

From project root:

python manila/manila_geocode_stations.py

This generates:

- manila/manila_gas_prices_geocoded.csv

## Optional: Run from inside Manila folder

If your terminal is already in `manila/`:

python manila-gas-scraper.py
python manila_geocode_stations.py
