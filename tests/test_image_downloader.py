import pytest
from pathlib import Path
from downloader import image_downloader
from unittest.mock import patch
from requests.exceptions import MissingSchema, HTTPError, ConnectionError


def get_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / filename


@pytest.fixture
def fake_dir(tmp_path):
    temp_dir = tmp_path / "images"
    temp_dir.mkdir()
    return temp_dir


@pytest.fixture
def get_not_existing_dir():
    return "not_existing_dir"


@pytest.fixture(name="existing_file")
def get_existing_url_file():
    return get_path("files/url_file.txt")


@pytest.fixture(name="not_existing_file")
def get_not_existing_url_file():
    return get_path("no_existing_file.txt")


@pytest.fixture(name="mixed_urls")
def get_mixed_url_file():
    return get_path("files/mixed_url_file.txt")


@pytest.fixture(name="working_url")
def get_valid_url():
    return "https://interactives.natgeofe.com/high-touch/ngm-23-YIP/builds/main/img/photos/MM9747_221026_13114.jpg"


def test_download_from_url_successful(fake_dir, working_url, caplog):
    image_downloader.download_image_from_url(working_url, fake_dir)
    assert len(caplog.records) == 0
    assert fake_dir.exists()
    assert len([*fake_dir.iterdir()]) == 1


def test_download_from_url_not_successful(fake_dir, caplog):
    img_url = "https://interactives.natgeofe.com/thisdoesnotexist.jpg"
    image_downloader.download_image_from_url(img_url, fake_dir)

    assert "403 Client Error" in caplog.records[0].message
    assert fake_dir.exists()
    assert len([*fake_dir.iterdir()]) == 0


def test_download_from_url_missing_schema(fake_dir, caplog):
    img_url = "www.interactives.natgeofe.com/high-touch/ngm-23-YIP/builds/main/img/photos/MM9747_221026_13114.jpg"
    image_downloader.download_image_from_url(
        img_url,
        fake_dir,
    )

    assert "No scheme supplied" in caplog.records[0].message
    assert fake_dir.exists()
    assert len([*fake_dir.iterdir()]) == 0


def test_download_from_file_successful(fake_dir, existing_file, caplog):
    image_downloader.download_image_from_file(existing_file, fake_dir)

    assert len(caplog.records) == 0
    assert fake_dir.exists()
    assert len([*fake_dir.iterdir()]) == 5


def test_download_from_file_partly_successful(fake_dir, mixed_urls, caplog):
    image_downloader.download_image_from_file(mixed_urls, fake_dir)
    assert "Failed to resolve" and "Max retries exceeded" in caplog.records[0].message
    assert "403 Client Error" in caplog.records[1].message
    assert fake_dir.exists()
    assert len([*fake_dir.iterdir()]) == 1


def test_download_from_file_not_existing_file(fake_dir, not_existing_file, caplog):
    with pytest.raises(FileNotFoundError):
        image_downloader.download_image_from_file(not_existing_file, fake_dir)
    assert len(caplog.records) == 1
    assert fake_dir.exists()


def test_download_from_file_not_existing_save_path(
    get_not_existing_dir, existing_file, caplog
):
    with pytest.raises(FileNotFoundError):
        image_downloader.download_image_from_file(existing_file, get_not_existing_dir)
    assert len(caplog.records) == 1
    assert caplog.records[0].message == f"{get_not_existing_dir} does not exist"
