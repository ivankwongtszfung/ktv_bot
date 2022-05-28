import requests
from decouple import config

from ktv_bot.services.ctfile.file_download_url import CtFileDownloadUrl
from ktv_bot.services.ctfile.value_objects.file_object import CtFileObject

FILE_INFO_URL = f"{config('CTFILE_URL')}/getfile.php"


class CtFile:
    def __init__(self, **kwargs):
        self.api_url = kwargs.get("api_url") or FILE_INFO_URL

    def get_file(self, fid: str) -> CtFileObject:
        # fid is {user_id}-{file_id}
        response = requests.get(self.api_url, params={"f": fid})
        return CtFileObject.from_json(response.json())

    def get_download_url(self, ctfile_object: CtFileObject) -> str:
        return CtFileDownloadUrl().get_url(ctfile_object)
