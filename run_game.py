# -*- coding: utf-8 -*-
import logging

from gamelib import settings, main

logger = logging.getLogger(__name__)
logger.debug(f"launching {settings.GameSettings.game_name}")

if __name__ == '__main__':
    main.main()

logger.debug("exiting game")
