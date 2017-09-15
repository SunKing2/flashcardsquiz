import unittest

class Template(object):

    def __init__(self, template):
        self.arrTemplate = template.splitlines()
        # create array of boolean true for each line of template
        self.showThisString = [True] * len(self.arrTemplate)
        
        
    def getLine(self, lineNumber):
        return self.arrTemplate[lineNumber]
    
    # this entire method could be a list comprehension one-liner if I were smarter
    def getResult(self):
        lisTmp = [];
        i = 0;
        for s in self.arrTemplate:
            if (self.showThisString[i]):
                lisTmp.append(s)
            i = i + 1
        return '\n'.join(lisTmp)
    
    
    def setStringVisibility(self, stringNumber, visible):
        self.showThisString[stringNumber] = visible;


class Test(unittest.TestCase):


    def testGetLine(self):
        expected = "now that it has been eaten,"
        template = Template(
        """My cow gives less milk,
now that it has been eaten,
by a fierce dragon.""")
        self.assertEqual(expected, template.getLine(1))
    
    def testGetResult(self):
        expected = "My cow gives less milk,\nnow that it has been eaten,\nby a fierce dragon."
        template = Template(expected)
        self.assertEqual(expected, template.getResult())
    
    def testsetStringVisibility(self):
        template = Template("aa\nbb\ncc")
        expected = "aa\ncc"
        template.setStringVisibility(1, False)
        self.assertEqual(expected, template.getResult())
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()