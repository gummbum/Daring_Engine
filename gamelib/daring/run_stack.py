# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)
logger.debug("importing...")

_run_stack = []


def top():
    if _run_stack:
        return _run_stack[-1]


def push(context):
    _run_stack.append(context)


def pop():
    _run_stack.pop(-1)


def clear():
    del _run_stack[:]



logger.debug("imported")
