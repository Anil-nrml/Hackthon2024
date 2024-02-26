import unittest
from calc import calc
class TestCalc(unittest.TestCase):
    def test_Add(self):
        result=calc.add(10,5)
        self.assertEqual(calc.add(10,5),15)
        self.assertEqual(calc.add(-1,1),0)
        self.assertEqual(calc.add(-1,-1),-2)
        self.assertEqual(calc.add(2,-1),1)

if __name__=='__main__':
    unittest.main()