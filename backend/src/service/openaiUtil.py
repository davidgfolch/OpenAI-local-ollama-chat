from openai import OpenAI
from openai.pagination import SyncPage
from openai.types import Model

from service.host import hostArgs
from util.logUtil import initLog

log = initLog(__file__)

openAICli = OpenAI(**hostArgs)

def getModels() -> list:
    res: SyncPage[Model] = openAICli.models.list()
    res = list(map(lambda m: m.id, res.data))
    res.sort()
    return res
