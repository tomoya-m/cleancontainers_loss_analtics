import logging
from pathlib import Path
import struct
from typing import Sequence

import pandas
import pyodbc

try:
    from .azure_credential import get_credential
except ImportError:
    from azure_credential import get_credential


class CleanContainersDb:
    host = "sql-dwhserver-prod-001.database.windows.net"
    database_name = "sqldb-CleanContainersDb-prod-001"


    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.credential = get_credential()


    def _build_connection_string(self) -> str:
        return (
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server=tcp:{self.host},1433;"
            f"Database={self.database_name};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )


    def _build_access_token_attrs(self) -> dict[int, int | bytes | bytearray | str | Sequence[str]]:
        token = self.credential.get_token("https://database.windows.net/.default").token
        token_bytes = token.encode("utf-16-le")
        token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)

        # 1256 is SQL_COPT_SS_ACCESS_TOKEN in msodbcsql.h.
        return {1256: token_struct}


    def execute_sql_file(self, sql_file_path: str | Path) -> pandas.DataFrame:
        sql_file_path = Path(sql_file_path)
        query = sql_file_path.read_text(encoding="utf-8")

        conn_str = self._build_connection_string()
        attrs_before = self._build_access_token_attrs()

        with pyodbc.connect(conn_str, attrs_before=attrs_before) as connection:
            return pandas.read_sql_query(query, connection)


if __name__ == "__main__":
    sql_file_path = Path(__file__).resolve().parent.parent / "select.sql"

    db = CleanContainersDb()
    df = db.execute_sql_file(sql_file_path=sql_file_path)

    print(df.head())
