import unittest

import pytest
from util.truncateStrings import TruncateStrings
from langchain_core.messages import HumanMessage, AIMessage

LONG_TEXT = "This is a very long string that needs truncating."
TRUNCATED_TEXT = "This is a very long [...]"
SHORT_TEXT = "short text"

sut = TruncateStrings({HumanMessage: ["content"]}, 20)


class TestTruncateStrings(unittest.TestCase):

    def test_truncate_string(self):
        res = sut.process(None)
        self.assertEqual(res, None)
        # string
        res = sut.process(LONG_TEXT)
        self.assertEqual(res, TRUNCATED_TEXT)
        res = sut.process(SHORT_TEXT)
        self.assertEqual(res, SHORT_TEXT)
        # dict
        res = sut.process({"key": LONG_TEXT})
        self.assertEqual(res["key"], TRUNCATED_TEXT)
        # list
        res = sut.process([LONG_TEXT])
        self.assertEqual(res[0], TRUNCATED_TEXT)
        # tuple
        res = sut.process(("x", LONG_TEXT))
        self.assertEqual(res[1], TRUNCATED_TEXT)
        # BaseMessage
        res = sut.process(HumanMessage(LONG_TEXT))
        self.assertEqual(res.content, TRUNCATED_TEXT)
        # error
        with pytest.raises(Exception):
            res = sut.process(AIMessage(LONG_TEXT))
        # error
        res = sut.process(type(HumanMessage))
        assert res == type(HumanMessage)


if __name__ == '__main__':
    unittest.main()
