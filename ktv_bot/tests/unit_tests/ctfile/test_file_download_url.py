import responses
from pytest import fixture, mark


from ktv_bot.services.ctfile.file_download_url import CtFileDownloadUrl
from ktv_bot.services.ctfile.value_objects.file_object import CtFileObject


@fixture
def file_info(faker):
    return CtFileObject(
        id=faker.pyint(),
        name=faker.pystr(),
        user_id=faker.pyint(),
        chunk=faker.pystr(),
        duration_in_min=faker.pyint(),
        vip_duration_in_min=faker.pyint(),
        size=faker.pyfloat(),
    )


@fixture
def api_url(faker):
    return faker.url().strip("/")


@fixture
def download_url(faker):
    return faker.url()


@fixture
def api_response(faker, download_url):
    return {
        "downurl": download_url,
        "code": 200,
        "pop": 1,
        "file_size": 40662644,
        "file_name": faker.pystr(),
        "xhr": True,
    }


@responses.activate
def test__from_json_return_object(api_url, api_response, file_info, download_url):
    responses.add(responses.GET, api_url, json=api_response)
    assert download_url == CtFileDownloadUrl(api_url=api_url).get_url(file_info)
