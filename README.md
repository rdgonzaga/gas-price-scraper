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

## Output Files

- manila_gas_prices.csv
- manila_gas_summary.csv
- quezon_city_gas_prices.csv
- quezon_city_gas_summary.csv
- merged_manila_quezon_city_gas_prices.csv
- merged_manila_quezon_city_gas_summary.csv
