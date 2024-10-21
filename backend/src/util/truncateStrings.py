import collections
import collections.abc
import logging
from typing import Any, Dict

from util.logUtil import initLog

log = initLog(__file__, logging.DEBUG)


class TruncateStrings:
    def __init__(self, objAttributesMap: Dict[object, str], max: int = 30, suffix: str = "[...]"):
        self.objAttributesMap = objAttributesMap
        self.max = max
        self.suffix = suffix

    def process(self, o: Any) -> str:
        """ Truncates any object strings recursively supporting dict, tuple, iterable out-of-the-box.

        To parse special objects pass specific map with object properties you want to truncate, f.ex.:
        ```
        setTruncateAttrMap({
            BaseMessage: ["content"],  # parses only content attribute (str) from BaseMessage
            ChatPromptValue: ["messages"]  # parses only messages attribute (list) from ChatPromptValue
        })
        ```
        """
        return self.truncate(o, 0)

    def truncate(self, o: Any, deep: int = 0) -> str:
        if not o or isinstance(o, int) or isinstance(o, float) or isinstance(o, bool):
            return o
        try:
            for classType in self.objAttributesMap:
                if isinstance(o, classType):
                    return self.forClass(o, classType, deep+1)
            if isinstance(o, dict):
                return self.forDict(o, deep+1)
            if isinstance(o, str):
                log.debug(("   "*deep)+f"obj type = {type(o)} -> isinstance of str")
                return self.forString(o, deep+1)
            if isinstance(o, tuple):
                log.debug(("   "*deep)+f"obj type = {type(o)} -> isinstance of tuple")
                return (o[0], self.truncate(o[1], deep+1))
            if isinstance(o, collections.abc.Iterable):
                return self.forIterable(o, deep+1)
            log.error(("   "*deep)+f"obj type = {type(o)} NOT IMPLEMENTED!!!!!!!!!!!!!!!!!!")
        except Exception as e:
            log.error(("   "*deep)+f"failed to truncate strings for object type {type(o)}", e)
        return o

    def forClass(self, o: Any, classType: object, deep: int):
        attributes = self.objAttributesMap.get(classType)
        if attributes:
            for attr in attributes:
                res = self.truncate(
                    getattr(o, attr), deep+1)
                setattr(o, attr, res)
        return o

    def forIterable(self, o: collections.abc.Iterable, deep: int):
        log.debug(("   "*deep)+f"obj type = {type(o)} -> isinstance of Iterable")
        for idx, item in enumerate(o):
            o[idx] = self.truncate(item, deep+1)
        return o

    def forDict(self, o: Dict, deep: int):
        log.debug(("   "*deep)+f"obj type = {type(o)} -> isinstance of dict")
        for key_ in o.keys():
            if key_:
                o[key_] = self.truncate(o[key_], deep+1)
        return o

    def forString(self, str: str, deep: int) -> str:
        mx = self.max - len(self.suffix)
        if len(str) > mx:
            truncated = str[:mx + len(self.suffix)] + self.suffix
            log.debug(("   "*deep)+f"truncating string to: {truncated}")
            return truncated
        return str
