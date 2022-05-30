import responses
from pytest import fixture, raises

from ktv_bot.services.ctfile.file import CtFile


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


@fixture
def not_found_response():
    return {"code": 404, "message": "The share does not exist or has expired."}


@responses.activate
def test__get_file_return_object(api_url, api_response, fid, name):
    responses.add(responses.GET, api_url, json=api_response)
    file_object = CtFile(api_url=api_url).get_file(fid)
    assert file_object.name == name


@responses.activate
def test__get_file_raise_not_found_exception(api_url, not_found_response, fid, name):
    responses.add(responses.GET, api_url, json=not_found_response)
    with raises(Exception):
        CtFile(api_url=api_url).get_file(fid)
