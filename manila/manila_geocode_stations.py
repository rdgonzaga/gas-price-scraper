import argparse
import time
from pathlib import Path

import pandas as pd
import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
DEFAULT_REGION_HINT = "Metro Manila, Philippines"
BASE_DIR = Path(__file__).resolve().parent


def build_query(station_name: str, city: str | None) -> str:
    parts = [station_name.strip()]
    if city:
        parts.append(city.strip())
    parts.append(DEFAULT_REGION_HINT)
    return ", ".join([part for part in parts if part])


def geocode(query: str, user_agent: str, timeout: int = 20) -> tuple[float | None, float | None, str | None]:
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
        "countrycodes": "ph",
    }
    headers = {"User-Agent": user_agent}

    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return None, None, f"request_error: {exc}"

    if not data:
        return None, None, "no_match"

    top = data[0]
    lat = float(top["lat"])
    lon = float(top["lon"])
    return lat, lon, None


def geocode_file(
    input_csv: Path,
    output_csv: Path,
    station_column: str,
    city_column: str | None,
    fixed_city: str | None,
    user_agent: str,
    delay_seconds: float,
) -> None:
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    df = pd.read_csv(input_csv)
    if station_column not in df.columns:
        raise ValueError(f"Missing station column '{station_column}' in {input_csv}")

    latitudes: list[float | None] = []
    longitudes: list[float | None] = []
    geocode_queries: list[str] = []
    geocode_errors: list[str | None] = []

    total = len(df)
    print(f"Geocoding {total} station rows...")

    for idx, row in df.iterrows():
        station_name = str(row.get(station_column, "")).strip()
        city_name = None

        if city_column and city_column in df.columns:
            city_name = str(row.get(city_column, "")).strip() or None

        if fixed_city:
            city_name = fixed_city

        query = build_query(station_name, city_name)
        print(f"[{idx + 1}/{total}] Query: {query}")

        lat, lon, err = geocode(query, user_agent=user_agent)

        if err:
            print(f"[{idx + 1}/{total}] Result: error={err}")
        else:
            print(f"[{idx + 1}/{total}] Result: lat={lat}, lon={lon}")

        latitudes.append(lat)
        longitudes.append(lon)
        geocode_queries.append(query)
        geocode_errors.append(err)

        if (idx + 1) % 25 == 0 or (idx + 1) == total:
            print(f"Processed {idx + 1}/{total}")

        time.sleep(delay_seconds)

    df["Geocode Query"] = geocode_queries
    df["Latitude"] = latitudes
    df["Longitude"] = longitudes
    df["Geocode Error"] = geocode_errors

    original_total = len(df)
    df = df[df["Geocode Error"].fillna("").str.lower() != "no_match"].copy()
    removed_no_match = original_total - len(df)

    df.to_csv(output_csv, index=False, encoding="utf-8")

    success_count = int(df["Latitude"].notna().sum())
    print(f"Removed no_match rows: {removed_no_match}")
    print(f"Geocoded successfully: {success_count}/{len(df)}")
    print(f"Saved output to: {output_csv}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Geocode gas station names from CSV and append latitude/longitude."
    )
    parser.add_argument(
        "--input",
        default=str(BASE_DIR / "manila_gas_prices.csv"),
        help="Input CSV path",
    )
    parser.add_argument(
        "--output",
        default=str(BASE_DIR / "manila_gas_prices_geocoded.csv"),
        help="Output CSV path",
    )
    parser.add_argument(
        "--station-column",
        default="Station",
        help="Station name column in CSV",
    )
    parser.add_argument(
        "--city-column",
        default="",
        help="City column in CSV (set empty string to disable)",
    )
    parser.add_argument(
        "--fixed-city",
        default="Manila",
        help="Force a single city for all rows (e.g., Manila)",
    )
    parser.add_argument(
        "--user-agent",
        default="gas-price-scraper/1.0 (contact: local-script)",
        help="User-Agent header required by Nominatim policy",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API calls in seconds",
    )
    args = parser.parse_args()

    geocode_file(
        input_csv=Path(args.input),
        output_csv=Path(args.output),
        station_column=args.station_column,
        city_column=args.city_column if args.city_column else None,
        fixed_city=args.fixed_city if args.fixed_city else None,
        user_agent=args.user_agent,
        delay_seconds=max(args.delay, 0.0),
    )


if __name__ == "__main__":
    main()
