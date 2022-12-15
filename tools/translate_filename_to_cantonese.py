import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

from decouple import config
from opencc import OpenCC

cc = OpenCC("s2t")

LOCAL_FOLDER = config("SONG_LOCAL_PATH")
KTV_FOLDER = Path(LOCAL_FOLDER)
KTV_SUFFIX = "_[MVXZ.com]_MV下载王"
KTV_FOLDERS = [KTV_FOLDER, KTV_FOLDER / "Loaded", KTV_FOLDER / "Loaded 2"]
KTV_FOLDERS = [folder for folder in KTV_FOLDERS if folder.exists()]


def translate_to_cantonese(to_convert: str) -> str:
    return cc.convert(to_convert)


def get_file_mapping() -> Dict[str, List[Path]]:
    filename_mapping = defaultdict(lambda: [])
    for folder in KTV_FOLDERS:
        if not folder.exists():
            continue
        for file in folder.iterdir():
            if file.is_file():
                filename_mapping[get_filename(file)].append(file)
    return filename_mapping


def get_all_file() -> List[Path]:
    return [
        file for folder in KTV_FOLDERS for file in folder.iterdir() if file.is_file()
    ]


def translate_filename_to_cantonese():
    for file in get_all_file():
        folder = file.parent.resolve()
        canto_filename = translate_to_cantonese(file.name)
        os.rename(str(file), str(folder / canto_filename))


def remove_duplicate_files():
    filename_mapping = get_file_mapping()
    duplicated_filename_mapping = dict(
        filter(lambda elem: len(elem[1]) > 1, filename_mapping.items())
    )
    if duplicated_filename_mapping:
        print("Remove duplicated files...")
    for list_of_same_files in duplicated_filename_mapping.values():
        for file in list_of_same_files:
            if get_filename(file).endswith(KTV_SUFFIX):
                file.unlink(missing_ok=True)
    return


def main():
    remove_duplicate_files()
    translate_filename_to_cantonese()


if __name__ == "__main__":
    main()
