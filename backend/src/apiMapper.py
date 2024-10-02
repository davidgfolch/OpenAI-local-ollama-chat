import re
from ast import Dict
from markdown import markdown
import mdformat
from logConfig import initLog

log = initLog(__file__)

def markDownToHtml(md:str):
    formatted_md = mdformat.text(re.sub(r'\n{3,}', '\n\n',md), options= {'end-of-line':'crlf'})
    return markdown(formatted_md, extensions=['extra']) #https://python-markdown.github.io/extensions/

def listMapper(msg: Dict):
    key = 'a' if 'q' not in msg else 'q'
    value = msg.get(key, '')
    log.info(f"mapping key/value => {key}/{value}")
    return {key: markDownToHtml(value)}