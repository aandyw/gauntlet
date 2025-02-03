import logging


class DiscordMessageError(ValueError):
    """ValueError we raise when we want to send a message to the user."""

    def __init__(self, message: str):
        super().__init__(message)


# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # filename="bot.log",
    # filemode="w",
)

# Create a logger
logger = logging.getLogger(__name__)
