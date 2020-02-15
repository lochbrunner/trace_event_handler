#!/usr/bin/env python3

import logging
from trace_event_handler import TraceEventHandler


def bar():
    global logger
    logger.warning('bar')


def foo():
    global logger
    logger.warning('foo')
    bar()


if __name__ == '__main__':
    handler = TraceEventHandler()
    logging.basicConfig(
        handlers=[
            logging.StreamHandler(None),
            handler
        ],
        level=logging.INFO
    )

    global logger
    logger = logging.getLogger(__file__)

    logger.warning('root 1')

    foo()
    foo()

    logger.warning('root 2')
    logger.warning('root 3')

    handler.dump()
