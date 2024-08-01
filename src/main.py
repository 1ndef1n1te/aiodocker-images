import asyncio
import aiodocker
import argparse
import time
import aiofiles
import yaml
from pydantic import BaseModel, Field, DirectoryPath
from loguru import logger


class Config(BaseModel):
    docker_images: list[str]
    save_images: bool
    save_images_directory: DirectoryPath = Field(default="/aiodocker-saved-images")


def validate_config(config_file_name):
    with open(config_file_name) as config_file:
        config_data = yaml.safe_load(config_file)
    return Config(**config_data).dict()


async def docker_pull_images(docker_images_client, image):
    logger.info(f"Start pulling {image}")
    await docker_images_client.pull(image)
    logger.info(f"End pulling {image}")


async def docker_save_image(docker_images_client, image, save_images_directorys):
    tarball = docker_images_client.export_image(image)
    async with tarball as tar:
        tar_content = await tar.read()
        async with aiofiles.open(
            f"{save_images_directorys}/{image.split('/')[-1].replace(':', '.')}.tar",
            mode="w",
        ) as f:
            logger.info(f"Start saving {image}")
            await f.write(tar_content.decode(encoding="latin-1"))
            logger.info(f"End saving {image}")


async def main(images: list, save_images: bool, save_images_directory: str):
    docker = aiodocker.Docker()
    docker_images_client = aiodocker.images.DockerImages(docker)
    pull_coros = [docker_pull_images(docker_images_client, image) for image in images]
    for coroutine in asyncio.as_completed(pull_coros):
        try:
            await coroutine
        except Exception as error:
            logger.error(f"Can`t pull image due to following error: {error}")
    print(pull_coros)
    if save_images:
        save_coros = [
            docker_save_image(docker_images_client, image, save_images_directory)
            for image in images
        ]
        for coroutine in asyncio.as_completed(save_coros):
            try:
                await coroutine
            except Exception as error:
                logger.error(f"Can`t save image due to following error: {error}")
    await docker.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Config file with YAML format", required=True)
    args = parser.parse_args()
    config_file_name = args.config
    config_data = validate_config(config_file_name)
    start_time = time.perf_counter()
    asyncio.run(
        main(
            config_data.get("docker_images"),
            config_data.get("save_images"),
            config_data.get("save_images_directory"),
        )
    )
    end_time = time.perf_counter() - start_time
    logger.info(f"Total time elapsed: {end_time:.2f}")
