import argparse
import requests
import logging
import os
import sys
from typing import List
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def get_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / filename


def download_image_from_url(
        img_url: str, save_path: str | Path, override: bool = True
):
    img = _download_image(img_url)
    if img:
        img_name = img_url.split("/")[-1]
        save_path = save_path / img_name
        if os.path.isfile(save_path) and not override:
            LOGGER.warning(f"Image not saved! File {save_path}  already exists!")
        else:
            with open(save_path, mode="wb") as img_f:
                img_f.write(img)


def download_image_from_file(
        filename: str | os.PathLike, save_path: str | os.PathLike, override: bool = True
):
    # if not os.path.isfile(get_path(filename)):
    if not os.path.isfile(filename):
        error_msg = f"{filename} does not exist"
        LOGGER.error(error_msg)
        raise FileNotFoundError(error_msg)

    # if not os.path.isdir(get_path(save_path)):
    if not os.path.isdir(save_path):
        error_msg = f"{save_path} does not exist"
        LOGGER.error(error_msg)
        raise FileNotFoundError(error_msg)

    #    save_path = get_path(save_path)
    save_path = save_path

    # img_urls = _get_urls_from_file(get_path(filename))
    img_urls = _get_urls_from_file(filename)

    for img_url in img_urls:
        download_image_from_url(img_url, save_path, override)


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


def _get_urls_from_file(filename: str | os.PathLike) -> List[str]:
    # with open(get_path(filename), mode="r") as f:
    with open(filename, mode="r") as f:
        urls = [img_url.rstrip() for img_url in f if img_url.rstrip()]
    return urls


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", dest='file_name')
    parser.add_argument("-o", "--output-folder", dest='output_folder')
    args = parser.parse_args()

    input_file = args.file_name
    output_folder = args.output_folder

    print(input_file)
    print(output_folder)
    download_image_from_file(input_file, output_folder)
