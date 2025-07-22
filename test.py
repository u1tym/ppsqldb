# -*- coding: utf-8 -*-

import sys
import warnings

sys.dont_write_bytecode = True
warnings.filterwarnings('ignore')

from psqldb import Db

def main() -> None:
    test1()
    return


def test1() -> None:
    db = Db("127.0.0.1", 5432, "testdb", "testuser", "xxxx", print)
    res = db.connect()
    if res == False:
        return

    db.disconnect()


if __name__ == '__main__':
    main()
