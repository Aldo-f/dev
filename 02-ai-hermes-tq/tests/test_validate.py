import unittest
from validate import parse_validation_section

class TestValidation(unittest.TestCase):
    def test_parse_validation_section(self):
        md = """
# Task
Some text.

### VALIDATION
- [ ] Item 1
- [x] Item 2
* [ ] Item 3
1. [ ] Item 4
"""
        checks = parse_validation_section(md)
        self.assertEqual(len(checks), 4)
        self.assertFalse(checks[0]['checked'])
        self.assertTrue(checks[1]['checked'])
        self.assertEqual(checks[0]['text'], "Item 1")
        self.assertEqual(checks[2]['text'], "Item 3")
        self.assertEqual(checks[3]['text'], "Item 4")

    def test_no_validation(self):
        md = "# Task\nNo validation here."
        checks = parse_validation_section(md)
        self.assertEqual(len(checks), 0)

if __name__ == '__main__':
    unittest.main()
