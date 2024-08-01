# aiodocker-images

## Description

Tool for async pull and save docker images.

## Purpose

Making faster operations with pulling and saving docker images by using python asyncio and aiodocker

## Usage

### Config file schema

- docker_images: `yaml list`: list of docker images
- save_images: `yaml Boolean`
    - True: save images to directory, directory with saved images inside container is `/aiodocker-saved-images`, this directory should be specify in docker volume
    - False: do not save images
- save_images_directory: `yaml str`: **existing** directory where to save pulled images
### Run with docker command

1) Build docker image: `docker build -t aiodocker-images:main .`
2) Run docker container: `docker run -d -v /var/run/docker.sock:/var/run/docker.sock -v ./aiodocker_config.yaml:/aiodocker_config.yaml -v ./saved-images:/aiodocker-saved-images aiodocker-images:main`
3) Your saved images will be in `./saved-images` directory

### Run with docker-compose.yaml

1) Run docker-compose.yaml: `docker-compose up -d`
2) Your saved images will be in `./saved-images` directory

### Logs

For viewing logs use `docker logs {container-id}` command