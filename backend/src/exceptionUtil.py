def getExceptionStackMessages(ex, msgs=[]):
    msgs.append(type(ex).__name__+": "+str(ex))
    if (ex.__cause__):
        getExceptionStackMessages(ex.__cause__, msgs)
    return msgs
