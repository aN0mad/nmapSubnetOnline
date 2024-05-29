import sys
import loguru


def initLogger(
    DEBUG: bool, QUIET: bool, DAEMON: bool, UI: bool, FILELOGGER: str, logger
):
    logger.remove(0)
    level_fileWrite = logger.level("fileWrite", no=31, color="<blue>")
    level_modification = logger.level("modification", no=31, color="<yellow>")
    COLOR = True
    if UI:
        COLOR = False

    # Enable daemon logging
    if DAEMON:
        # Don't log to stdout and just use a file if provided
        if FILELOGGER != "":
            logger.add(
                FILELOGGER,
                colorize=COLOR,
                format="{time} | <level>{level}</level> | {message}",
                level="DEBUG",
            )
        return

    if QUIET:
        logger.add(
            sys.stdout,
            colorize=COLOR,
            format="{time} | <level>{level}</level> | {message}",
            level=100,
        )
        return

    if DEBUG:
        logger.add(
            sys.stdout,
            colorize=COLOR,
            format="{time} | <level>{level}</level> | {message}",
            level="DEBUG",
        )
        if FILELOGGER != "":
            logger.add(
                FILELOGGER,
                colorize=COLOR,
                format="{time} | <level>{level}</level> | {message}",
                level="DEBUG",
            )
    else:
        logger.add(
            sys.stdout,
            colorize=COLOR,
            format="{time} | <level>{level}</level> | {message}",
            level="INFO",
        )
        if FILELOGGER != "":
            logger.add(
                FILELOGGER,
                colorize=COLOR,
                format="{time} | <level>{level}</level> | {message}",
                level="INFO",
            )
