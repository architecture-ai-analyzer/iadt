#!/usr/bin/env python3
"""Worker: consome fila de entrada (SQS), processa diagrama via S3, publica JSON na fila de saída."""

import sys

from adapters.aws.sqs_worker import run_forever
from config.logging_config import get_logger

logger = get_logger(__name__)


def main() -> None:
    try:
        run_forever()
    except KeyboardInterrupt:
        logger.info("worker_stopped", extra={"extra": {"reason": "KeyboardInterrupt"}})
        sys.exit(0)
    except Exception as exc:
        logger.exception("worker_fatal", extra={"extra": {"error": str(exc)}})
        sys.exit(1)


if __name__ == "__main__":
    main()
