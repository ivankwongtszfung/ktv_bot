import logging
from pathlib import Path
from typing import List
from urllib.request import urlretrieve

from ktv_bot.services.ctfile.file import CtFile, CtFileObject
from ktv_bot.services.mvxz.songs import Song, SongService
from tqdm import tqdm

song_service = SongService()
ctfile_service = CtFile()
current_path = Path().resolve()
download_path = current_path / "downloads"


class TqdmUpTo(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)  # also sets self.n = b * bsize


def get_download_filepath(song: Song) -> Path:
    return download_path / f"{song.name}.mkv"


def download_file(song):
    filepath = get_download_filepath(song)
    if filepath.is_file():
        print(f"{song.name} already exists, now skipping...")
        return
    file = ctfile_service.get_file(song.file_id)
    download_url = ctfile_service.get_download_url(file)
    with TqdmUpTo(
        unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=song.name
    ) as t:
        urlretrieve(download_url, filename=filepath, reporthook=t.update_to, data=None)
        t.total = t.n


def download_all_results(keyword, page):
    songs = song_service.get_songs(keyword, page)
    for song in songs:
        try:
            download_file(song)
        except Exception:
            logging.exception(f"Error occurred while downloading {song.name}")
            get_download_filepath(song).unlink(missing_ok=True)
    else:
        if songs:
            download_all_results(keyword, page + 1)


if __name__ == "__main__":
    keyword = "taylor swift"
    download_all_results(keyword, page=1)
