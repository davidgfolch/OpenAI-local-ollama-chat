from ast import Dict
import logging
from util.logUtil import initLog

log = initLog(__file__, logging.INFO)


def listMapper(msg: Dict):
    key = 'a' if 'q' not in msg else 'q'
    value = msg.get(key, '')
    log.debug(f"mapping key/value => {key}/{value}")
    return {key: value}
