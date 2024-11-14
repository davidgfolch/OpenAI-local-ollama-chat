
from service.langchain.prompByModel import Model, cleanMarkdown, getSpecifications


QWEN = Model.QWEN_2_5_CODER.value
LLAMA = Model.LLAMA_3_2.value

MARKDOWN_INITIAL = """
## TEST
Some text here.
LLM is returning handling code block mark:
```somedanglingcodemark

### Py code ok:
```python
from a import b
```



"""
MARKDOWN_CLEAN = """
## TEST
Some text here.
LLM is returning handling code block mark:

### Py code ok

```python
from a import b
```

"""


def assertSameSpecs(model1: str, model2: str):
    assert getSpecifications(model1) == getSpecifications(model2)


def test_getSpecifications():
    assertSameSpecs(QWEN, QWEN)
    assertSameSpecs(f'{QWEN}:7b', QWEN)
    assertSameSpecs('unknown model', LLAMA)


def test_cleanMarkdown():
    assert cleanMarkdown(QWEN, MARKDOWN_INITIAL) == MARKDOWN_CLEAN
