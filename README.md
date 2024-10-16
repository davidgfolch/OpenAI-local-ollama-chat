# OpenAI langchain Local Ollama chat

[![backend-build-lint-and-tests](https://github.com/davidgfolch/OpenAI-local-ollama-chat/actions/workflows/backend-build-lint-and-tests.yml/badge.svg)](https://github.com/davidgfolch/OpenAI-local-ollama-chat/actions/workflows/backend-build-lint-and-tests.yml)
[![Backend coverage](README.md_images/coverage.svg)](backend/README.md#generate-coverage-badge-for-readmemd)

This project implements a local AI chat, with:

- Response pretty printing: markdown to html & code highlight
- Backend chat history with persistence (file store)
  - Delete question/answer in file history.
- LLM response live streaming: chunked streaming
  - Stop current streaming response.
- Tech-stack: Vue3 -> Python (langchain/openai) -> Ollama

## Watch the Youtube demo

<a href="https://youtu.be/lzJOmwnY1m4" target="_blank">
    <img src="README.md_images/youtubeScreenshot.png"/>
</a>

## Ollama installation & setup (required)

See [README_OLLAMA.md](README_OLLAMA.md)

## Project run

### Run Ollama and load model

```bash
sudo service ollama start
```

### Run backend & frontend

See respective README.md docs: [backend](backend/README.md) & [frontend](frontend/README.md)

## References

### Langchain

- <https://python.langchain.com/docs/concepts/>
- <https://python.langchain.com/docs/how_to/>
- <https://python.langchain.com/docs/integrations/platforms/openai/>
- <https://python.langchain.com/docs/integrations/chat/ollama/>
- <https://python.langchain.com/api_reference/ollama/index.html>
- <https://api.python.langchain.com/en/latest/llms/langchain_community.llms.ollama.Ollama.html>
- <https://api.python.langchain.com/en/latest/ollama/index.html>
- <https://api.python.langchain.com/en/latest/openai_api_reference.html>

### OpenAI

- <https://github.com/openai/openai-python>
- <https://platform.openai.com/docs/api-reference/introduction>
- <https://platform.openai.com/docs/libraries/python-library>

### Ollama

- <https://github.com/ollama/ollama>
- <https://ollama.com/library>
- <https://www.reddit.com/r/LocalLLaMA/>

## TODO

1. Langchain PR for FileChatMessageHistory delete_message.
2. Upload file or folder to give context to llm (RAG??).
3. Agents?
4. Multiple question scheduler.

## Known issues (todo)

### DeepSeekCoder V2 fails randomly

When context gets bigger and can't fit into VRAM (after several q/a f.ex.), Ollama throws the following error because Deepseek2 does not support K-shift

```log
ollama[17132]: /go/src/github.com/ollama/ollama/llm/llama.cpp/src/llama.cpp:15110: Deepseek2 does not support K-shift
ollama[17132]: Could not attach to process.  If your uid matches the uid of the target
ollama[17132]: process, check the setting of /proc/sys/kernel/yama/ptrace_scope, or try
ollama[17132]: again as the root user.  For more details, see /etc/sysctl.d/10-ptrace.conf
ollama[17132]: ptrace: Inappropriate ioctl for device.
ollama[17132]: No stack.
ollama[17132]: The program is not being run.
```
