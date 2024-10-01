from typing import cast
from flask import Response, make_response, Request, jsonify
from logConfig import initLog
import logging

log = initLog(__file__, logging.DEBUG)

def corsHeaders(res: Response):
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'DELETE,GET,POST,OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return res

def getReqParams(request:Request, params:list): #see https://pypi.org/project/Flask-Parameter-Validation/
    paramValue:list = list(map(lambda p: (p, request.json.get(p)), params))
    log.debug(f"params-values: "+ (", ".join([str(a)+'='+str(b) for a,b in paramValue])))
    invalidParams:list = list(filter(lambda p: p[1] is None, paramValue))
    invalidParams = list(map(lambda p: p[0], invalidParams))
    for p in invalidParams: log.debug("invalidParam="+p)
    if len(invalidParams)>0: 
        invalidParams = setResponseKO('Required fields not informed: '+", ".join(invalidParams))
        results=list(map(lambda p: p[0], paramValue))
    else: results=list(map(lambda p: p[1], paramValue))
    results.insert(0, invalidParams)
    return results

def setResponseOK(res):
    return corsHeaders(make_response({'response': res}, 200))

def setResponseKO(ex):
    if (isinstance(ex,Exception)):
        exceptions=getExceptionStackMessages(ex)
        error=list(dict.fromkeys(exceptions))
        log.exception(ex)
    else:
        error=ex
        log.error(ex)
    return corsHeaders(make_response({'error': error}, 500))

def getExceptionStackMessages(ex, msgs=[]):
    if (isinstance(ex,Exception)): msgs.append(type(ex).__name__+": "+str(ex))
    else: msgs.append(ex)
    if (ex.__cause__): getExceptionStackMessages(ex.__cause__,msgs)
    return msgs
