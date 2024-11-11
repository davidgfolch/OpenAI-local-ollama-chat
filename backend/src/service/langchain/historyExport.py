from datetime import datetime
import logging
from threading import Timer, current_thread
import json
import os
from pathlib import Path
import re
import shutil
from typing import Dict
from pathvalidate import sanitize_filepath
import zipfile
import urllib
from unidecode import unidecode
from service.langchain.langchainUtil import getFilePath, getSessionHistoryName
from util.files import createFolder
from util.logUtil import initLog

log = initLog(__file__, logging.DEBUG)


# autopep8: off
def exportHistory(user: str, history: str) -> Path:
    session = getSessionHistoryName(user, history)
    log.info(f'exportHistory loading history={getFilePath(session)}')
    outDir = sanitize_filepath(getFilePath(session, ''))+'/'
    userHistoryDir = sanitize_filepath(getFilePath(session, ''))
    createFolder(outDir)
    zipFile = userHistoryDir+'.zip'
    userHistoryDir = userHistoryDir+'/'
    with open(getFilePath(session)) as history:
        historyItems: Dict = json.load(history)
        if historyItems:
            readme = outDir+'README.md'
            with zipfile.ZipFile(zipFile, 'w', zipfile.ZIP_DEFLATED) as zip:
                log.debug(f'generating history export at {readme}')
                processHistoryItems(session, zip, historyItems, userHistoryDir, readme)
                zip.write(outDir+'README.md', userHistoryDir+'README.md')
    log.debug(f"returning {zipFile}")
    _cleanFuture(outDir, zipFile)
    return Path(zipFile).absolute()


def processHistoryItems(session, zip, historyItems, userHistoryDir, readme):
    with open(readme, 'w') as readmeWriter:
        readmeWriter.write(f'# openai-local-ollama-chat history {getFilePath(session)}\n\nExport date: {datetime.now().strftime("%Y-%b-%d %X")}')
        for item in historyItems:
            content: str = item['data']['content']
            type: str = item['data']['type']
            if not type == 'human':
                answerDir = _answerDir(content)
                log.debug(f'history CONTENT {content}')
                newContent = _moveCodeBlocksToFiles(zip, userHistoryDir, answerDir, content, type)
                newContent = _cleanMarkdown(newContent)
                readmeWriter.write(newContent)
        readmeWriter.write('\n')


def _cleanMarkdown(md: str) -> str:
    md = re.sub(r'[*]+Código de ejemplo:?[*]+', '', md, FLAGS)  # remove repetitive "header"
    md = re.sub(r'[*]+Instalación de las librerías:?[*]+', '', md, FLAGS)  # remove repetitive "header"
    md = re.sub(r'[^\n][\n]```([a-z]+)', r'\n\n```\1', md, FLAGS)
    md = re.sub(r'```\n(?!=\n)', r'```\n\n', md, FLAGS)
    md = re.sub(r'\n[*]{2}([^*]+)[*]{2}\s?\n', r'\n### \1\n\n', md, FLAGS)  # replaces **(.*)** by ### .*
    md = re.sub(r'\n[*]   ', '\n* ', md, FLAGS)  # replaces *   xxx by * xxx
    md = re.sub(r'(\n+[#]+ +)[*]{2}([^*]+)[*]{2}(\s?\n)', r'\1\2\3', md, FLAGS)  # remove ** from titles
    md = re.sub(r'(\n[#]+ +.+)[.:!]+\n', r'\1\n', md, FLAGS)
    md = re.sub(r'[\n]{3,}', r'\n\n', md, FLAGS)
    md = re.sub(r'(?<=\b)([a-z]{3,5}://[a-z][a-z0-9_-]+(:\d{1,5}|\.[a-z]{2,10})(/[a-z][a-z0-9_-]+)*(/)?)(?=\b)', r' <\1> ', md, FLAGS)   # http://localhost:8000/ -> <http://localhost:8000/>
    return md


def _answerDir(content) -> str:
    dir: str = content.split('\n')[0].split('.')[0]
    return sanitize_filepath(dir) + '/'


FLAGS = re.IGNORECASE | re.MULTILINE | re.DOTALL
PATTERN_FILE_NAME = '([a-z_-]+[.][a-z]{1,3})'
PATTERN_CODE_BLOCK = '[`]{3}[a-z_-]+ *\n+ *((?!```).*\n)+[`]{3}'
VALID_FOLDER_FILE_CHARS = '[a-zá-úà-ùä-ûñç_]+[a-zá-úà-ùä-ûñç0-9_-]*'
PATTERN_FILENAME_CODE = re.compile('[*`]+((' + VALID_FOLDER_FILE_CHARS + '/)*' + VALID_FOLDER_FILE_CHARS +
                                   '([.][a-z]{1,4})+)[`:*]+[^\n]*\n+^```[a-z-_]*\\s*\n(.*?)(?=^```)```', FLAGS)
MIN_LINES = 1


def _moveCodeBlocksToFiles(zip: zipfile.ZipFile, userHistoryDir: str, answerDir: str, content: str, type: str) -> str:
    content = _byPattern(PATTERN_FILENAME_CODE, zip, userHistoryDir, answerDir, content, type)
    return content


def _byPattern(pattern: re.Pattern, zip: zipfile.ZipFile, userHistoryDir: str, answerDir: str, content: str, type: str) -> str:
    for fileNamesAndContents in re.finditer(pattern, content):
        fileNameOriginal = fileNamesAndContents.groups()[0]
        fileName = unidecode(fileNameOriginal)
        fileContent = fileNamesAndContents.groups()[3]
        log.debug(f'fileNames: {fileName} content: {fileContent}')
        if fileName and fileContent and len(fileContent.split('\n')) >= MIN_LINES:
            log.debug(f'content match to file {fileName}')
            newFilePath = sanitize_filepath(userHistoryDir+'/'+answerDir+fileName)
            createFolder(os.path.dirname(newFilePath))
            with open(newFilePath, 'w') as f:
                log.debug(f'history file {newFilePath}')
                f.write(f"{fileContent}")
            zip.write(newFilePath, userHistoryDir+'/'+answerDir + fileName)
            mdDirFile = urllib.parse.quote(answerDir + fileName, safe='/', encoding=None, errors=None)
            content = re.sub(pattern, f'[{fileName}]({mdDirFile})\n', content, 1)
    prefix = '' if content.startswith('\n## ') else '\n\n## '
    return prefix + content


def _clean(outDir: str, zipFile: str):
    # log.debug(f'cleaning export folder {outDir} in another thread')
    shutil.rmtree('./'+outDir)
    os.remove(zipFile)

def _cleanFuture(outDir: str, zipFile: str, interval=10):
    log.debug(f'cleaning export in {interval}secs folder {outDir} in thread ')
    Timer(interval=interval, function=_clean, args=(outDir, zipFile)).start()
