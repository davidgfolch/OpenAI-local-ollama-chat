from util.logUtil import initLog
import logging

log = initLog(__file__, logging.INFO)

def getExceptionStackMessages(ex):
    return __getExceptionStackMessages(ex, [])


def __getExceptionStackMessages(ex, msgs):
    log.info(f'getExceptionStackMessages -> {type(ex).__name__+": "+str(ex)}')
    msgs.append(type(ex).__name__+": "+str(ex))
    if (ex.__cause__):
        log.info(f'getExceptionStackMessages __cause -> {ex.__cause__}')
        msgs = __getExceptionStackMessages(ex.__cause__, msgs)
    return msgs
