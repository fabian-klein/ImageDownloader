import requests
import logging
import os
import sys
from typing import List

LOGGER = logging.getLogger(__name__)


def get_path(path: str | os.PathLike):
    return os.path.abspath(path)


class ImageDownloader:

    @staticmethod
    def download_image_from_url(
            img_url: str, save_path: str | os.PathLike, override: bool = True
    ):
        img = ImageDownloader._download_image(img_url)
        if img:
            img_name = img_url.split("/")[-1]
            save_path = str(save_path) + "/" + img_name
            if os.path.isfile(save_path) and not override:
                LOGGER.warning(
                    "Image not saved! File " + save_path + " already exists!"
                )
            else:
                with open(save_path, mode="wb") as img_f:
                    img_f.write(img)

    @staticmethod
    def download_image_from_file(
            filename: str | os.PathLike, save_path: str | os.PathLike, override: bool = True
    ):
        if not os.path.isfile(get_path(filename)):
            LOGGER.error("File does not exist")
            raise FileNotFoundError

        if not os.path.isdir(get_path(save_path)):
            LOGGER.error("Path does not exist")
            raise FileNotFoundError

        save_path = get_path(save_path)
        img_urls = ImageDownloader._get_urls_from_file(get_path(filename))
        for img_url in img_urls:
            if img_url:
                ImageDownloader.download_image_from_url(img_url, save_path, override)

    @staticmethod
    def _download_image(img_url: str) -> bytes | None:
        try:
            response = requests.get(img_url, timeout=5)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            LOGGER.error(
                f"The following Exception happened: {type(e).__name__} for Url {img_url}\n"
                f"Please check URLs"
            )

    @staticmethod
    def _get_urls_from_file(filename: str | os.PathLike) -> List[str]:
        with open(get_path(filename), mode="r") as f:
            urls = [img_url.strip("\n") for img_url in f if img_url]
        return urls


if __name__ == "__main__":
    file = sys.argv[1]
    dest = sys.argv[2]
    ImageDownloader.download_image_from_file(file, dest)
