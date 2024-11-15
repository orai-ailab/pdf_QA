from loguru import logger

logger.add(
    "logs/chat_inference.log",
    filter=lambda record: record["extra"].get("logger_name") == "chat_inference",
    level="INFO",
)
logger.add(
    "logs/chroma.log",
    filter=lambda record: record["extra"].get("logger_name") == "chroma",
    level="INFO",
)
logger.add(
    "logs/encoder_inference.log",
    filter=lambda record: record["extra"].get("logger_name") == "encoder_inference",
    level="INFO",
)
logger.add(
    "logs/init_profile.log",
    filter=lambda record: record["extra"].get("logger_name") == "init_profile",
    level="INFO",
)
logger.add(
    "logs/offline_flow.log",
    filter=lambda record: record["extra"].get("logger_name") == "offline_flow",
    level="INFO",
)
logger.add(
    "logs/system.log",
    filter=lambda record: record["extra"].get("logger_name") == "system",
    level="INFO",
)

__all__ = ["logger"]