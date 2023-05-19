import asyncio
from concurrent.futures import ProcessPoolExecutor
import logging
import logging.config

import uvicorn
import uvloop

from src.db.base_manager import run_migrations
# from internal_common.logging.logging import get_uvicorn_log_file, loguru_json_serializer
# from internal_common.rabbitmq import ConnectionPool as AmqpConnectionPool, Consumer
# from internal_common.cron.scheduler import Scheduler, Task
from loguru import logger
from src.db.main_db_manager import MainDbManager
# from supply.ingestors.generator.balnamoon import retrieve_balnamoon_generation

import settings
# from supply.external_clients import MainExternalClient
from src.server.server import make_server_app


async def main(loop: asyncio.AbstractEventLoop) -> None:
    # if not settings.LOCAL_RUN:
    #     logging.config.fileConfig(get_uvicorn_log_file())
    #     logger.remove()
    #     logger.add(loguru_json_serializer, level=settings.LOG_LEVEL, serialize=True)

    run_migrations()

    main_db_manager = MainDbManager(db_name_prefix=settings.DB_NAME_PREFIX)

    # amqp_connection_pool = AmqpConnectionPool(
    #     login=settings.RABBIT_LOGIN,
    #     password=settings.RABBIT_PASSWORD,
    #     host=settings.RABBIT_HOST,
    #     port=settings.RABBIT_PORT,
    #     ssl=settings.RABBIT_SSL,
    #     no_verify_ssl=True if settings.LOCAL_RUN else False,
    #     prefetch_count=settings.RABBIT_PREFETCH_COUNT,
    # )
    #
    # amqp_server = AMQPServer(
    #     main_db_manager=main_db_manager,
    # )
    #
    # consumer = Consumer(
    #     connection_pool=amqp_connection_pool,
    #     subscriptions=amqp_server.subscriptions,
    # )

    # executor = ProcessPoolExecutor(
    #     max_workers=1,
    # )

    # scheduler = Scheduler(
    #     [
    #         Task(
    #             settings.BALNAMOON_DATA_RETRIEVAL_CRON,
    #             retrieve_balnamoon_generation,
    #             [loop, executor, main_db_manager],
    #         )
    #     ]
    # )

    server_app = make_server_app(
        main_db_manager=main_db_manager,
        # authorization=not settings.LOCAL_RUN,
        # startup_events=[consumer.start, scheduler.start],
        shutdown_events=[
            # amqp_connection_pool.close,
            main_db_manager.close,
            # main_external_client.close,
            # scheduler.stop,
            # executor.shutdown,
        ],
    )

    # if not settings.LOCAL_RUN:
    #     config = uvicorn.Config(
    #         server_app,
    #         host="0.0.0.0",
    #         port=settings.APP_PORT,
    #         log_config=get_uvicorn_log_file(),
    #         use_colors=False,
    #     )
    # else:
    #     config = uvicorn.Config(server_app, host="0.0.0.0", port=settings.APP_PORT)

    config = uvicorn.Config(server_app, host="0.0.0.0", port=settings.APP_PORT)

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        app = loop.run_until_complete(main(loop))
    finally:
        loop.close()
