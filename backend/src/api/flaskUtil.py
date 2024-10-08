from flask import Response, make_response, Request
from util.exceptionUtil import getExceptionStackMessages
from util.logUtil import initLog
import logging

log = initLog(__file__, logging.DEBUG)

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'DELETE,GET,POST,OPTIONS,STREAM',
    'Access-Control-Allow-Headers': 'Content-Type'
}

EVENT_STREAM_CHUNKED_HEADERS = {
    'Accept': 'text/event-stream',
    'Content-Type': "text/event-stream",
    'Transfer-Encoding': "chunked",  # tried, no help
    # 'Cache-Control': "no-cache",
    # 'Connection': "keep-alive",
}
EVENT_STREAM_CHUNKED_HEADERS.update(CORS_HEADERS)


def corsHeaders(res: Response = Response()):
    res.headers.update(CORS_HEADERS)
    return res


# see https://pypi.org/project/Flask-Parameter-Validation/
def getReqParams(request: Request, params: list, paramsOptional: list = []):
    paramValues: list = list(map(lambda p: (p, request.json.get(p)), params))
    values = (", ".join([str(a)+'='+str(b) for a, b in paramValues]))
    log.debug("params-values: " + values)
    invalidParams: list = list(
        filter(lambda p: p[1] is None and p[0] not in paramsOptional, paramValues))
    invalidParams = list(map(lambda p: p[0], invalidParams))
    for p in invalidParams:
        log.debug("invalidParam="+p)
    if len(invalidParams) > 0:
        invalidParams = setResponseKO(
            'Required fields not informed: '+", ".join(invalidParams))
        results = list(map(lambda p: p[0], paramValues))
    else:
        results = list(map(lambda p: p[1], paramValues))
        invalidParams = ''
    results.insert(0, invalidParams)
    return results


def setResponseOK(res):
    return corsHeaders(make_response({'response': res}, 200))


def setResponseKO(ex):
    error = setResponseKO_internal__(ex)
    return corsHeaders(make_response({'error': error}, 500))


def setResponseKO_internal__(ex):
    if (isinstance(ex, Exception)):
        exceptions = getExceptionStackMessages(ex)
        error = list(dict.fromkeys(exceptions))
        log.exception(ex)
    else:
        error = ex
        log.error(ex)
    return error
