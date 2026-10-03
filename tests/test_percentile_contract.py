import unittest

from finops.services.statistics import percentile


class PercentileContractTests(unittest.TestCase):
    def test_interpolation_and_boundaries(self):
        self.assertEqual(percentile([10, 30, 20], 0.25), 15)
        self.assertEqual(percentile([10, 30], 0), 10)
        self.assertEqual(percentile([10, 30], 1), 30)
        self.assertEqual(percentile([], 0.5), 0)

    def test_invalid_quantiles_fail_even_for_empty_inputs(self):
        for quantile in (float("nan"), float("inf"), True):
            for values in ([], [1], [1, 2]):
                with (
                    self.subTest(quantile=quantile, values=values),
                    self.assertRaisesRegex(ValueError, "quantile"),
                ):
                    percentile(values, quantile)

    def test_non_finite_observations_are_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with (
                self.subTest(value=value),
                self.assertRaisesRegex(ValueError, "values must be finite"),
            ):
                percentile([1, value], 0.5)
