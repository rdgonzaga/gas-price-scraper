from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import re
from pathlib import Path

KNOWN_BRANDS = [
    "Petron",
    "Shell",
    "Caltex",
    "Phoenix",
    "Seaoil",
    "Unioil",
    "Flying V",
    "Cleanfuel",
    "CleanFuel",
    "PTT",
    "Total",
    "TotalEnergies",
    "Jetti",
]

BASE_DIR = Path(__file__).resolve().parent

def clean_price(price_str):
    """Removes the '₱' sign and converts the string to a usable decimal number."""
    try:
        return float(price_str.replace('₱', '').replace(',', '').strip())
    except (AttributeError, ValueError):
        return None


def parse_station_id(onclick_value):
    """Extracts numeric station ID from: openCityReport(33, "Station Name")."""
    if not onclick_value:
        return None

    match = re.search(r"openCityReport\((\d+),", onclick_value)
    return int(match.group(1)) if match else None


def normalize_station_name(name):
    return re.sub(r"\s+", " ", name).strip().lower()


def is_generic_city_station(station_name, city_name):
    normalized = normalize_station_name(station_name)
    city_normalized = city_name.strip().lower()

    for brand in KNOWN_BRANDS:
        brand_city = f"{brand.lower()} {city_normalized}"
        if normalized == brand_city:
            return True

    return False


def filter_and_deduplicate_stations(stations_data, city_name):
    cleaned_rows = []
    seen = set()
    removed_generic = 0
    removed_duplicates = 0

    for row in stations_data:
        station_name = row.get("Station", "")
        if is_generic_city_station(station_name, city_name):
            removed_generic += 1
            continue

        dedupe_key = (
            normalize_station_name(station_name),
            row.get("Price per Liter (PHP)"),
            row.get("Brand Color"),
        )

        if dedupe_key in seen:
            removed_duplicates += 1
            continue

        seen.add(dedupe_key)
        cleaned_rows.append(row)

    return cleaned_rows, removed_generic, removed_duplicates


def expand_station_rows(page, max_clicks=40):
    """Clicks 'Show more' until all station rows are loaded."""
    print("Expanding station list to load all rows...")

    # Some page states initially show only the first 5 rows.
    # Click the action like "Show all 108 stations" when available.
    show_all_candidates = page.locator("button:has-text('Show all')")
    for i in range(show_all_candidates.count()):
        candidate = show_all_candidates.nth(i)
        try:
            text = candidate.inner_text().strip().lower()
        except Exception:
            continue

        if "stations" in text and candidate.is_visible():
            previous_rows = page.locator('#stationTableBody tr').count()
            candidate.click(force=True)

            try:
                page.wait_for_function(
                    "(previous) => document.querySelectorAll('#stationTableBody tr').length > previous",
                    arg=previous_rows,
                    timeout=8000,
                )
            except Exception:
                page.wait_for_timeout(1000)
            break

    for _ in range(max_clicks):
        current_rows = page.locator('#stationTableBody tr').count()
        show_more_btn = page.locator("button:has-text('Show more')")

        if show_more_btn.count() == 0 or not show_more_btn.first.is_visible():
            break

        show_more_btn.first.click()

        try:
            page.wait_for_function(
                "(previous) => document.querySelectorAll('#stationTableBody tr').length > previous",
                arg=current_rows,
                timeout=5000,
            )
        except Exception:
            # If rows don't increase immediately, allow a short delay before re-checking.
            page.wait_for_timeout(700)

    total_rows = page.locator('#stationTableBody tr').count()
    print(f"Loaded {total_rows} station rows.")

def scrape_gaswatch():
    url = "https://gaswatchph.com/quezon-city"
    
    print("Launching headless browser to fetch data...")
    
    # --- 1. GET FULLY RENDERED HTML USING PLAYWRIGHT ---
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Go to the page and wait for the specific table ID to appear
        page.goto(url, wait_until="domcontentloaded")
        print("Waiting for the data to load on the page...")
        
        try:
            # Wait for at least one rendered row to avoid parsing an empty table body.
            page.wait_for_selector('#stationTableBody tr', timeout=20000)
        except Exception as e:
            print("Timed out waiting for the table. The site might be blocking us.")
            browser.close()
            return

        expand_station_rows(page)

        html = page.content()
        browser.close()

    # --- 2. PARSE WITH BEAUTIFULSOUP ---
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract Summary Cards
    print("\n--- Top Fuel Prices Summary ---")
    summary_data = []
    cards = soup.find_all('div', class_='summary-card')
    
    for card in cards:
        label_el = card.find('div', class_='summary-card-label')
        price_el = card.find('div', class_='summary-card-price')
        brand_el = card.find('div', class_='summary-card-brand')

        label = label_el.get_text(strip=True).replace('Viewing', '').strip() if label_el else None
        raw_price = price_el.get_text(strip=True) if price_el else None
        clean_val = clean_price(raw_price)
        brand = brand_el.get_text(strip=True) if brand_el else None
        
        summary_data.append({
            "Fuel Type": label,
            "Price (PHP)": clean_val,
            "Brand": brand
        })

    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
        summary_df.to_csv(BASE_DIR / 'quezon_city_gas_summary.csv', index=False, encoding='utf-8')
    else:
        print("No summary cards found on the page.")

    # Extract Full Station List
    print("\n--- Extracting Full Station List ---")
    stations_data = []
    table_body = soup.find('tbody', id='stationTableBody') 
    
    if table_body:
        rows = table_body.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3: 
                rank_badge = cols[0].find('span', class_='rank-badge')
                rank_text = rank_badge.get_text(strip=True) if rank_badge else cols[0].get_text(strip=True)

                station_info = cols[1].find('div', class_='station-info')
                station_name = station_info.get_text(" ", strip=True) if station_info else cols[1].get_text(" ", strip=True)

                brand_dot = cols[1].find('span', class_='brand-dot')
                brand_color = None
                if brand_dot:
                    style = brand_dot.get('style', '')
                    color_match = re.search(r"background\s*:\s*([^;]+)", style)
                    brand_color = color_match.group(1).strip() if color_match else None
                
                price_cell = cols[2]
                raw_price = price_cell.get_text(strip=True)
                clean_val = clean_price(raw_price)

                report_button = cols[3].find('button', class_='city-report-btn') if len(cols) > 3 else None
                station_id = parse_station_id(report_button.get('onclick', '')) if report_button else None
                
                stations_data.append({
                    "Rank": int(rank_text) if rank_text.isdigit() else rank_text,
                    "Station ID": station_id,
                    "Station": station_name,
                    "Price per Liter (PHP)": clean_val,
                    "Brand Color": brand_color
                })

    if stations_data:
        stations_data, removed_generic, removed_duplicates = filter_and_deduplicate_stations(
            stations_data,
            city_name="Quezon City",
        )

        df = pd.DataFrame(stations_data)
        print("\nScraping Successful! Here is a preview of the main table:")
        print(df.head())

        print(
            f"Removed {removed_generic} city-only generic stations and {removed_duplicates} duplicate rows."
        )
        print(f"Final station count: {len(df)}")
        
        df.to_csv(BASE_DIR / 'quezon_city_gas_prices.csv', index=False, encoding='utf-8')
        print("\n✅ Main data saved to 'quezon_city_gas_prices.csv'!")
    else:
        print("Failed to parse the table rows.")

if __name__ == "__main__":
    scrape_gaswatch()