from bookshelf_app.helper.logger import get_app_logger


def test_get_app_logger_does_not_add_duplicate_handlers():
    logger = get_app_logger("tests.logger.duplicate")
    initial_handler_count = len(logger.handlers)

    same_logger = get_app_logger("tests.logger.duplicate")

    assert same_logger is logger
    assert len(same_logger.handlers) == initial_handler_count
    assert not logger.propagate
