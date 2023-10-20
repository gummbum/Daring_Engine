# -*- coding: utf-8 -*-
import logging

import pygame

from gamelib.settings import Runtime

logger = logging.getLogger(__name__)
logger.debug("importing...")


class Timer:

    def __init__(self):
        self._timers = []

    def add(self, timed_item):
        self._timers.append(timed_item)

    def get_timers(self):
        return list(self._timers)

    def update(self):
        timers = []
        for t in self._timers:
            t.tick()
            timers.append(t)
        return timers

    def clear(self):
        del self._timers[:]
        return self.get_timers()

    def remove(self, timer):
        try:
            self._timers.remove(timer)
        except ValueError:
            pass
        return self.get_timers()


class TimedItem:

    def __init__(self, interval, callback, args=None, kwargs=None):
        """create a timer that fires a callback every interval

        Args:
            interval: recurring interval to fire callback
            callback: callable, must accept dt as its first argument
            args: sequence, passed to callback as *args
            kwargs: map, passed to callback as **kwargs
        """
        self.callback = callback
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}

        self.interval = interval                    # milliseconds
        self._start = pygame.time.get_ticks()       # milliseconds
        self._mark = self._start                    # milliseconds
        self.dt = 0                                 # milliseconds

    def tick(self):
        dt = pygame.time.get_ticks() - self._mark
        if dt >= self.interval:
            self._mark = pygame.time.get_ticks()
            self.dt = dt
            self.callback(dt, *self.args, **self.kwargs)


logger.debug("imported")
