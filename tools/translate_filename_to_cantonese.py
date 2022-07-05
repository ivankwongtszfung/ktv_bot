import os
import string
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import typer
from opencc import OpenCC

cc = OpenCC("s2t")

KTV_FOLDER = Path("/mnt/c/Users/invok/Desktop/KTV/")
KTV_SUFFIX = "_[MVXZ.com]_MV下载王"
KTV_FOLDERS = [KTV_FOLDER]


def translate_to_cantonese(to_convert: str) -> str:
    return cc.convert(to_convert)


def get_file_mapping() -> Dict[str, List[Path]]:
    filename_mapping = defaultdict(lambda: [])
    for folder in KTV_FOLDERS:
        for file in folder.iterdir():
            if file.is_file():
                filename_mapping[get_filename(file)].append(file)
    return filename_mapping


def get_all_file() -> List[Path]:
    return [
        file for folder in KTV_FOLDERS for file in folder.iterdir() if file.is_file()
    ]


def get_filename(file: Path):
    name, _ = os.path.splitext(file.name)
    return name[: -len(KTV_SUFFIX)] if name.endswith(KTV_SUFFIX) else name


def title_singer_and_song(filename: str):
    singers, suffix = filename.split("-", 1)
    song_name, suffix = suffix.split("_", 1)
    idx = song_name.find("(")
    if idx != -1:
        song_name, song_suffix = song_name[:idx], song_name[idx:]
    else:
        song_name, song_suffix = song_name, ""
    return f"{singers}-{string.capwords(song_name)}{song_suffix}_{suffix}"


def replace_underscore(filename: str):
    singers, suffix = filename.split("-", 1)
    return f"{singers.replace('_', '+')}-{suffix}"


def translate_filename_to_cantonese(dry_run):
    for file in get_all_file():
        filename = get_filename(file)
        folder, ext = file.parent.resolve(), file.suffix
        canto_filename = translate_to_cantonese(filename)
        canto_filename = title_singer_and_song(canto_filename)
        canto_filename = replace_underscore(canto_filename)
        canto_path = folder / f"{canto_filename}{ext}"
        if file == canto_path:
            continue
        print(file, canto_path)
        if not dry_run:
            result = os.rename(file, canto_path)


def remove_duplicate_files(dry_run: bool = False):
    filename_mapping = get_file_mapping()
    duplicated_filename_mapping = dict(
        filter(lambda elem: len(elem[1]) > 1, filename_mapping.items())
    )
    if duplicated_filename_mapping:
        print("Show duplicated files...")
    for list_of_same_files in duplicated_filename_mapping.values():
        for file in list_of_same_files:
            if get_filename(file).endswith(KTV_SUFFIX):
                print(file) if dry_run else file.unlink(missing_ok=True)
    return


def main(dry_run: bool = False, remove_only: bool = False):
    remove_duplicate_files(dry_run)
    if remove_only:
        return
    translate_filename_to_cantonese(dry_run)


if __name__ == "__main__":
    typer.run(main)
