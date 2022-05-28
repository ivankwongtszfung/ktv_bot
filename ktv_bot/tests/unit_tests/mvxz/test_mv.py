from urllib.parse import urlparse

from pytest import fixture

from ktv_bot.services.mvxz import MvUrlService


def is_absolute(url):
    return bool(urlparse(url).netloc)


def read_html(folder):
    with open(folder, encoding="utf-8") as html_data:
        return html_data.read()


@fixture
def mv_record_html(html_dir):
    return read_html(html_dir / "mvxz_mv_record.html")


class FakeMvService(MvUrlService):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def _fetch(self, _: str) -> str:
        return self.data


def test_get_mv_download_url(faker, mv_record_html):
    fake_song_service = FakeMvService(data=mv_record_html)
    mv = fake_song_service.get_mv_url(id=faker.pyint())
    assert is_absolute(mv)
