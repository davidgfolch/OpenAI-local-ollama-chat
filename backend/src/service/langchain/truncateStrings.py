import collections
import logging
from typing import Any
from langchain_core.messages import BaseMessage

from util.logUtil import initLog

log = initLog(__file__, logging.ERROR)


def truncateString(str: str, max: int, suffix: str, deepStr: str) -> str:
    mx = max - len(suffix)
    if len(str) > mx:
        truncated = str[:mx + len(suffix)] + suffix
        return truncated
    return str


def truncateStrings(o: Any, max: int = 40) -> str:
    return truncateStringsInternal(o, max)


def truncateStringsInternal(o: Any, max: int, suffix: str = "[...]", deep: int = 0) -> str:
    if not o or isinstance(o, int) or isinstance(o, float) or isinstance(o, bool):
        return o
    deepStr = ("   "*deep)
    if isinstance(o, dict):
        log.info(f"obj type = {type(o)} -> isinstance of dict")
        for key_ in o.keys():
            if key_:
                o[key_] = truncateStringsInternal(o[key_], max, suffix, deep+1)
    elif isinstance(o, str):
        log.info(f"obj type = {type(o)} -> isinstance of str")
        o = truncateString(o, max, suffix, deepStr)
    elif isinstance(o, BaseMessage):
        log.info(f"obj type = {type(o)} -> isinstance of BaseMessage")
        o.content = truncateStringsInternal(o.content, max, suffix, deep+1)
    elif isinstance(o, tuple):
        log.info(f"obj type = {type(o)} -> isinstance of tuple")
        t: tuple = o
        o = (t[0], truncateStringsInternal(t[1], max, suffix, deep+1))
    elif isinstance(o, collections.abc.Iterable):
        log.info(f"obj type = {type(o)} -> isinstance of Iterable")
        for idx, item in enumerate(o):
            o[idx] = truncateStringsInternal(item, max, suffix, deep+1)
    else:
        log.error(f"obj type = {type(o)} NOT IMPLEMENTED!!!!!!!!!!!!!!!!!!1")
    return o
