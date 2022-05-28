from pytest import mark, fixture
import responses
from ktv_bot.services.ctfile.file import CtFile, CtFileObject


@mark.parametrize(
    ("time", "time_in_min"),
    [("1 hr 8 min 24 sec", 68), ("2 hr ", 120), ("56 min ", 56), ("24 sec", 1)],
)
def test_duration_parse_time(time, time_in_min):
    assert CtFileObject._parse_duration(time) == time_in_min


@fixture
def api_url(faker):
    return faker.url().strip("/")


@fixture
def fid(faker):
    return faker.pystr()


@fixture
def name(faker):
    return faker.pystr()


@fixture
def api_response(faker, name):
    return {
        "code": 200,
        "file": {
            "file_name": name,
            "file_size": "58.08 MB",
            "userid": 2836101,
            "file_id": 421960335,
            "free_speed": "48 sec",
            "vip_speed": "12 sec",
            "file_chk": faker.pystr(),
        },
    }


@responses.activate
def test__from_json_return_object(api_url, api_response, fid, name):
    responses.add(responses.GET, api_url, json=api_response)
    file_object = CtFile(api_url=api_url).get_file(fid)
    assert file_object.name == name
