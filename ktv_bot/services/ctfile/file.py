from urllib.parse import urljoin

import requests
from decouple import config

from ktv_bot.services.ctfile.file_download_url import CtFileDownloadUrl
from ktv_bot.services.ctfile.value_objects.file_object import CtFileObject
from ktv_bot.services.mvxz.songs import Song

FILE_INFO_URL = urljoin(config('CTFILE_URL'), "getfile.php")


class CtFile:
    def __init__(self, **kwargs):
        self.api_url = kwargs.get("api_url") or FILE_INFO_URL

    def get_file(self, song: Song) -> CtFileObject:
        # fid is {user_id}-{file_id}
        response = requests.get(
            self.api_url,
            params={"f": song.file_id, "path": song.url_path},
            headers={"Referer": song.file_url},
        )
        json = response.json()
        if json["code"] == 404:
            raise Exception(json["file"]["message"])
        return CtFileObject.from_json(json["file"])

    def get_download_url(self, ctfile_object: CtFileObject) -> str:
        return CtFileDownloadUrl().get_url(ctfile_object)
