import logging

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # filename="bot.log",
    # filemode="w",
)

# Create a logger
logger = logging.getLogger(__name__)
