from openai import OpenAI
from openai.pagination import SyncPage
from openai.types import Model

from service.host import hostArgsV1
from util.logUtil import initLog

log = initLog(__file__)

openAICli = OpenAI(**hostArgsV1)

def getModels() -> list:
    res: SyncPage[Model] = openAICli.models.list()
    if not res.data:
        raise Exception("No available models found in Ollama, you need to: ollama pull <model>")
    res = list(map(lambda m: m.id, res.data))
    res.sort()
    return res
