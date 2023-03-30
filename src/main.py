import datetime
import logging
import os
import time
from logging.handlers import RotatingFileHandler

import schedule
import yaml
from humiolib.HumioClient import HumioIngestClient
from requests import Response, get


def send_api_call(
        api_url: str,
        header: list | None = None,
) -> Response:
    headers = {'User-Agent': 'Apispark.net/1.0'}

    # append the headers from the config file
    if None is not header:
        headers_api = dict.fromkeys(header)
        headers.update(headers_api)

    return get(url=api_url, headers=headers)


def send_to_logscale(
        logscale_url: str,
        ingest_token: str,
        attributes: dict,
) -> None:
    # Creating the client
    client = HumioIngestClient(
        base_url=logscale_url,
        ingest_token=ingest_token)

    # Ingesting Structured Data
    structured_data = [
        {
            "tags": {"host": "Apispark.net/1.0"},
            "events": [
                {
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                    "attributes": attributes
                }
            ]
        }
    ]

    # ingest data
    client.ingest_json_data(structured_data)


def load_config() -> dict:
    logging.debug('Loading config.yaml')
    
    if not os.path.exists('config.yaml'):
        logging.error('config.yaml file not found')
        raise Exception('config.yaml file not found')

    logging.debug('Reading config.yaml')

    # read config file
    with(open('config.yaml', 'r') as fp):
        config = yaml.safe_load(fp)

    return config


def api_to_logscale(
        api_url: str,
        logscale_url: str,
        ingest_token: str
) -> None:

    # get data from api call
    data = send_api_call(api_url=api_url)

    # send data to logscale
    send_to_logscale(logscale_url=logscale_url,
                     ingest_token=ingest_token, attributes=data.json())


def schedule_jobs() -> None:

    config = load_config()

    # check config file
    if config['logscale_url'] == '':
        raise Exception('Logscale url not entered')

    # check for each api call
    for api in config['api'].values():

        # check for the correct configuration of the repository file
        to_repository = api.get('to_repository')
        if None is to_repository:
            raise KeyError(
                'The field [to_repository] is not set found or empty.')

        # get the ingest token for the data
        ingest_token = config.get('repository').get(to_repository).get('token')
        if None is ingest_token:
            raise KeyError(
                'Token for repository [' + to_repository + '] not found! Please check your config.yaml.')

        # get the interval
        interval = api.get('interval')
        if None is interval:
            raise KeyError(
                'Interval is not set or empty. Please add min or hour.')

        interval_min = interval.get('min')

        # check if the interval is set correct
        if None is interval_min:
            raise KeyError(
                'Missing interval for min(utes).')

        # log info of scheduled job
        logging.info('Creating job [{0}] [{1}min] call [{2}].'.format(
            api.get('name'), interval_min, api.get('url')))

        # set interval correct
        if interval_min == 1:
            schedule.every(interval_min).minute.do(api_to_logscale, api.get(
                'url'), config.get('logscale_url'), ingest_token).tag(api.get('name'))
        else:
            schedule.every(interval_min).minutes.do(api_to_logscale, api.get(
                'url'), config.get('logscale_url'), ingest_token).tag(api.get('name'))

    # get scheduled jobs
    for job in schedule.jobs:
        logging.debug(job)


if __name__ == "__main__":

    # Create the root logger
    logging.basicConfig(level=logging.DEBUG)

    # Create a RotatingFileHandler with a max size of 10MB and a max of 5 backup files
    handler = RotatingFileHandler(
        '/logs/apispark.log', maxBytes=10*1024*1024, backupCount=5)

    # Set the logging level
    handler.setLevel(logging.DEBUG)

    # Set the log format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the root logger
    logging.getLogger().addHandler(handler)

    logging.info('Starting main program')

    # schedule jobs from config.yaml
    schedule_jobs()

    # run jobs
    while True:
        schedule.run_pending()
        time.sleep(1)
