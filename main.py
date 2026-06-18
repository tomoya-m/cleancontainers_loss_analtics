from __future__ import annotations
from pathlib import Path

import pandas

from services.cleancontainers_db import CleanContainersDb


OUTPUT_DIR = "outputs"


def main() -> None:
    # 各種パスを設定する。
    sql_file_path = Path(__file__).resolve().parent / "select.sql"
    products_json_path = Path(__file__).resolve().parent / "products.json"
    output_csv_path = Path(__file__).resolve().parent / OUTPUT_DIR

    # 製造データを取得する。
    db = CleanContainersDb()
    manufacturing_df = db.execute_sql_file(sql_file_path=sql_file_path)

    # 製品データを取得する。
    product_df = pandas.read_json(products_json_path, orient="index").reset_index(names="製品名")
    # 列の順番を、製品ID、製品名、容量、重量、本体カラーの順に並び替える。
    product_df = product_df[["製品ID", "製品名", "容量", "重量", "本体カラー"]]

    # CSVファイルとして出力する。
    manufacturing_df.to_csv(output_csv_path / "製造データ.csv", index=False, encoding="utf-8-sig")
    product_df.to_csv(output_csv_path / "製品データ.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
