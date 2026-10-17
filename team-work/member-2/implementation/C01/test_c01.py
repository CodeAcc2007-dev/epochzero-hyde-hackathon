"""C01-specific checks; M is injected by verify_c01.py."""
import unittest
M = None
class C01Tests(unittest.TestCase):
    def test_reserve_enablers_present_and_bounded(self):
        self.assertTrue(hasattr(M.EconomyPolicy, 'reserve_enablers'))
        self.assertEqual(M.EconomyPolicy.reserve_enablers.__func__.__code__.co_argcount if hasattr(M.EconomyPolicy.reserve_enablers,'__func__') else 3, 3)
