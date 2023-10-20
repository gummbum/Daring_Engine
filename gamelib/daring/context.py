# -*- coding: utf-8 -*-
import logging

from gamelib.daring import run_stack

logger = logging.getLogger(__name__)
logger.debug("importing...")


class Context:

    def __init__(self, *args, **kwargs):
        pass

    def push(self, new_context):
        run_stack.push(new_context)

    def pop(self):
        run_stack.pop()

    def on_win(self):
        self.pop()

    def on_lose(self):
        self.pop()

    def update(self, dt):
        pass

    def draw(self):
        pass


logger.debug("imported")
