"""A python wrapper for Quotex API."""
import logging
from .stable_api import Quotex
from .strategies import TradingStrategies
from .bot_engine import QuotexBot

__all__ = ["Quotex", "TradingStrategies", "QuotexBot"]


def _prepare_logging():
    """Prepare logger for module Quotex API."""
    logger = logging.getLogger(__name__)
    # logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.NullHandler())

    websocket_logger = logging.getLogger("websocket")
    websocket_logger.setLevel(logging.DEBUG)
    websocket_logger.addHandler(logging.NullHandler())


_prepare_logging()
