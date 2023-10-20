# -*- coding: utf-8 -*-
import logging


class LogSettings:
    log_level = logging.DEBUG


logging.basicConfig(encoding='utf-8', level=LogSettings.log_level)

logger = logging.getLogger(__name__)
logger.debug("importing...")


class GameSettings:
    game_name = 'Win All the Things'


class Runtime:
    clock = None            # global clock
    dt = 0                  # time used in the previous tick
    timer = None            # persistent global timers; don't use this for levels, instead make a local timer


class TimeSettings:
    # todo: these timings are decoupled; need to implement interpolated rendering
    ups = 30        # updates per second; i.e. the game's time step
    fps = 30        # frames per second; i.e. the game's render step
    clock_nice = True       # when clock_throttle > 0, nice=True uses Clock.tick(), else Clock.tick_busy_loop()


class DisplaySettings:
    width = 800
    height = 600
    flags = 0
    depth = 0
    display = 0
    vsync = 0


class AudioSettings:
    frequency = 44100
    size = 1024
    channels = -16
    buffer = 1024
    device_name = 'default'


logger.debug("imported")
