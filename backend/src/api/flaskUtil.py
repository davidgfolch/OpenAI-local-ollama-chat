from flask import Response, make_response, Request
from api.apiException import ValidationException
from util.exceptionUtil import getExceptionStackMessages
from util.logUtil import initLog
import logging

log = initLog(__file__, logging.INFO)

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'DELETE,GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}

EVENT_STREAM_CHUNKED_HEADERS = {
    'Accept': 'text/event-stream',
    'Content-Type': "text/event-stream",
}
EVENT_STREAM_CHUNKED_HEADERS.update(CORS_HEADERS)
REQUIRED_FIELDS = 'Required fields not informed: '


def corsHeaders(res: Response = Response()):
    res.headers.update(CORS_HEADERS)
    return res


# TODO: ? https://pypi.org/project/Flask-Parameter-Validation/
def getReqParams(req: Request, params: list, paramsOp: list = []):
    paramValues: list = list(map(lambda p: (p, req.json.get(p)), params))
    values = (", ".join([str(a)+'='+str(b) for a, b in paramValues]))
    log.debug("params-values: " + values)
    invalid: list = list(
        filter(lambda p: p[1] is None and p[0] not in paramsOp, paramValues))
    invalid = list(map(lambda p: p[0], invalid))
    if len(invalid) > 0:
        for p in invalid:
            log.debug("invalidParam="+p)
        raise ValidationException(REQUIRED_FIELDS+", ".join(invalid))
    return list(map(lambda p: p[1], paramValues))


def setResponseOK(res: str):
    return corsHeaders(make_response({'response': res}, 200))


def setResponseKO(ex):
    error = __setResponseKO(ex)
    statusCode = 400 if isinstance(ex, ValidationException) else 500
    return corsHeaders(make_response({'error': error}, statusCode))


def __setResponseKO(ex):
    if (isinstance(ex, Exception)):
        exceptions = getExceptionStackMessages(ex)
        error = list(dict.fromkeys(exceptions))
        log.exception(ex)
    else:
        error = [ex]
        log.error(ex)
    return error
