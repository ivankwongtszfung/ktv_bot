import requests
from bs4 import BeautifulSoup, ResultSet
from decouple import config

from ktv_bot.services.mvxz.http_request import MvxzRequestor

MVXZ_URL = config("MVXZ_URL")
MVXZ_MV_URL = f"{MVXZ_URL}/imv.asp"


class MvUrlService(MvxzRequestor):
    def __init__(self):
        self.url = MVXZ_MV_URL

    def get_mv_url(self, id: int):
        html_content = self._fetch(id)
        return self._parse(html_content)

    def _fetch(self, id: int) -> str:
        response = requests.get(self.url, headers=self._header(), params={"id": id})
        return response.text.encode("latin1")

    def _parse(self, html_response: str) -> ResultSet:
        soup = BeautifulSoup(html_response, "html.parser")
        video_div = soup.find("div", class_="video")
        anchor = video_div.select("a")
        return anchor[0]["href"]
