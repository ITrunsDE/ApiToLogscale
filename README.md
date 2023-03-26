# Ingest JSON data from API calls directly to Logscale

## Idea
You have an API that provides data for your Logscale repository. At the moment you have to get it from the API and send it to your Logscale instance via a bash script. That you also have to schedule via a cronjob.

Why not using a Docker container that runs the code in that interval that you specified and gets the data from the API and sends it to your Logscale repository.

## Installation

The installation is quite simple. Just clone the repository and run the make command, to build the docker container.

```bash
git clone ITrunsDE/ApiToLogscale
make build
```

## Basic configuration

Before you start your container, you should configure your **config.yaml**. 

```yaml
logscale_url: "https://cloud.community.humio.com" # or https://cloud.humio.com

repository:
  your_repo_name:
    token: ffffffff-ffff-ffff-ffff-ffffffffffff # repo ingest token

api:
  api_call_1:
    name: "Your API identifier"
    url: "https://api12.test.com/apiv1/get_data.php?test=1"
    to_repository: your_repo_name # must match the name of the repo
    interval:
      min: 1
```

## Start the docker container

To run the docker container you can use the make command.

```bash
make up
```

This will run the container and first API call will start at the first end of the interval. If you have an interval of 1 minute, the first call will occur 1 minute after the first start of the container.

If you change something in your **config.yaml** you have to restart the container.

## Advanced configuration

### Multiple Logscale repositories

To add another repository you can just copy the exisiting code block or use the sample one.

```yaml
  another_repo:
    token: ffffffff-ffff-ffff-ffff-ffffffffffff
```

The repo name **another_repo** is use an identifier in the API call section **to_repository**.


### Multiple API calls

You can have multiple API calls to different locations at different intervals. Simply add the following code block and change your settings.

```yaml
  another_api_call:
    name: "Your API identifier"
    url: "https://your_url_to_call_the_api"
    to_repository: another_repo_name # must match the name of the repo
    interval:
      min: 60
```
