import argparse
from pathlib import Path

import pandas as pd


def load_city_csv(file_path: Path, city_name: str) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    df = pd.read_csv(file_path)
    df.insert(0, "City", city_name)
    return df


def merge_price_data(manila_path: Path, qc_path: Path, output_path: Path) -> None:
    manila_df = load_city_csv(manila_path, "Manila")
    qc_df = load_city_csv(qc_path, "Quezon City")

    merged_df = pd.concat([manila_df, qc_df], ignore_index=True)

    # Keep prices clean and consistently sorted for easier analysis.
    if "Price per Liter (PHP)" in merged_df.columns:
        merged_df["Price per Liter (PHP)"] = pd.to_numeric(
            merged_df["Price per Liter (PHP)"], errors="coerce"
        )
        merged_df = merged_df.sort_values(
            by=["Price per Liter (PHP)", "City", "Rank"],
            ascending=[True, True, True],
            na_position="last",
        )

    merged_df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Merged station rows: {len(merged_df)}")
    print(f"Saved merged prices to: {output_path}")


def merge_summary_data(manila_path: Path, qc_path: Path, output_path: Path) -> None:
    manila_df = load_city_csv(manila_path, "Manila")
    qc_df = load_city_csv(qc_path, "Quezon City")

    merged_df = pd.concat([manila_df, qc_df], ignore_index=True)

    if "Price (PHP)" in merged_df.columns:
        merged_df["Price (PHP)"] = pd.to_numeric(merged_df["Price (PHP)"], errors="coerce")
        merged_df = merged_df.sort_values(by=["Fuel Type", "City"])

    merged_df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Merged summary rows: {len(merged_df)}")
    print(f"Saved merged summary to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge gas price CSV data for Manila and Quezon City."
    )
    parser.add_argument(
        "--manila-prices",
        default="manila_gas_prices.csv",
        help="Path to Manila station prices CSV",
    )
    parser.add_argument(
        "--qc-prices",
        default="quezon_city_gas_prices.csv",
        help="Path to Quezon City station prices CSV",
    )
    parser.add_argument(
        "--manila-summary",
        default="manila_gas_summary.csv",
        help="Path to Manila summary CSV",
    )
    parser.add_argument(
        "--qc-summary",
        default="quezon_city_gas_summary.csv",
        help="Path to Quezon City summary CSV",
    )
    parser.add_argument(
        "--out-prices",
        default="merged_manila_quezon_city_gas_prices.csv",
        help="Output path for merged station prices CSV",
    )
    parser.add_argument(
        "--out-summary",
        default="merged_manila_quezon_city_gas_summary.csv",
        help="Output path for merged summary CSV",
    )

    args = parser.parse_args()

    merge_price_data(
        Path(args.manila_prices),
        Path(args.qc_prices),
        Path(args.out_prices),
    )
    merge_summary_data(
        Path(args.manila_summary),
        Path(args.qc_summary),
        Path(args.out_summary),
    )


if __name__ == "__main__":
    main()
