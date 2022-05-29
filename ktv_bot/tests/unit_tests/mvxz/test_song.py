from pytest import fixture

from ktv_bot.services.mvxz import SongService


def read_html(folder):
    with open(folder, encoding="utf-8") as html_data:
        return html_data.read()


@fixture
def one_record_html(html_dir):
    return read_html(html_dir / "mvxz_one_record.html")


@fixture
def multi_record_html(html_dir):
    return read_html(html_dir / "mvxz_multi_records.html")


@fixture
def multi_no_record_html(html_dir):
    return read_html(html_dir / "mvxz_no_record.html")


@fixture
def multi_last_plus_one_html(html_dir):
    return read_html(html_dir / "mvxz_last_plus_one_page.html")


class FakeSongService(SongService):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def _fetch(self, _: str, __: int) -> str:
        return self.data


def test_parse_html_content(faker, one_record_html):
    fake_song_service = FakeSongService(data=one_record_html)
    songs = fake_song_service.get_songs(name=faker.pystr(), page=1)
    assert len(songs) == 1


def test_parse_html_content_multiple_records(faker, multi_record_html):
    fake_song_service = FakeSongService(data=multi_record_html)
    songs = fake_song_service.get_songs(name=faker.pystr(), page=1)
    assert len(songs) == 2


def test_parse_html_content_no_records(faker, multi_no_record_html):
    fake_song_service = FakeSongService(data=multi_no_record_html)
    songs = fake_song_service.get_songs(name=faker.pystr(), page=1)
    assert len(songs) == 0


def test_parse_html_content_last_plus_one_page(faker, multi_last_plus_one_html):
    fake_song_service = FakeSongService(data=multi_last_plus_one_html)
    songs = fake_song_service.get_songs(name=faker.pystr(), page=1)
    assert len(songs) == 0
