from __future__ import annotations

import logging
import shutil
from collections import deque
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import List, Union
from urllib.request import urlretrieve

import typer
import socket
from tqdm import tqdm

from ktv_bot.services.ctfile.file import CtFile
from ktv_bot.services.mvxz.songs import Song, SongService

logging.basicConfig(filename="songs.log", level=logging.INFO)

song_service = SongService()
ctfile_service = CtFile()
download_path = Path("/mnt/c/Users/invok/Desktop/KTV/").resolve()
loaded_paths = [download_path, download_path / "Loaded", download_path / "Loaded 2"]
temp_path = Path().resolve() / "temp"
DOWNLOAD_BATCH_SIZE = 5
socket.setdefaulttimeout(60 * 5)


class TqdmUpTo(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)  # also sets self.n = b * bsize


def get_download_filepath(path: Path, song: Union[Song, CtFile]) -> Path:
    if song.name.endswith(".mkv"):
        return path / song.name
    return path / f"{song.name}.mkv"


def get_tmp_download_filepath(song: Union[Song, CtFile]) -> Path:
    return get_download_filepath(temp_path, song)


def is_downloaded(song: Union[Song, CtFile]):
    return any(get_download_filepath(path, song).is_file() for path in loaded_paths)


def download_file(song):
    if is_downloaded(song):
        print(f"{song.name} already exists, now skipping...")
        return
    file = ctfile_service.get_file(song)
    if is_downloaded(file):
        print(f"{file.name} already exists, now skipping...")
        return
    download_url = ctfile_service.get_download_url(file)
    with TqdmUpTo(
        unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=song.name
    ) as t:
        tmp_filepath = get_tmp_download_filepath(song)
        urlretrieve(
            download_url, filename=tmp_filepath, reporthook=t.update_to, data=None
        )
        t.total = t.n
    move_file_to_download_folder(tmp_filepath)


def move_file_to_download_folder(tmp_path: Path):
    shutil.move(str(tmp_path), str(download_path))


def download_all_results(keyword: str, page: int, dfs: bool = True) -> int:
    """download all songs result for a page

    Args:
        keyword (str): search songs with this keyword, must be in simplified chiense
        page (int): page of the search results
        dfs (bool, optional): whether to download all songs for keyword in one call. Defaults to True.

    Returns:
        int: return number of song downloaded
    """
    no_of_songs = 0
    songs = song_service.get_songs(keyword, page)
    for song in songs:
        try:
            logging.info(song)
            download_file(song)
            no_of_songs += 1
        except socket.timeout as se:
            logging.exception(f"Socket timeout")
            get_tmp_download_filepath(song).unlink(missing_ok=True)
        except Exception:
            logging.exception(f"Error occurred while downloading {song.name}")
            get_tmp_download_filepath(song).unlink(missing_ok=True)
    if dfs and songs:
        download_all_results(keyword, page + 1)
    return no_of_songs


def download_all_songs(songs: List[Song]) -> int:
    """download all the songs provided

    Args:
        songs (List[Song]): songs from mvxz

    Returns:
        int: number of songs download
    """
    no_of_songs = 0
    for song in songs:
        try:
            logging.info(song)
            download_file(song)
            no_of_songs += 1
        except Exception:
            logging.exception(f"Error occurred while downloading {song.name}")
            get_tmp_download_filepath(song).unlink(missing_ok=True)
    return no_of_songs


def setup_folder():
    shutil.rmtree(str(temp_path), ignore_errors=True)
    temp_path.mkdir(exist_ok=True)
    download_path.mkdir(exist_ok=True)


@dataclass
class SongResult:
    keyword: str
    page: int = 1
    current: int = 0

    def get_songs(self, number_of_songs: int):
        return self.songs[self.current : self.current + number_of_songs]

    @classmethod
    def from_prev_result(cls, other: SongResult):
        return cls(other.keyword, other.page + 1)

    @cached_property
    def songs(self):
        return song_service.get_songs(self.keyword, self.page)

    @cached_property
    def length(self):
        return len(self.songs)

    @property
    def all_downloaded(self):
        return self.current == self.length


def main(keywords: List[str]):  # , dfs: bool = typer.Option(True, "--dfs/--bfs")):
    setup_folder()
    keyword_queue = deque(SongResult(keyword) for keyword in keywords)
    while keyword_queue:
        song_result = keyword_queue.popleft()
        songs = song_result.get_songs(DOWNLOAD_BATCH_SIZE)
        length = download_all_songs(songs)
        if length == len(songs):
            song_result.current += DOWNLOAD_BATCH_SIZE
        keyword_queue.append(
            SongResult.from_prev_result(song_result)
            if song_result.all_downloaded
            else song_result
        )


if __name__ == "__main__":
    typer.run(main)
