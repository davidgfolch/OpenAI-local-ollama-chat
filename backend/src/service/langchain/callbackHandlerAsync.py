import logging
from typing import Any, Dict, List
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage
from service.langchain.callbackHandler import truncate
from util.logUtil import initLog

log = initLog(__file__, logging.DEBUG)


class CallbackHandlerAsync(AsyncCallbackHandler):

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        log.debug("on_llm_start ==> serialized=%s prompts=%x", truncate(serialized), truncate(prompts))

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        log.debug("on_llm_end ==> response=%s", truncate(response))

    async def on_chat_model_start(self, serialized: dict[str, Any], messages: list[list[BaseMessage]], **kwargs) -> None:
        log.debug("on_chat_model_start ==> serialized=%s, messages=%s", truncate(serialized), truncate(messages))
