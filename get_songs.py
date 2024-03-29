from __future__ import annotations

import logging
import shutil
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union
from urllib.request import urlretrieve

import typer
import socket
from decouple import config
from tqdm import tqdm

from ktv_bot.services.ctfile.file import CtFile
from ktv_bot.services.mvxz.songs import Song, SongService

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # or whatever
handler = logging.FileHandler("test.log", "w", "utf-8")  # or whatever
handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(message)s"))  # or whatever
logger.addHandler(handler)

song_service = SongService()
ctfile_service = CtFile()
LOCAL_FOLDER = config("SONG_LOCAL_PATH")

download_path = Path(LOCAL_FOLDER).resolve()
loaded_paths = [download_path, download_path / "Loaded", download_path / "Loaded 2"]
temp_path = Path().resolve() / "temp"
DOWNLOAD_BATCH_SIZE = 5
socket.setdefaulttimeout(60 * 5)


def my_hook(t):
    last_b = [0]

    def update_to(b=1, bsize=1, tsize=None):
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return update_to


def get_download_filepath(path: Path, song: Union[Song, CtFile]) -> Path:
    if song.name.endswith(".mkv"):
        return path / song.name
    return path / f"{song.name}.mkv"


def get_tmp_download_filepath(song: Union[Song, CtFile]) -> Path:
    return get_download_filepath(temp_path, song)


def is_downloaded(song: List[Union[Song, CtFile]]):
    is_downloaded = any(
        get_download_filepath(path, song).is_file() for path in loaded_paths
    )
    is_downloaded and song.mark_downloaded()
    return is_downloaded


def download_file(song):
    if is_downloaded(song):
        print(f"{song.name} already exists, now skipping...")
        return
    file = ctfile_service.get_file(song)
    download_url = ctfile_service.get_download_url(file)
    with tqdm(
        unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=song.name
    ) as t:
        tmp_filepath = get_tmp_download_filepath(song)
        urlretrieve(
            download_url, filename=tmp_filepath, reporthook=my_hook(t), data=None
        )
        t.total = t.n
    move_file_to_download_folder(tmp_filepath)
    song.mark_downloaded()


def move_file_to_download_folder(tmp_path: Path):
    shutil.move(str(tmp_path), str(download_path))

def download_song(song: Song):
    try:
        logging.info(song)
        download_file(song)
        return True
    except Exception:
        logging.exception(f"Error occurred while downloading {song.name}")
        get_tmp_download_filepath(song).unlink(missing_ok=True)
        return False



def download_all_songs(songs: List[Song]):
    """download all the songs provided

    Args:
        songs (List[Song]): songs from mvxz

    Returns:
    """
    for song in songs:
        download_song(song)


def setup_folder():
    shutil.rmtree(str(temp_path), ignore_errors=True)
    temp_path.mkdir(exist_ok=True)
    download_path.mkdir(exist_ok=True)


@dataclass
class SongResult:
    keyword: str
    page: int = 1
    song_queue: List[Song] = field(default_factory=deque)

    def process_top_x(self, number_of_songs:int = DOWNLOAD_BATCH_SIZE):
        count = 0
        while count < DOWNLOAD_BATCH_SIZE:
            if len(self.song_queue) < DOWNLOAD_BATCH_SIZE:
                self.page += 1
                self.get_song_by_page()
            breakpoint()
            song = self.song_queue.popleft()
            if not is_downloaded(song):
                continue
            elif download_song(song):
                count += 1
            else:
                self.song_queue.append(song)


    def get_song_by_page(self):
        breakpoint()
        songs = song_service.get_songs(self.keyword, self.page)
        self.song_queue.extend(songs)


def main(keywords: List[str]):  # , dfs: bool = typer.Option(True, "--dfs/--bfs")):
    setup_folder()
    keyword_queue = deque(SongResult(keyword) for keyword in keywords)
    # try:
    #     while keyword_queue:
    #         song_result = keyword_queue.popleft()
    #         songs = song_result.process_top_x()
    #         keyword_queue.append(song_result)
    # except Exception:
    #     logging.exception(f"unexpected error")
    while keyword_queue:
        song_result = keyword_queue.popleft()
        songs = song_result.process_top_x()
        keyword_queue.append(song_result)


if __name__ == "__main__":
    typer.run(main)

