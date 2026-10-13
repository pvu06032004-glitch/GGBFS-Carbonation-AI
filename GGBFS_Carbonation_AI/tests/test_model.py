import unittest
from src.model import generate_synthetic_dataset, train_and_evaluate, predict_depth, DEFAULTS
from src.lifetime import estimate_lifetime
class Tests(unittest.TestCase):
    def test_pipeline(self):
        b=train_and_evaluate(generate_synthetic_dataset(100)); self.assertGreaterEqual(float(predict_depth(b,DEFAULTS)[0]),0)
    def test_lifetime(self):
        r=estimate_lifetime(10,365.25,30,5); self.assertAlmostEqual(r['t_init_years'],9); self.assertAlmostEqual(r['t_total_years'],14)
    def test_invalid(self):
        with self.assertRaises(ValueError): estimate_lifetime(10,365.25,0)
if __name__=='__main__': unittest.main()
