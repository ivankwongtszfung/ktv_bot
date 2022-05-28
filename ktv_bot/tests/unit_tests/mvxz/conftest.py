from pathlib import Path

from pytest import fixture


@fixture
def html_dir():
    return Path(__file__).parent / "html"
