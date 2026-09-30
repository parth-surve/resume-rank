"""
slice_excel.py — Create a smaller test subset from your screening Excel.

Usage:
    python scripts/slice_excel.py --input Original.xlsx --rows 10
    python scripts/slice_excel.py --input Original.xlsx --rows 5 --output small_test.xlsx
    python scripts/slice_excel.py --input Original.xlsx --rows 10 --sheet "Software Engg"

Options:
    --input   Path to your full Excel file (required)
    --rows    Number of rows to keep per sheet (default: 10)
    --output  Output filename (default: <input>_slice_<N>.xlsx)
    --sheet   Only slice a specific sheet (default: all sheets)
    --random  Randomly sample rows instead of taking first N
"""

import argparse
import os
import random

import pandas as pd


def slice_excel(
    input_path: str,
    n_rows: int = 10,
    output_path: str | None = None,
    sheet_filter: str | None = None,
    randomize: bool = False,
) -> str:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    xl = pd.ExcelFile(input_path)
    sheets_to_process = (
        [s for s in xl.sheet_names if s == sheet_filter]
        if sheet_filter
        else xl.sheet_names
    )

    if not sheets_to_process:
        raise ValueError(
            f"Sheet '{sheet_filter}' not found. "
            f"Available: {xl.sheet_names}"
        )

    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = f"{base}_slice_{n_rows}.xlsx"

    print(f"\n📂 Input  : {input_path}")
    print(f"📄 Output : {output_path}")
    print(f"📊 Rows   : {n_rows} per sheet {'(random)' if randomize else '(first N)'}")
    print()

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name in sheets_to_process:
            df = xl.parse(sheet_name)
            total = len(df)

            if randomize and n_rows < total:
                sliced = df.sample(n=n_rows, random_state=42).reset_index(drop=True)
            else:
                sliced = df.head(n_rows)

            sliced.to_excel(writer, sheet_name=sheet_name, index=False)

            print(
                f"  ✅  Sheet '{sheet_name}': "
                f"{total} → {len(sliced)} rows"
            )

    print(f"\n🎉 Saved to: {os.path.abspath(output_path)}\n")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Slice a screening Excel file to N rows per sheet."
    )
    parser.add_argument("--input", required=True, help="Path to source Excel file")
    parser.add_argument("--rows", type=int, default=10, help="Rows per sheet (default: 10)")
    parser.add_argument("--output", default=None, help="Output file path (optional)")
    parser.add_argument("--sheet", default=None, help="Only process this sheet name")
    parser.add_argument(
        "--random",
        action="store_true",
        help="Randomly sample rows instead of taking first N",
    )

    args = parser.parse_args()
    slice_excel(
        input_path=args.input,
        n_rows=args.rows,
        output_path=args.output,
        sheet_filter=args.sheet,
        randomize=args.random,
    )
