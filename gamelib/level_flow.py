# -*- coding: utf-8 -*-
import logging

from gamelib.level_intro import ContextIntro
from gamelib.level_outro import ContextOutro
from gamelib.level_1 import ContextLevel1

logger = logging.getLogger(__name__)
logger.debug("importing...")

level_sequence = [
    ContextIntro,
    ContextLevel1,
    ContextOutro,
]


_level_iterator = iter(level_sequence)


def next_level():
    return next(_level_iterator)


logger.debug("imported")
