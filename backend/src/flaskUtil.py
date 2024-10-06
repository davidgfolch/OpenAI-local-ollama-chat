from flask import Response, make_response, Request
from exceptionUtil import getExceptionStackMessages
from logConfig import initLog
import logging

log = initLog(__file__, logging.DEBUG)


def corsHeaders(res: Response = Response()):
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'DELETE,GET,POST,OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return res


# see https://pypi.org/project/Flask-Parameter-Validation/
def getReqParams(request: Request, params: list):
    paramValue: list = list(map(lambda p: (p, request.json.get(p)), params))
    log.debug("params-values: " + (", ".join([str(a)+'='+str(b) for a, b in paramValue])))
    invalidParams: list = list(filter(lambda p: p[1] is None, paramValue))
    invalidParams = list(map(lambda p: p[0], invalidParams))
    for p in invalidParams:
        log.debug("invalidParam="+p)
    if len(invalidParams) > 0:
        invalidParams = setResponseKO(
            'Required fields not informed: '+", ".join(invalidParams))
        results = list(map(lambda p: p[0], paramValue))
    else:
        results = list(map(lambda p: p[1], paramValue))
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
