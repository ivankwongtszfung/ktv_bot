from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, ResultSet
from decouple import config
from methodtools import lru_cache

from ktv_bot.services.mvxz.http_request import MvxzRequestor

MVXZ_MV_URL = urljoin(config("MVXZ_URL"), "imv.asp")


@dataclass
class MvPath:
    url: str
    file_id: str
    user_id: str


class MvUrlService(MvxzRequestor):
    def __init__(self):
        self.url = MVXZ_MV_URL

    @lru_cache(maxsize=None)
    def get_mv_url(self, id: int):
        html_content = self._fetch(id)
        return self._parse(html_content)

    def get_file_id(self, id: int):
        # /{source}/{user_id}-{file_id}
        path = self._get_stripped_mv_path(id)
        return path.rsplit("/", 1)[-1]

    def get_path(self, id: int):
        path = self._get_stripped_mv_path(id)
        return path.rsplit("/", 2)[-2]

    def _get_stripped_mv_path(self, id: int):
        mv_url = self.get_mv_url(id)
        parsed_url = urlparse(mv_url)
        return parsed_url.path.strip("/")  # path: /some/where.html

    def _fetch(self, id: int) -> str:
        response = requests.get(self.url, headers=self._header(), params={"id": id})
        return response.text.encode("latin1")

    def _parse(self, html_response: str) -> ResultSet:
        soup = BeautifulSoup(html_response, "html.parser")
        video_div = soup.find("div", class_="video")
        anchor = video_div.select("a")
        return anchor[0]["href"]
