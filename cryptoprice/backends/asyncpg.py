import subprocess
import typing
import contextlib
import asyncpg
from asyncpg import Connection
from apistar import Command, Component, Settings
import logging


class AsyncPgBackend(object):
    """AsyncPg Backend"""
    async def __init__(self, settings: Settings) -> None:
        #  self._conn = await asyncpg.connect()

        self._config = settings.get('DATABASE')
        self._url = self._config.get('URL')
        if self._url:
            self._pool = await asyncpg.create_pool(self._url)

        kwargs = {}
        for k in ('HOST', 'DATABASE', 'USER', 'PORT', 'PASSWORD', 'TIMEOUT', 'SSL'):
            if k in self._config:
                kwargs[k] = self._config[k]

        self._pool = await asyncpg.create_pool(**kwargs)

    #  @property
    #  def conn(self):
    #      return self._conn
    @property
    def pool(self):
        return self._pool


@contextlib.contextmanager
async def get_conn(backend: AsyncPgBackend) -> typing.Generator[Connection, None, None]:
    """
    XXX
    """
    pool = backend.pool
    conn = await pool.aquire()

    try:
        yield conn
        #  session.commit()
    except Exception:
        #  session.rollback()
        raise
    finally:
        pool.release(conn)


def pg_cli(conn: Connection):
    settings = conn.get_settings()
    print('pgcli settings: %s', settings)

    #  subprocess.call(
    #      ['psql'] + host + password + port + db
    #  )



components = [
    Component(AsyncPgBackend, init=AsyncPgBackend),
    Component(Connection, init=get_conn, preload=False),
]

commands = [
    Command('dbshell', pg_cli),
]
