import responses
from pytest import fixture, mark

from ktv_bot.services.ctfile.file import CtFile, CtFileObject


@fixture
def duration():
    return 56


@fixture
def file_size():
    return 56.52


@fixture
def json_response(faker, duration, file_size):
    return {
        "file": {
            "file_id": faker.pyint(),
            "file_name": faker.pystr(),
            "userid": faker.pyint(),
            "file_chk": faker.pystr(),
            "free_speed": f"{duration} min ",
            "vip_speed": f"{duration} min ",
            "file_size": f"{file_size} MB",
        }
    }


@mark.parametrize(
    ("time", "time_in_min"),
    [("1 hr 8 min 24 sec", 68), ("2 hr ", 120), ("56 min ", 56), ("24 sec", 1)],
)
def test_duration_parse_time(time, time_in_min):
    assert CtFileObject._parse_duration(time) == time_in_min


def test_from_json_works(json_response, duration, file_size):
    file_info = CtFileObject.from_json(json_response)
    assert file_info.duration_in_min == duration
    assert file_info.size == file_size
