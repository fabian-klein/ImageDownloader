import pytest
from pathlib import Path
from downloader.imageDownloader import ImageDownloader
from unittest.mock import patch


def get_path(filename: str) -> Path:
    file_path = Path(filename)
    return file_path.absolute()


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


def test_download_from_url_successful(fake_dir, working_url):
    with patch("logging.Logger.error") as mock_logger:
        ImageDownloader.download_image_from_url(working_url, fake_dir)
        mock_logger.assert_not_called()
        assert fake_dir.exists()
        assert len([*fake_dir.iterdir()]) == 1


def test_download_from_url_missing_schema(fake_dir):
    img_url = "www.interactives.natgeofe.com/high-touch/ngm-23-YIP/builds/main/img/photos/MM9747_221026_13114.jpg"
    with patch("logging.Logger.error") as mock_logger:
        ImageDownloader.download_image_from_url(
            img_url,
            fake_dir,
        )
        mock_logger.assert_called_once()
        mock_logger.assert_called_with(
            f"The following Exception happened: MissingSchema for Url {img_url}\n"
            f"Please check URLs"
        )
        assert fake_dir.exists()
        assert len([*fake_dir.iterdir()]) == 0


def test_download_from_url_not_successful(fake_dir):
    img_url = "https://interactives.natgeofe.com/thisdoesnotexist.jpg"
    with patch("logging.Logger.error") as mock_logger:
        ImageDownloader.download_image_from_url(img_url, fake_dir)

        mock_logger.assert_called_once()
        mock_logger.assert_called_with(
            f"The following Exception happened: HTTPError for Url {img_url}\n"
            f"Please check URLs"
        )
        assert fake_dir.exists()
        assert len([*fake_dir.iterdir()]) == 0


def test_download_from_file_successful(fake_dir, existing_file):
    ImageDownloader.download_image_from_file(existing_file, fake_dir)
    assert fake_dir.exists()
    assert len([*fake_dir.iterdir()]) == 5


def test_download_from_file_partly_successful(fake_dir, mixed_urls):
    with patch("logging.Logger.error") as mock_logger:
        ImageDownloader.download_image_from_file(mixed_urls, fake_dir)

        mock_logger.assert_called()
        logger_calls = mock_logger.call_args_list

        first_call = logger_calls[0]
        second_call = logger_calls[1]

        first_call_arguments = first_call[0]
        second_call_arguments = second_call[0]

        assert "ConnectionError" in first_call_arguments[0]
        assert "HTTPError" in second_call_arguments[0]
        assert fake_dir.exists()
        assert len([*fake_dir.iterdir()]) == 1


def test_download_from_file_not_existing_file(fake_dir, not_existing_file):
    with patch("logging.Logger.error") as mock_logger:
        with pytest.raises(FileNotFoundError):
            ImageDownloader.download_image_from_file(not_existing_file, fake_dir)

    mock_logger.assert_called_once()
    mock_logger.assert_called_with("File does not exist")
    assert fake_dir.exists()


def test_download_from_file_not_existing_save_path(get_not_existing_dir, existing_file):
    with patch("logging.Logger.error") as mock_logger:
        with pytest.raises(FileNotFoundError):
            ImageDownloader.download_image_from_file(
                existing_file, get_not_existing_dir
            )

    mock_logger.assert_called_once()
    mock_logger.assert_called_with("Path does not exist")
