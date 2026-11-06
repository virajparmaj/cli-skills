"""Independently recompute canonical fixture anchors from their stated inputs."""
import json
import math
from pathlib import Path
import statistics
import unittest

DATA = json.loads((Path(__file__).parents[1] / 'references/benchmarks.json').read_text())
FIXTURES = {item['id']: item for group in ('financial', 'ml') for item in DATA[group]}


class FixtureAnswerTests(unittest.TestCase):
    def test_sharpe_conventions(self):
        for ddof, deviation in ((0, statistics.pstdev), (1, statistics.stdev)):
            fixture = FIXTURES[f'sharpe_daily_ddof{ddof}_ann252']
            r = fixture['input']['returns']
            expected = statistics.mean(r) / deviation(r) * math.sqrt(252)
            self.assertAlmostEqual(fixture['expected'], expected, places=10)

    def test_sortino_uses_all_observations_in_downside_denominator(self):
        fixture = FIXTURES['sortino_daily_ddof0_ann252']
        r = fixture['input']['returns']
        downside = math.sqrt(sum(min(x, 0) ** 2 for x in r) / len(r))
        self.assertAlmostEqual(fixture['expected'], statistics.mean(r) / downside * math.sqrt(252))

    def test_sample_annualized_volatility(self):
        fixture = FIXTURES['annualized_vol_daily_ddof1']
        self.assertAlmostEqual(fixture['expected'], statistics.stdev(fixture['input']['returns']) * math.sqrt(252))

    def test_binary_log_loss(self):
        fixture = FIXTURES['log_loss_known']
        values = fixture['input']
        terms = [y * math.log(p) + (1-y) * math.log(1-p)
                 for y, p in zip(values['y_true'], values['y_prob'])]
        self.assertAlmostEqual(fixture['expected'], -statistics.mean(terms))


if __name__ == '__main__':
    unittest.main()
