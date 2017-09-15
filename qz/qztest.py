import unittest


class Qz(object):

    def stats(self):
        return "this is groovy stats"

    def process(self, sData, arrResponses):
        return "cow " + arrResponses[0] + " " + arrResponses[1]


class Test(unittest.TestCase):


    def test_stats(self):
        x = Qz()
        self.assertEqual("this is groovy stats", x.stats())
    
    def test_process(self):
        expected = "cow resp1 resp2"
        x = Qz()
        sData = "cow"
        arrResponses = ["resp1", "resp2"]
        self.assertEqual(expected, x.process(sData, arrResponses))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()