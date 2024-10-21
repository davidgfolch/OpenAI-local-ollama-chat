import unittest
from util.truncateStrings import truncateStrings
from langchain_core.messages import HumanMessage

LONG_TEXT = "This is a very long string that needs truncating."
TRUNCATED_TEXT = "This is a very long [...]"
SHORT_TEXT = "short text"


class TestTruncateStrings(unittest.TestCase):

    class NoAttributesClassMeta(type):
        def __setattr__(cls, name, value):
            if name not in cls.__dict__:
                raise AttributeError("Cannot set attributes")
            type.__setattr__(cls, name, value)

    def test_truncate_string(self):
        result = truncateStrings(None, max=20)
        self.assertEqual(result, None)
        # string
        result = truncateStrings(LONG_TEXT, max=20)
        self.assertEqual(result, TRUNCATED_TEXT)
        result = truncateStrings(SHORT_TEXT, max=20)
        self.assertEqual(result, SHORT_TEXT)
        # dict
        result = truncateStrings({"key": LONG_TEXT}, max=20)
        self.assertEqual(result["key"], TRUNCATED_TEXT)
        # list
        result = truncateStrings([LONG_TEXT], max=20)
        self.assertEqual(result[0], TRUNCATED_TEXT)
        # tuple
        result = truncateStrings(("x", LONG_TEXT), max=20)
        self.assertEqual(result[1], TRUNCATED_TEXT)
        # BaseMessage
        result = truncateStrings(HumanMessage(LONG_TEXT), max=20)
        self.assertEqual(result.content, TRUNCATED_TEXT)
        # other
        result = truncateStrings(HumanMessage(LONG_TEXT), max=20)
        self.assertEqual(result.content, TRUNCATED_TEXT)


if __name__ == '__main__':
    unittest.main()
