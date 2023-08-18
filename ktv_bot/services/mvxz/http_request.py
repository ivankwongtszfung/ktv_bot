from abc import ABC
from urllib.parse import urljoin, urlparse

from decouple import config


class MvxzRequestor(ABC):
    def _header(self):
        return {
            "Host": self._get_host(),
            # "Origin": self._get_origin(),
            "Referer": self._get_referer(),
        }

    def _get_referer(self):
        return urljoin(config('MVXZ_URL'), "isearch.asp")

    def _get_origin(self):
        return config("MVXZ_URL")

    def _get_host(self):
        return urlparse(config("MVXZ_URL")).netloc
