from __future__ import annotations

import logging
import platform
import shutil
import socket
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union
from urllib.request import urlcleanup
from urllib3.connection import HTTPConnection
import requests

import typer
from decouple import Csv, config
from tqdm import tqdm

import logging_config
from ktv_bot.services.ctfile.file import CtFile
from ktv_bot.services.mvxz.songs import Song, SongService

logger = logging.getLogger()

song_service = SongService()
ctfile_service = CtFile()
LOCAL_FOLDER_LIST = config("SONG_LOCAL_PATH", cast=Csv())


def get_folder_path(LOCAL_FOLDER_LIST: List[str]):
    loaded_paths = []
    for folder in LOCAL_FOLDER_LIST:
        if not Path(folder).exists():
            raise FileNotFoundError(f"{folder} doesn't exist")
        elif not Path(folder).is_dir():
            raise NotADirectoryError(f"{folder} is not a directory")
        else:
            loaded_paths.append(Path(folder).resolve())
    return loaded_paths


loaded_paths = get_folder_path(LOCAL_FOLDER_LIST)
print(loaded_paths)
download_path = loaded_paths[0]
temp_path = Path().resolve() / "temp"
DOWNLOAD_BATCH_SIZE = 5
socket.setdefaulttimeout(60 * 5)


def my_hook(t):
    last_block = [0]

    def update_to(block_cnt=1, block_size=1, total_size=None):
        if total_size is not None:
            t.total = total_size
        t.update((block_cnt - last_block[0]) * block_size)
        last_block[0] = block_cnt

    return update_to


def get_download_filepath(path: Path, song: Union[Song, CtFile]) -> Path:
    if song.name.endswith(".mkv"):
        return path / song.name
    return path / f"{song.name}.mkv"


def get_tmp_path(song: Union[Song, CtFile]) -> Path:
    return get_download_filepath(temp_path, song)


def is_downloaded(song: List[Union[Song, CtFile]]):
    return any(get_download_filepath(path, song).is_file() for path in loaded_paths)


def move_file_to_download_folder(tmp_path: Path):
    logger.info(f"move files from {str(tmp_path)}, {str(download_path)}")
    shutil.move(str(tmp_path), str(download_path))


def download_song(song: Song) -> int:
    # return 0: download failed
    #        1: download success
    #       -1: file not available
    try:
        if is_downloaded(song):
            logging.info(f"{song.name} already exists, now skipping...")
            return 1
        try:
            logging.info(song)
            download_url = ctfile_service.get_url_from_song(song)
        except Exception as e:
            return -1
        with tqdm(
            unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=song.name
        ) as t:
            tmp_filepath = get_tmp_path(song)
            download_file(download_url, filename=tmp_filepath, reporthook=my_hook(t))
            t.total = t.n
        move_file_to_download_folder(tmp_filepath)
        return 1
    except Exception:
        logging.exception(f"Error occurred while downloading {song.name}")
        return 0


class HTTPAdapterWithSocketOptions(requests.adapters.HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.socket_options = kwargs.pop("socket_options", None)
        super(HTTPAdapterWithSocketOptions, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.socket_options is not None:
            kwargs["socket_options"] = self.socket_options
        super(HTTPAdapterWithSocketOptions, self).init_poolmanager(*args, **kwargs)


def download_file(url, filename, reporthook):
    # NOTE the stream=True parameter below
    adapter = HTTPAdapterWithSocketOptions(
        socket_options=HTTPConnection.default_socket_options
        + [
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
            (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1),
            (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3),
            (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5),
        ]
    )
    s = requests.session()
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    with s.get(url, stream=True) as r:
        r.raise_for_status()
        total_length = int(r.headers.get("content-length"))
        block_cnt = 0
        block_size = 1024
        reporthook(block_cnt, block_size, total_length)
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=block_size):
                if len(chunk) == 0:
                    logger.debug(f"received chunksize: {len(chunk)}")
                block_cnt += 1
                f.write(chunk)
                reporthook(block_cnt, block_size, total_length)


def setup_folder():
    shutil.rmtree(str(temp_path), ignore_errors=True)
    temp_path.mkdir(exist_ok=True)
    download_path.mkdir(exist_ok=True)


@dataclass
class SongResult:
    keyword: str
    page: int = 0
    song_cnt: int = 0
    song_queue: List[Song] = field(default_factory=deque)
    all_downloaded = False

    def process_top_x(self, max_songs: int = DOWNLOAD_BATCH_SIZE):
        count = 0
        while count < max_songs:
            if len(self.song_queue) < max_songs:
                self.get_songs_in_next_page()
            if not self.song_queue:  # no more songs
                self.all_downloaded = True
                return
            song = self.song_queue.popleft()
            if is_downloaded(song):
                logging.info(f"{song.name} already exists, now skipping...")
                self.song_cnt += 1
                continue
            download_result = download_song(song)
            if download_result == 1:
                count += 1
                self.song_cnt += 1
            elif download_result == 0:
                self.song_queue.append(song)

    def get_songs_in_next_page(self):
        self.page += 1
        logger.info(f"fetching next songs, {self.keyword} page: {self.page}")
        songs = song_service.get_songs(self.keyword, self.page)
        logger.info(
            f"we have {len(self.song_queue)} in the Q & find {len(songs)} songs in page {self.page}"
        )
        self.song_queue.extend(songs)


def main(keywords: List[str]):  # , dfs: bool = typer.Option(True, "--dfs/--bfs")):
    setup_folder()
    keyword_queue = deque(SongResult(keyword) for keyword in keywords)
    while keyword_queue:
        song_result = keyword_queue.popleft()
        logger.info(f"Processing {song_result.keyword}")
        song_result.process_top_x()
        if song_result.song_queue:
            keyword_queue.append(song_result)


if __name__ == "__main__":
    typer.run(main)
