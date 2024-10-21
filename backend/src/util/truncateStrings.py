import collections
import collections.abc
import copy
import logging
from typing import Any, Dict

from util.logUtil import initLog

log = initLog(__file__, logging.INFO)

__objAttributesMap: Dict[object, str] = {}


def setTruncateAttrMap(objAttributesMap: dict):
    global __objAttributesMap
    __objAttributesMap = objAttributesMap
    log.info(f"setTruncateAttrMap objAttributesMap={__objAttributesMap}")


def truncateStrings(o: Any, max: int = 40) -> str:
    """ Truncates any object strings recursively supporting dict, tuple, iterable out-of-the-box.

    To parse special objects pass specific map with object properties you want to truncate, f.ex.:
    ```
    setTruncateAttrMap({
        BaseMessage: ["content"],  # parses only content attribute (str) from BaseMessage
        ChatPromptValue: ["messages"]  # parses only messages attribute (list) from ChatPrompValue
    })
    ```
    """
    return __truncateStrings(copy.deepcopy(o), max)


def __truncateStrings(o: Any, max: int, suffix: str = "[...]", deep: int = 0) -> str:
    if not o or isinstance(o, int) or isinstance(o, float) or isinstance(o, bool):
        return o
    try:
        for classType in __objAttributesMap:
            if isinstance(o, classType):
                return __truncateClass(o, classType, max, suffix, deep+1)
        if isinstance(o, dict):
            return __truncateDict(o, max, suffix, deep+1)
        if isinstance(o, str):
            log.debug(f"obj type = {type(o)} -> isinstance of str")
            return truncateString(o, max, suffix, deep+1)
        if isinstance(o, tuple):
            log.debug(f"obj type = {type(o)} -> isinstance of tuple")
            return (o[0], __truncateStrings(o[1], max, suffix, deep+1))
        if isinstance(o, collections.abc.Iterable):
            return __truncateIterable(o, max, suffix, deep+1)
        log.error(f"obj type = {type(o)} NOT IMPLEMENTED!!!!!!!!!!!!!!!!!!")
    except Exception as e:
        log.error(f"failed to truncate strings for object type {type(o)}", e)
    return o


def __truncateClass(o: Any, classType: object, max: int, suffix: str, deep: int):
    attributes = __objAttributesMap.get(classType)
    if attributes:
        for attr in attributes:
            res = __truncateStrings(getattr(o, attr), max, suffix, deep+1)
            setattr(o, attr, res)
    return o


def __truncateIterable(o: collections.abc.Iterable, max: int, suffix: str, deep: int):
    log.debug(f"obj type = {type(o)} -> isinstance of Iterable")
    for idx, item in enumerate(o):
        o[idx] = __truncateStrings(item, max, suffix, deep+1)
    return o


def __truncateDict(o: Dict, max: int, suffix: str, deep: int):
    log.debug(f"obj type = {type(o)} -> isinstance of dict")
    for key_ in o.keys():
        if key_:
            o[key_] = __truncateStrings(o[key_], max, suffix, deep+1)
    return o


def truncateString(str: str, max: int, suffix: str, deep: int) -> str:
    mx = max - len(suffix)
    if len(str) > mx:
        truncated = str[:mx + len(suffix)] + suffix
        log.debug(("   "*deep)+f"truncating string to: {truncated}")
        return truncated
    return str
