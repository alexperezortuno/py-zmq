#!/usr/src/env python
# -*- coding: utf-8 -*-
import sys
import zmq

from typing import Dict
from pyzmq.core.commons import log_lvl, log_str
from pyzmq.core.logger import get_logger

logger = get_logger(log_lvl, log_str, __name__)


def start():
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:5558")

    while True:
        try:
            s: Dict = receiver.recv_json()
            if 'result' in s:
                logger.debug(f"Received request: {s['result']['name']}")

            if 'status' in s and s['status'] == 'error':
                logger.debug(f"Result: {s['message']}")
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    try:
        start()
    except Exception as ex:
        logger.error(f"{ex}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user, killing server…")
        sys.exit(0)
