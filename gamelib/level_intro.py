# -*- coding: utf-8 -*-
import logging

import pygame

from gamelib.settings import Runtime, DisplaySettings
from gamelib.daring.context import Context

logger = logging.getLogger(__name__)
logger.debug("importing...")


class ContextIntro(Context):

    def __init__(self, *args, **kwargs):
        Context.__init__(self, *args, **kwargs)

        # add game stuff here
        font = pygame.font.SysFont('sans', 40)
        self.image = font.render('WELCOME', True, 'orange')
        self.rect = self.image.get_rect(center=(DisplaySettings.width // 2, DisplaySettings.height // 2))

    def update(self, dt):
        pygame.display.set_caption(f'Context: Intro (press any key) | {int(round(Runtime.clock.get_fps()))} fps')
        self.handle_events()

    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        screen.blit(self.image, self.rect)
        pygame.display.flip()

    def handle_events(self):
        for e in pygame.event.get():
            if e.type in (pygame.QUIT, pygame.KEYDOWN):
                self.on_win()


logger.debug("imported")
