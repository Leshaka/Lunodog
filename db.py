from typing import Iterable, Literal
from logging import getLogger
import aiomysql

from config import MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASS

logger = getLogger('mysql')


class Database:
    pool: aiomysql.Pool

    async def connect(self, loop):
        self.pool = await aiomysql.create_pool(
            maxsize=3,
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            db=MYSQL_DB,
            autocommit=True,
            cursorclass=aiomysql.DictCursor,
            loop=loop
        )

    async def close(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def execute(self, query, args=None) -> int:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                logger.debug(f'{query} -- {args}')
                await cur.execute(query, args)
                return cur.lastrowid

    async def executemany(self, query, args=None) -> int:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                logger.debug(f'{query} -- (...)')
                return await cur.executemany(query, args)

    async def fetch_one(self, query, args=None) -> dict | None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                logger.debug(f'{query} -- {args}')
                await cur.execute(query, args)
                return await cur.fetchone()

    async def fetch_all(self, query, args=None) -> list[dict]:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                logger.debug(f'{query} -- {args}')
                await cur.execute(query, args)
                return await cur.fetchall()

    @staticmethod
    def _insert(table: str, keys: Iterable[str], on_conflict: str | None) -> str:
        return {'ignore': 'INSERT IGNORE', 'replace': 'REPLACE', None: 'INSERT'}[on_conflict] + \
               ' INTO `{}` ({}) VALUES ({})'.format(
                   table,
                   ', '.join([f'`{i}`' for i in keys]),
                   ', '.join([f'%s' for _ in keys])
               )

    async def insert(self, table: str, row: dict, on_conflict: Literal['ignore', 'replace'] = None) -> int:
        return await self.execute(query=self._insert(table, tuple(row.keys()), on_conflict), args=tuple(row.values()))

    async def insert_many(
            self, table: str, keys: Iterable[str], values: Iterable, on_conflict: Literal['ignore', 'replace'] = None
    ) -> int | None:
        return await self.executemany(query=self._insert(table, keys, on_conflict), args=values)

    @staticmethod
    def _select(table: str, keys: Iterable[str]) -> str:
        return 'SELECT * FROM `{}` WHERE {}'.format(
            table,
            ' AND '.join(f'`{i}`=%s' for i in keys)
        )

    async def select(self, table: str, q: dict) -> list[dict]:
        return await self.fetch_all(query=self._select(table, tuple(q.keys())), args=tuple(q.values()))

    async def select_one(self, table: str, q: dict) -> dict | None:
        return await self.fetch_one(query=self._select(table, tuple(q.keys())), args=tuple(q.values()))

    @staticmethod
    def _update(table: str, keys: Iterable[str], where_keys: Iterable[str]) -> str:
        return 'UPDATE `{}` SET {} WHERE {}'.format(
            table,
            ', '.join(f'`{i}`=%s' for i in keys),
            ' AND '.join(f'`{i}`=%s' for i in where_keys)
        )

    async def update(self, table: str, data: dict, where: dict) -> int:
        return await self.execute(
            query=self._update(table, tuple(data.keys()), tuple(where.keys())),
            args=(*data.values(), *where.values())
        )

    @staticmethod
    def _on_dup_update(keys: Iterable[str]):
        return ' ON DUPLICATE KEY UPDATE {}'.format(
            ', '.join(f'`{key}`=VALUES(`{key}`)' for key in keys)
        )

    async def insert_update(self, table: str, data: dict, update_keys: list[str]) -> int:
        """ Insert, on duplicate keys update"""
        return await self.execute(
            query=self._insert(table, data.keys(), on_conflict=None) + self._on_dup_update(keys=update_keys),
            args=data.values()
        )

    async def insert_update_many(self, table: str, base_keys: list[str], update_keys: list[str], values: Iterable):
        q = self._insert(table, base_keys+update_keys, on_conflict=None) + self._on_dup_update(keys=update_keys)
        logger.warning(q)
        return await self.executemany(
            query=q,
            args=values
        )

    @staticmethod
    def _delete(table: str, keys: Iterable[str]):
        return 'DELETE FROM `{}` WHERE {}'.format(
            table,
            ' AND '.join(f'`{i}`=%s' for i in keys)
        )

    async def delete(self, table: str, q: dict) -> int:
        return await self.execute(query=self._delete(table, tuple(q.keys())), args=tuple(q.values()))


db = Database()
