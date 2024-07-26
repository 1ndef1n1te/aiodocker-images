import asyncio
import aiodocker
import time
import aiofiles
import yaml
from pydantic import BaseModel, Field
from loguru import logger

class Config(BaseModel):
    registry_url: str = Field(default="docker.io") 
    docker_images: list[str]
    save_images: bool

def validate_config(config_file_name):
    with open(config_file_name) as config_file:
        config_data = yaml.safe_load(config_file)
    return Config(**config_data).dict()

async def docker_pull_images(docker_images_client, image):
    logger.info(f"Start pulling {image}")
    await docker_images_client.pull(image)
    logger.info(f"End pulling {image}")

async def docker_save_image(docker_images_client, image):
    tarball = docker_images_client.export_image(image)
    async with tarball as tar:
        tar_content = await tar.read()
        async with aiofiles.open(
            f"{image.split('/')[-1].replace(':', '.')}.tar", mode="w"
        ) as f:
            await f.write(tar_content.decode(encoding="latin-1"))

async def main(images: list, save_images: bool):
    docker = aiodocker.Docker()
    docker_images_client = aiodocker.images.DockerImages(docker)
    pull_coros = [docker_pull_images(docker_images_client, image) for image in images]
    await asyncio.gather(*pull_coros)
    if save_images:
      save_coros = [docker_save_image(docker_images_client, image) for image in images]
      await asyncio.gather(*save_coros)
    await docker.close()

if __name__ == "__main__":
    start_time = time.perf_counter()
    config_file_name = "aiodocker_config.yaml"
    config_data = validate_config(config_file_name)
    asyncio.run(
        main(config_data.get("docker_images"), config_data.get("save_images"))
    )
    end_time = time.perf_counter() - start_time
    print(f"Total time elapsed: {end_time:.2f}")