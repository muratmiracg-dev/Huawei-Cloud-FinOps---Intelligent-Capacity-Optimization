from __future__ import annotations

import unittest

from finops.services.statistics import mean, median, percentile, sample_stddev


class StatisticsTests(unittest.TestCase):
    def test_percentile_empty(self):
        self.assertEqual(percentile([], 0.95), 0)

    def test_percentile_single(self):
        self.assertEqual(percentile([8], 0.95), 8)

    def test_percentile_interpolates(self):
        self.assertAlmostEqual(percentile([0, 10], 0.25), 2.5)

    def test_percentile_clamps_quantile(self):
        self.assertEqual(percentile([1, 2, 3], 2), 3)

    def test_median(self):
        self.assertEqual(median([9, 1, 5]), 5)

    def test_mean_empty(self):
        self.assertEqual(mean([]), 0)

    def test_sample_stddev(self):
        self.assertAlmostEqual(sample_stddev([1, 2, 3]), 1.0)


if __name__ == "__main__":
    unittest.main()
