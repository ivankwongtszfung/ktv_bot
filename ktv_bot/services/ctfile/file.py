from dataclasses import dataclass
from typing import Dict
import requests

from decouple import config

FILE_URL = f"{config('CTFILE_URL')}/getfile.php"


@dataclass
class CtFileObject:
    id: int
    name: str
    user_id: int
    chunk: str  # an id used internally to identify the object
    duration_in_min: int
    vip_duration_in_min: int
    size: str

    @classmethod
    def from_json(cls, json: Dict[str, any]):
        info = json["file"]
        return cls(
            id=info["file_id"],
            name=info["file_name"],
            user_id=info["userid"],
            chunk=info["file_chk"],
            duration_in_min=cls._parse_duration(info["free_speed"]),
            vip_duration_in_min=cls._parse_duration(info["vip_speed"]),
            size=info["file_size"],
        )

    @staticmethod
    def _parse_duration(duration):
        # duration has at least 5 character
        time_map = {"hr": 3600, "min": 60, "sec": 1}
        i = cursor = duration_in_sec = 0
        while i < len(duration) - 2:
            trigram = duration[i : i + 3].strip()
            if trigram in time_map:
                duration_in_sec += int(duration[cursor:i]) * time_map[trigram]
                cursor = i = i + 3
            else:
                i += 1
        return max(duration_in_sec // 60, 1)


class CtFile:
    def __init__(self, **kwargs):
        self.api_url = kwargs.get("api_url") or FILE_URL

    def get_file(self, fid: str) -> CtFileObject:
        # fid is {user_id}-{file_id}
        response = requests.get(self.api_url, params={"f": fid})
        return CtFileObject.from_json(response.json())

    def get_download_url(self, ctfile_obj: CtFileObject) -> str:
        pass
