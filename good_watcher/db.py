import sqlite3
import subprocess
import sys
import time
import asyncio
from sqlite3 import Connection
from dataclasses import dataclass


@dataclass
class Guard:
    name: str
    url: str
    spider: str
    keyword: str
    first: bool

@dataclass
class Good:
    id: int
    guard: str
    url: str
    title: str
    price: float


def connection(path) -> Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class Guards():
    def __init__(self, conn: Connection):
        self.conn = conn
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS guards (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT UNIQUE NOT NULL,
                url       TEXT NOT NULL,
                spider    TEXT NOT NULL,
                keyword   TEXT,
                active    BOOL NOT NULL,
                first     BOOL NOT NULL
            )
        """)


    def add_shop(self, record: Guard):

        res = self.conn.execute("SELECT name, url, spider, keyword FROM guards WHERE name = ?", (record.name,)).fetchone()
        if res is None:
            self.conn.execute("INSERT INTO guards (name, url, spider, keyword, active, first) VALUES (?, ?, ?, ?, 1, 1)", (record.name, record.url, record.spider, record.keyword,))
        
        else:
            self.conn.execute("UPDATE guards SET active = 1 WHERE name = ?", (record.name,))
        self.conn.commit()

    def deactivateAll(self):
        self.conn.execute("UPDATE guards SET active = 0")
        self.conn.commit()

    def active(self):
        res = self.conn.execute("SELECT name, url, spider, keyword, first FROM guards WHERE active = 1")
        return [Guard(**dict(r)) for r in res]

    def firstRun(self):
        self.conn.execute("UPDATE guards SET first = 0")
        self.conn.commit()

class Goods():
    def __init__(self, conn):
        self.conn = conn
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS goods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guard      TEXT NOT NULL,
                url       TEXT NOT NULL,
                title     TEXT NOT NULL,
                price     REAL NOT NULL,
                FOREIGN KEY (guard) REFERENCES guards(name) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def upsert(self, record: dict) -> int | None:
        exist = self.conn.execute(
            "SELECT id, guard, url, price FROM goods WHERE url = ?", (record['url'],)
        ).fetchone()
        with self.conn:
            if exist is None:
                self.conn.execute("INSERT INTO goods (guard, url, title, price) VALUES (?, ?, ?, ?)", (record['guard'], record['url'], record['title'], record['price']))
                return -1 # Return Code for new product
            
            if exist['price'] != record['price']:
                self.conn.execute(
                    "UPDATE goods SET price = ? WHERE id = ?",
                    (record["price"], exist['id']),
                )
                return exist['price']
        return None # Return code for already saved product