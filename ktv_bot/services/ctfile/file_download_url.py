import requests
from decouple import config

from ktv_bot.services.ctfile.value_objects import CtFileObject

FILE_DOWNLOAD_URL = f"{config('CTFILE_URL')}/get_file_url.php"


class CtFileDownloadUrl:
    def __init__(self, **kwargs):
        self.api_url = kwargs.get("api_url") or FILE_DOWNLOAD_URL

    def get_url(self, file_obj: CtFileObject) -> str:
        response = requests.get(self.api_url, params=self._create_payload(file_obj))
        return response.json()["downurl"]

    @staticmethod
    def _create_payload(file_obj: CtFileObject):
        return {
            "uid": file_obj.user_id,
            "fid": file_obj.id,
            "file_chk": file_obj.chunk,
            "mb": 0,
            "app": 0,
            "acheck": 2,
        }
