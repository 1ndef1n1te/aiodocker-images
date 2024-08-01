import asyncio
import aiodocker
import argparse
import time
import aiofiles
import yaml
from pydantic import BaseModel, DirectoryPath
from loguru import logger


class RetagImages(BaseModel):
    new_tag: str | None
    new_repo_url: str | None

class SaveImages(BaseModel):
    save_images_directory: DirectoryPath
    retag_images: RetagImages | None = None

class Config(BaseModel):
    docker_images: list[str]
    save_images: SaveImages | None = None
    

def validate_config(config_file_name):
    with open(config_file_name) as config_file:
        config_data = yaml.safe_load(config_file)
    return Config(**config_data).dict()


async def docker_pull_images(docker_images_client, image):
    logger.info(f"Start pulling {image}")
    await docker_images_client.pull(image)
    logger.info(f"End pulling {image}")


async def docker_retag(docker_images_client, image, retag_images):
    await docker_images_client.tag(
        name=image,
        repo=f'{retag_images.get("new_repo_url")}/{image.split(":")[-2].split("/")[-1]}',
        tag=retag_images.get("new_tag"),
    )
    logger.info(f"Image: {image} successfully retagged | new repo url: {retag_images.get("new_repo_url")} | new tag: {retag_images.get("new_tag")}")

async def docker_save_image(docker_images_client, image, save_images_directory):
    tarball = docker_images_client.export_image(image)
    async with tarball as tar:
        tar_content = await tar.read()
        async with aiofiles.open(
            f"{save_images_directory}/{image.split('/')[-1].replace(':', '.')}.tar",
            mode="wb",
        ) as f:
            logger.info(f"Start saving {image}")
            await f.write(tar_content)
            logger.info(f"End saving {image}")


async def main(
    images: list,
    save_images: bool
):
    docker = aiodocker.Docker()
    docker_images_client = aiodocker.images.DockerImages(docker)

    # MAKE DOCKER PULL COROUTINES WITH ORIGINAL IMAGES
    pull_coros = [docker_pull_images(docker_images_client, image) for image in images]

    # PULL DOCKER IMAGES
    for coroutine in asyncio.as_completed(pull_coros):
        try:
            await coroutine
        except Exception as error:
            logger.error(f"Can`t pull image due to following error: {error}")

     
    if save_images is not None and save_images.get("retag_images") is not None:
        
        # MAKE RETAGGED COROUTINES
        retag_coros = [
            docker_retag(docker_images_client, image, save_images.get("retag_images")) for image in images
        ]

        # RETAG DOCKER IMAGES
        for coroutine in asyncio.as_completed(retag_coros):
            try:
                await coroutine
            except Exception as error:
                logger.error(f"Can`t retag image due to following error: {error}")

        # MAKE DOCKER SAVE COROUTINES WITH RETAGGED IMAGES
        save_coros = [
            docker_save_image(docker_images_client, f'{save_images.get("retag_images").get("new_repo_url")}/{image.split(":")[-2].split("/")[-1]}:{save_images.get("retag_images").get("new_tag")}', save_images.get("save_images_directory"))
            for image in images
        ]

    elif save_images is not None and save_images.get("retag_images") is None:

        # MAKE DOCKER SAVE COROUTINES WITH ORIGINAL IMAGES
        save_coros = [
            docker_save_image(docker_images_client, image, save_images.get("save_images_directory"))
            for image in images
        ]

    # SAVE DOCKER IMAGES
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
    print(config_data)
    start_time = time.perf_counter()
    asyncio.run(
        main(
            config_data.get("docker_images"),
            config_data.get("save_images")
        )
    )
    end_time = time.perf_counter() - start_time
    logger.info(f"Total time elapsed: {end_time:.2f}")
