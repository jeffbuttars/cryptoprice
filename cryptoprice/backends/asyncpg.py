import os
import subprocess
import typing
import asyncio
from aiocontext import async_contextmanager as contextmanager
import asyncpg
from asyncpg import Connection
from apistar import Command, Component, Settings
import logging

logger = logging.getLogger(__name__)


class AsyncPgBackend(object):
    """AsyncPg Backend"""
    CLI_CONFIG_MAP = {
        'HOST': '--host',
        'PORT': '--port',
        'USER': '--username',
        'NAME': '--dbname',
        'DATABASE': '--dbname',
    }

    def __init__(self, settings: Settings) -> None:
        self._config = settings.get('DATABASE')
        self._url = self._config.get('URL')
        self._pool = None

    async def _connect(self):
        logger.debug("Creating Postgresql connection")

        try:
            if self._url:
                logger.debug("Creating Postgresql connection from URL")
                self._pool = await asyncpg.create_pool(self._url)
            else:
                logger.debug("Creating Postgresql connection from credentials")
                kwargs = {}
                if 'DATBASE' not in self._config:
                    kwargs['database'] = self._config.pop('NAME', '')

                for k in ('HOST', 'DATABASE', 'USER', 'PORT', 'PASSWORD', 'TIMEOUT', 'SSL'):
                    if k in self._config:
                        kwargs[k.lower()] = self._config[k]

                self._pool = await asyncpg.create_pool(**kwargs)

            # 'PING' the DB
            ping = await self.fetch("SELECT $1", 'PONG')
            logger.debug("ping: %s", ping[0][0])
        except Exception as e:
            logger.error("connection error: %s", e)
            raise

        return self._pool

    @property
    async def pool(self):
        if self._pool:
            return self._pool

        return await self._connect()

    async def fetch(self, *args, **kwargs):
        pool = await self.pool

        async with pool.acquire() as conn:
            try:
                return await conn.fetch(*args, **kwargs)
            except Exception as e:
                logger.error("AsyncPgBackend fetch error: %s", e)
                raise

    async def exec(self, *args, **kwargs):
        pool = await self.pool

        async with pool.acquire() as conn:
            try:
                return await conn.execute(*args, **kwargs)
            except Exception as e:
                logger.error("AsyncPgBackend exec error: %s", e)
                raise

    @property
    def url(self):
        return self._url

    @property
    def config(self):
        return self._config.copy()


@contextmanager
async def get_conn(backend: AsyncPgBackend) -> typing.Generator[Connection, None, None]:
    """
    Get a database connection in a context that will release itself when the context is left.
    """
    pool = await backend.pool
    conn = await pool.acquire()
    logger.debug("asyncpg get_conn pool: %s, conn: %s", pool, conn)

    try:
        yield conn
    except Exception as e:
        logger.error("AsyncPG Error: %s", e)
        raise
    finally:
        await pool.release(conn)


def pg_cli(backend: AsyncPgBackend):
    """
    Run the Postgresql shell with this projects DB settings
    """
    psql = ['psql']
    env = os.environ.copy()

    if backend.url:
        # Prefer the url
        psql.append(backend.url)
    else:
        # Build a command line from the config.
        # Put the password in the environment with PGPASS
        config = backend.config
        env['DBPASSWORD'] = config.get('PASSWORD', '')

        keys = set(config.keys()) & set(backend.CLI_CONFIG_MAP.keys())
        for k in keys:
            psql.append(backend.CLI_CONFIG_MAP[k])
            psql.append(config[k])

    subprocess.call(psql, env=env)


components = [
    Component(AsyncPgBackend, init=AsyncPgBackend),
    Component(Connection, init=get_conn, preload=False),
]


commands = [
    Command('dbshell', pg_cli),
]
