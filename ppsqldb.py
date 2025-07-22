# -*- coding: utf-8 -*-

import sys
import warnings

sys.dont_write_bytecode = True
warnings.filterwarnings('ignore')

import psycopg
from psycopg import Connection, Cursor
from psycopg.rows import dict_row

from typing import Self
from typing import Optional
from typing import Literal
from typing import Union
from typing import Any
from typing import Callable

RecordType = dict[str, Union[str, int, float, bool, None]]
TableType = list[RecordType]

class Db:
    _con: Optional[Connection]
    _cur: Optional[Cursor]
    _log: Optional[Callable[[str], None]]

    def __init__(self: Self, ip: str, port: int, dbname: str, user: str, password: str, logfunc: Optional[Callable[[str], None]] = None) -> None:
        # DBリソース初期化
        self._con = None
        self._cur = None

        # DB接続情報設定
        self._ip: str = ip
        self._pt: int = port
        self._nm: str = dbname
        self._us: str = user
        self._pw: str = password

        # ログ出力設定
        self._log = logfunc

        # エラー情報初期化
        self.last_error: str = ""


    def connect(self: Self) -> bool:
        result: bool = False

        try:
            self._con = psycopg.connect(
                host=self._ip, port=self._pt,
                dbname=self._nm,
                user=self._us, password=self._pw
            )
            self._log_output("connected")

            self._con.row_factory = dict_row # type: ignore
            self._cur = self._con.cursor()
            self._log_output("get cursor")

            result = True

        except Exception as e:
            self.last_error = str(e)
            self._log_output("exception: " + self.last_error)

            if self._cur is not None:
                self._cur.close()
                self._cur = None
                self._log_output("close cursor")

            if self._con is not None:
                self._con.close()
                self._con = None
                self._log_output("close connection")

        self._log_output("connected")
        return result

    def disconnect(self: Self) -> None:

        if self._cur is not None:
            self._cur.close()
            self._cur = None
            self._log_output("close cursor")

        if self._con is not None:
            self._con.close()
            self._con = None
            self._log_output("close connection")

        self._log_output("disconnected")
        return

    def fetchall(self: Self, sql: str) -> Union[Literal[False], TableType]:

        if self._cur is None:
            self._log_output("cursor is not opened")
            return False

        result: Union[Literal[False], TableType] = False

        try:
            self._cur.execute(sql) # type: ignore
            rows: list[dict[str, Any]] = self._cur.fetchall() # type: ignore
            result = []
            for row in rows:
                add_record: RecordType = {}
                for col_name in row.keys():
                    col_value: Union[str, int, float, bool, None] = row[col_name]
                    add_record[col_name] = col_value
                result.append(add_record)

        except Exception as e:
            self.last_error = str(e)
            self._log_output("exception: " + self.last_error)

        self._log_output("fetched " + str(result) if result == False else ("count=" + str(len(result))))
        return result

    def executesql(self: Self, sql: str) -> bool:

        if self._cur is None:
            self._log_output("cursor is not opened")
            return False

        result: bool = False
        try:
            self._cur.execute(sql) # type: ignore
            result = True

        except Exception as e:
            self.last_error = str(e)
            self._log_output("exception: " + self.last_error)

        self._log_output("executed " + str(result))
        return result


    def commit(self: Self) -> bool:

        if self._con is None:
            self._log_output("cursor is not opened")
            return False

        result: bool = False

        try:
            self._con.commit()
            result = True

        except Exception as e:
            self.last_error = str(e)
            self._log_output("exception: " + self.last_error)

        self._log_output("commited")
        return result


    def rollback(self: Self) -> bool:

        if self._con is None:
            self._log_output("cursor is not opened")
            return False

        result: bool = False

        try:
            self._con.rollback()
            result = True

        except Exception as e:
            self.last_error = str(e)
            self._log_output("exception: " + self.last_error)

        self._log_output("rollbacked")
        return result


    def _log_output(self: Self, msg: str) -> None:
        if self._log is None:
            return
        self._log(msg)
        return
