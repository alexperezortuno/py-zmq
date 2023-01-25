#!/usr/src/env python
# -*- coding: utf-8 -*-
import random
import sys

import zmq
import zmq.asyncio

from pyzmq.core.commons import log_lvl, log_str
from pyzmq.core.logger import get_logger

logger = get_logger(log_lvl, log_str, __name__)


def start():
    try:
        context = zmq.asyncio.Context.instance()
        sender = context.socket(zmq.PUSH)
        sender.bind("tcp://*:5557")

        sink = context.socket(zmq.PUSH)
        sink.connect("tcp://localhost:5558")
        logger.info("Starting server, press Ctrl+C to stop")
        logger.info("Listening on port 5555")
        while True:
            logger.debug("Press Enter when the workers are ready: ")
            _ = input()

            logger.debug("Sending tasks to workers...")
            sink.send_json({"result": {"status": "ok", "message": "start"}})

            for task_nbr in range(10):
                logger.debug(f"work {task_nbr}...")
                sender.send_json({"task": task_nbr, "data": random.randint(1, 50)})
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
