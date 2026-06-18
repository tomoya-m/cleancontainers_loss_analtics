import datetime
import io
import logging

from azure.storage.blob import ContainerClient
import pandas

from azure_credential import get_credential


class AdpDataLake:
    def __init__(
        self,
        storage_account_name: str = "dlsaicellodatalake001",
        container_name: str = "scada-archive"
    ):
        """
        Parameters
        ----------
        - storage_account_name: str
            - ストレージアカウントの名前
            - デフォルト値は`dlsaicellodatalake001`
        - container_name: str
            - コンテナの名前
            - デフォルト値は`scada-archive`
        """
        self.logger = logging.getLogger(__name__)

        # Azureの認証情報を取得する。
        self.credential = get_credential()

        # ContainerClientを取得する。
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        self.container_client = self._get_container_client(
            account_url=account_url,
            container_name=container_name,
        )


    def _get_container_client(
        self,
        account_url: str,
        container_name: str,
    ) -> ContainerClient:
        """
        ContainerClientを取得する。

        Parameters
        ----------
        - account_url: str
            - ストレージアカウントのURL
        - container_name: str
            - コンテナーの名前

        Returns
        -------
        - ContainerClient
            - コンテナークライアント
        """
        return ContainerClient(
            account_url=account_url,
            container_name=container_name,
            credential=self.credential
        )


    def download_csv_blob(
        self,
        device_id: str,
        target_date: datetime.date
    ) -> pandas.DataFrame:
        """
        CSVファイルをBlobストレージからダウンロードし、DataFrameとして返す。

        Parameters
        ----------
        - device_id: str
            - デバイスID
        - target_date: datetime.date
            - 対象の日付

        Returns
        -------
        - pandas.DataFrame
            - ダウンロードしたCSVファイルの内容を格納したDataFrame
        """
        # Blob名を生成する。
        target_year_str = target_date.strftime("%Y")
        target_month_str = target_date.strftime("%m")
        target_date_str = target_date.strftime("%Y%m%d")

        blob_name = f"device_id={device_id}/year={target_year_str}/month={target_month_str}/{target_date_str}.csv"
        self.logger.info(f"Downloading blob: {blob_name}")

        # BlobClientを取得する。
        blob_client = self.container_client.get_blob_client(blob_name)

        # BlobをダウンロードしてDataFrameに変換する。
        blob_data = blob_client.download_blob().readall()
        df = pandas.read_csv(io.BytesIO(blob_data))

        return df


if __name__ == "__main__":
    device_id = input("デバイスIDを入力してください: ")
    target_date_str = input("対象日付を入力してください (YYYY-MM-DD): ")
    target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()

    adp_datalake = AdpDataLake()
    df = adp_datalake.download_csv_blob(device_id=device_id, target_date=target_date)

    print(df.head())
