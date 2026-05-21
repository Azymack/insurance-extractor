import json
import pandas as pd

from bs4 import BeautifulSoup


INPUT_JSON = "output/ocr_result.json"


def expand_table(html):

    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table")

    if table is None:
        return []

    rows = table.find_all("tr")

    grid = []

    rowspan_map = {}

    for row_idx, row in enumerate(rows):

        cells = row.find_all(["td", "th"])

        grid_row = []

        col_idx = 0

        while (row_idx, col_idx) in rowspan_map:
            grid_row.append(rowspan_map[(row_idx, col_idx)])
            col_idx += 1

        for cell in cells:

            text = cell.get_text(" ", strip=True)

            rowspan = int(cell.get("rowspan", 1))
            colspan = int(cell.get("colspan", 1))

            while (row_idx, col_idx) in rowspan_map:
                grid_row.append(rowspan_map[(row_idx, col_idx)])
                col_idx += 1

            for _ in range(colspan):
                grid_row.append(text)

                if rowspan > 1:
                    for r in range(1, rowspan):
                        rowspan_map[(row_idx + r, col_idx)] = text

                col_idx += 1

        grid.append(grid_row)

    return grid


def normalize_grid(grid):

    max_cols = max(len(r) for r in grid)

    normalized = []

    for row in grid:

        padded = row + [""] * (max_cols - len(row))

        normalized.append(padded)

    return normalized


def process_tables(data):

    extracted_tables = []

    for page in data:

        page_num = page["page"]

        for item in page["ocr_result"]:

            if item["type"] != "table":
                continue

            html = item["res"]["html"]

            grid = expand_table(html)

            if not grid:
                continue

            normalized = normalize_grid(grid)

            df = pd.DataFrame(normalized)

            extracted_tables.append({
                "page": page_num,
                "dataframe": df
            })

    return extracted_tables


def main():

    with open(INPUT_JSON, "r") as f:
        data = json.load(f)

    tables = process_tables(data)

    print(f"\nFound {len(tables)} tables\n")

    for idx, table_data in enumerate(tables):

        print("=" * 80)
        print(f"TABLE {idx + 1}")
        print("=" * 80)

        print(table_data["dataframe"])

        print("\n")


if __name__ == "__main__":
    main()