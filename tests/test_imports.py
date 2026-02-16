import unittest


class TestImports(unittest.TestCase):
    def test_imports(self) -> None:
        import datadrift.cli  # noqa: F401
        import datadrift.drift  # noqa: F401
        import datadrift.specs  # noqa: F401


if __name__ == "__main__":
    unittest.main()

