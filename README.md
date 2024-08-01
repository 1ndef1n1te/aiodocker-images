# aiodocker-images

## Description

Tool for async pull and save docker images.

## Purpose

Making faster operations with pulling and saving docker images by using python asyncio and aiodocker

## Usage


### Config file schema

- `docker_images`: `yaml list`: list of docker images
- `save_images`: `yaml Boolean`
    - `save_images_directory`: `yaml str`: path to **existing** directory for saving pulled images
    - `retag_images`: `yaml dict`
        - `new_repo_url`: `yaml str`: new URL for retagging process
        - `new_tag`: `yaml str`: new tag for retagging process
        - 
For **pulling** images fill `docker_images` directive

For **pulling and saving** images fill `docker_images` and `save_images:save_images_directory` directive

For **pulling, retagging and saving** retagged images fill `docker_images` and `save_images:save_images_directory`, `save_images:retag_images` directive

### Run with docker command

1) Build docker image: `docker build -t aiodocker-images:main .`
2) Run docker container: `docker run -d -v /var/run/docker.sock:/var/run/docker.sock -v ./aiodocker_config.yaml:/aiodocker_config.yaml -v ./saved-images:/aiodocker-saved-images aiodocker-images:main`
3) Your saved images will be in `./saved-images` directory

### Run with docker-compose.yaml

1) Run docker-compose.yaml: `docker-compose up -d`
2) Your saved images will be in `./saved-images` directory

### Logs

For viewing logs use `docker logs {container-id}` command