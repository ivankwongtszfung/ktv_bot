from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup, ResultSet
from decouple import config

from ktv_bot.services.mvxz.http_request import MvxzRequestor
from ktv_bot.services.mvxz.mv_url import MvUrlService

MVXZ_URL = config("MVXZ_URL")
MVXZ_SEARCH_URL = f"{MVXZ_URL}/isearch.asp"
MVXZ_MV_URL = f"{MVXZ_URL}/imv.asp"


def is_absolute(url):
    return bool(urlparse(url).netloc)


@dataclass
class Song:
    name: str
    link: str
    size: float
    id: int = field(init=False)
    is_downloaded: bool = False
    _mv_url_service: Optional[MvUrlService] = None

    def __post_init__(self):
        self.link = (
            urljoin(MVXZ_URL, self.link) if not is_absolute(self.link) else self.link
        )
        url = urlparse(self.link)
        self.id = parse_qs(url.query)["id"][0]
        self._mv_url_service = self._mv_url_service or MvUrlService()

    def mark_downloaded(self):
        self.is_downloaded = True

    @classmethod
    def from_bs(cls, row: ResultSet):
        _, name_tr, size_tr, *_ = [data for data in row if data.text.strip()]
        anchor = name_tr.find("a")
        return cls(name=name_tr.text, link=anchor["href"], size=int(size_tr.text))

    @cached_property
    def file_id(self) -> str:
        return self._mv_url_service.get_file_id(self.id)

    @cached_property
    def file_url(self) -> str:
        return self._mv_url_service.get_mv_url(self.id)

    @cached_property
    def url_path(self) -> str:
        return self._mv_url_service.get_path(self.id)

    def __str__(self):
        return f"{self.name} {self.file_url} {self.url_path}"


class SongService(MvxzRequestor):
    def __init__(self):
        self.url = MVXZ_SEARCH_URL

    def get_songs(self, name: str, page: int):
        html_content = self._fetch(name, page)
        rows = self._parse(html_content)
        return [Song.from_bs(row) for row in rows]

    def _fetch(self, name: str, page: int) -> str:
        response = requests.post(
            self.url,
            headers=self._header(),
            data={"ktv": name, "page": page, "type": 3},
        )
        return response.text.encode("latin1")

    def _parse(self, html_response: str) -> ResultSet:
        soup = BeautifulSoup(html_response, "html.parser")
        tbody = soup.find("tbody")
        rows = tbody.findChildren("tr", recursive=False)
        return rows
