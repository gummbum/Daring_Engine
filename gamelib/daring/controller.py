# -*- coding: utf-8 -*-
import logging

from gamelib.settings import Runtime, TimeSettings
from gamelib.daring import run_stack
from gamelib.daring.context import Context
from gamelib.daring.timer import Timer, TimedItem

logger = logging.getLogger(__name__)
logger.debug("importing...")


def run(starting_context):
    run_stack.push(starting_context)
    top_context: Context = starting_context

    def update_callback(dt):
        top_context.update(dt)

    def draw_callback(dt):
        top_context.draw()

    timer = Timer()
    # todo: ups and fps timings are decoupled; need to implement interpolated rendering
    update_pulse = TimedItem(TimeSettings.ups, update_callback)
    draw_pulse = TimedItem(TimeSettings.fps, draw_callback)
    timer.add(update_pulse)
    timer.add(draw_pulse)

    # run as long as there is something on the run stack
    running = True
    while running:
        top_context = run_stack.top()
        if top_context:
            if TimeSettings.clock_nice:
                Runtime.dt = Runtime.clock.tick(TimeSettings.ups)
            else:
                Runtime.dt = Runtime.clock.tick_busy_loop(TimeSettings.ups)
            timer.update()
        else:
            running = False


logger.debug("imported")
