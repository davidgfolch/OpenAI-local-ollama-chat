from ast import Dict
from util.logUtil import initLog

log = initLog(__file__)


def listMapper(msg: Dict):
    key = 'a' if 'q' not in msg else 'q'
    value = msg.get(key, '')
    log.info(f"mapping key/value => {key}/{value}")
    return {key: value}
