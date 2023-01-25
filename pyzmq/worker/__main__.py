#!/usr/src/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import zmq
import requests

from typing import Dict
from multiprocessing import Process
from pyzmq.core.commons import log_lvl, log_str
from pyzmq.core.logger import get_logger

logger = get_logger(log_lvl, log_str, __name__)


def get_info(data: Dict, results_sender: zmq.Context = None):
    r = requests.get(f"https://swapi.dev/api/people/{data['data']}/")
    logger.debug(f"response: r{r}")
    if r.status_code == 200:
        # Send results to sink
        results_sender.send_json({"status": "ok", "result": r.json()})
    else:
        logger.debug(f"Error: {r.status_code}")
        results_sender.send_json({"status": "error", "message": f"{r.status_code}: {r.content}"})


def worker(worker_num: int, context: zmq.Context = None) -> None:
    logger.debug(f"Worker {worker_num} ready for listening")
    # Initialize a zeromq context
    ctx = context or zmq.Context.instance()
    with ctx:
        work_receiver = ctx.socket(zmq.PULL)
        work_receiver.connect("tcp://127.0.0.1:5557")

        results_sender = ctx.socket(zmq.PUSH)
        results_sender.connect("tcp://127.0.0.1:5558")

        poller = zmq.Poller()
        poller.register(work_receiver, zmq.POLLIN)

        while True:
            socks = dict(poller.poll())
            if socks.get(work_receiver) == zmq.POLLIN:
                work_message: Dict = work_receiver.recv_json()
                logger.debug(f"Worker {worker_num} received work: {work_message}")
                get_info(work_message, results_sender)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="ZeroMQ workers",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.0'
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("-w", "--workers", type=int, default=1)
        params: Dict = vars(parser.parse_args())
        worker_pool = range(params['workers'])

        context = zmq.Context()

        for wrk_num in range(len(worker_pool)):
            Process(target=worker, args=(wrk_num, context,)).start()
    except Exception as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received, exiting.")
        sys.exit(0)
