import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import safe_calculate, get_course_fee, late_fee, check_exam_eligibility


class TestDay8Rules(unittest.TestCase):
    def test_fees(self):
        self.assertEqual(get_course_fee("CS101"), 12000)
        self.assertEqual(get_course_fee("ai202"), 18000)
        self.assertIsNone(get_course_fee("UNKNOWN"))
        self.assertEqual(late_fee(5), 500)
        self.assertEqual(late_fee(30), 2000)
        self.assertEqual(safe_calculate("12000 + 18000 + 2000"), 32000)
        self.assertEqual(safe_calculate("12000 + 18000 + 500"), 30500)

    def test_eligibility_bands(self):
        self.assertEqual(check_exam_eligibility(82)["status"], "eligible")
        result = check_exam_eligibility(70)
        self.assertEqual(result["status"], "condonation_required")
        self.assertEqual(result["condonation_fee_per_course"], 500)
        self.assertEqual(check_exam_eligibility(50)["status"], "not_eligible")

    def test_safe_calculator_rejects_code(self):
        with self.assertRaises(ValueError):
            safe_calculate("__import__('os').system('echo unsafe')")
        with self.assertRaises(ValueError):
            safe_calculate("x + 1")
        with self.assertRaises(ValueError):
            safe_calculate("1 / 0")

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            late_fee(-1)
        with self.assertRaises(ValueError):
            check_exam_eligibility(101)


if __name__ == "__main__":
    unittest.main()
