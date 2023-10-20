# -*- coding: utf-8 -*-
import logging

import pygame

from gamelib import level_flow
from gamelib.settings import Runtime, DisplaySettings, AudioSettings
from gamelib.daring import controller, timer, context

logger = logging.getLogger(__name__)
logger.debug("importing...")


def main():
    logger.debug('pygame init')
    pygame.init()
    pygame.mixer.pre_init(AudioSettings.frequency, AudioSettings.size, AudioSettings.channels,
                          AudioSettings.buffer, AudioSettings.device_name)
    pygame.display.set_mode((DisplaySettings.width, DisplaySettings.height), DisplaySettings.flags,
                            DisplaySettings.depth, DisplaySettings.display, DisplaySettings.vsync)

    Runtime.clock = pygame.Clock()

    logger.debug('starting game loop')
    try:
        new_context = level_flow.next_level()
        while new_context:
            logger.debug(f'running new context: {new_context}')
            controller.run(new_context())
            try:
                new_context = None
                new_context = level_flow.next_level()
            except StopIteration:
                pass
    except StopIteration:
        return
    logger.debug('exited game loop')


logger.debug("imported")
