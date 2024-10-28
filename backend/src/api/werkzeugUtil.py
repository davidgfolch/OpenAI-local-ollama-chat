import logging
import os
from pathlib import Path
from werkzeug import Request
from werkzeug.datastructures import FileStorage, ImmutableMultiDict

from constants import UPLOAD_FOLDER
from util.logUtil import initLog

log = initLog(__file__, logging.DEBUG)

Request.max_form_parts = 100
Request.max_content_length = 16 * 1000 * 1000  # 16 megabytes

def saveUploadFiles(request):
    files: ImmutableMultiDict = request.files
    fileNames = []
    for (fileName, files) in files.lists():
        log.debug(f'fileName={fileName}, files={files}')
        if fileName:
            for file in files:
                f: FileStorage = file
                dirname = os.path.dirname(UPLOAD_FOLDER + f.filename)
                log.info(f"pathStr={dirname} => f.filename={f.filename}")
                Path(dirname).mkdir(parents=True, exist_ok=True)
                f.save(UPLOAD_FOLDER + f.filename)
                fileNames.append(f.filename)
    return fileNames
