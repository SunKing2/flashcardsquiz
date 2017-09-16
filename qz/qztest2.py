import time
import glob
import sys
import re

global gSessionStart
gSessionStart = time.time()
global gQCount 
gQCount = 0
global gQData
gQData = []

global gFileNum_Dirty
gFileNum_Dirty = []
global gFileNum_FileName
gFileNum_FileName = []
global gFileNum_QuestionCount
gFileNum_QuestionCount = []

global gQCorrect
gQCorrect = 0
global promptQord
promptQord = 0
global gTotalTime
gTotalTime = 0

global kFQuestion
global kFAnswer
global kFRating
global kFAge
global kFFlags
global kFNote
global kFields
kFQuestion = 0
kFAnswer = 1
kFRating = 2
kFAge = 3
kFFlags = 4
kFNote = 5
kFields = 6

global configMax_rating
configMax_rating = 100

global gQByAge
gQByAge = []


# ============================= begin lvb created procedures =======================
def printf(sformat, *args):
    sys.stdout.write(sformat % args)
# ============================= end   lvb created procedures =======================


# DoListStats - list file stats
def DoListStats():
    solved = 0
    totalRating = 0
    unseen = 0
    unsolved = 0
    age_sum = 0
    now = time.time()
    count = 0
    
    #calculate stats
    if (True):
        qIndex = kFRating
        #offsetq = kFQuestion - kFRating
        #offseta = kFAnswer - kFRating
        offsetage = kFAge - kFRating
        while (qIndex <= len(gQData)):
            #next unless & $config::question_filter($gQData[$qIndex + $offsetq]) && & $config::answer_filter($gQData[$qIndex + $offseta]);
            age_sum += int(gQData[qIndex + offsetage])
            count += 1
            sRating = gQData[qIndex]
            rating = int(sRating)
            if (re.match("^\+", sRating)):
                unseen +=1
            elif(rating == configMax_rating):
                unsolved += 1
            else:
                solved += 1
                totalRating += rating
            qIndex += kFields

    #print report
    seen = solved + unsolved;
    printf ("Total: %d\n", unseen + seen)
    if (unseen): printf ("Unseen: %d (%d%%)\n", unseen, 0.5 + 100.0 * (1.0 * unseen / (seen + unseen)))
    sys.stdout.write ("Solved: " + str(solved))
    if (seen): printf (" (%d%%)", 0.5 + 100.0 * solved / seen),
    sys.stdout.write  ("\nUnsolved: " + str(unsolved))
    if (seen): printf (" (%d%%)", 0.5 + 100.0 * unsolved / seen),
    print ("");
    if (solved): printf ("Mean solution time: %.1f s\n", 1.0 * totalRating / solved)
    if (unsolved or unseen): printf ("Mean difficulty: %.1f s\n", (100.0 * (unsolved + unseen) + totalRating) / (seen + unseen))
    if (count): print ("Mean solution age: " +
        FormatTime(int(now - 1.0 * age_sum / count)) + "\n"),
    t = 0 
    if (True):
        i = 0
        #offsetq = kFQuestion - kFAge
        #offseta = kFAnswer - kFAge
        while (gQByAge and i <= len(gQByAge)):
            qIndex = gQByAge[i] * kFields + kFAge
            i += 1
            #next unless & $config::question_filter($gQData[$qIndex + $offsetq]) && & $config::answer_filter($gQData[$qIndex + $offseta]);
            t = gQData[qIndex]
            #last
    print ("Oldest solution: " + (FormatTime(now - t) if t else 'never') + "\n"),
#DoListStats

def DoRunQuiz(argv):
    gSessionStart = time.time()
    if not argv: argv = glob.glob('*.qz')
    LoadData(argv)

def FormatTime(interval):
    if (interval < 60) : return str(interval) + " s"
    interval = int(interval/60)
    if (interval < 60) : return str(interval) + " m"
    interval = int(interval/60)
    if (interval < 24) : return str(interval) + " h"
    interval = int(interval/24)
    return str(interval) + " d"

def LoadData(files):
    gQCount = 0
    for ffile in files:
        fileQCount = 0
        with open(ffile, 'r') as infile:
            for line in infile.read().splitlines():
                fields = line.split('\t')
                if not fields: continue
                gQData.extend(fields)
                gQCount += 1
                fileQCount += 1
        gFileNum_Dirty.append(0)
        gFileNum_FileName.append(ffile)
        gFileNum_QuestionCount.append(fileQCount)

def S():
    printf ("\nYou answered %d question%s correctly of %d",\
    gQCorrect, '' if (gQCorrect == 1) else 's', promptQord),
    if promptQord: printf (" (%.1f%%)", 100 * gQCorrect/promptQord, end="")
    print (".")
    if gQCorrect: printf ("You took on average %.1f seconds to answer correctly.",
    gTotalTime/gQCorrect)
    if promptQord and gQCorrect/promptQord > 0.9: print ("Congratulations!") 
    elapsed = time.time() - gSessionStart
    printf ("Elapsed time: %d:%02d:%02d\n", 
    int(elapsed/3600), int(elapsed/60) % 60, elapsed % 60)
    print ("\nCurrent statistics for this question set:")
    #DoListStats()


# ============================= stuff needed for test =======================
class MyOutput(object):
    def __init__(self):
        self.data = []

    def write(self, s):
        self.data.append(s)

    def __str__(self):
        return "".join(self.data)
 

# ============================= test =======================
import unittest
class Test(unittest.TestCase):

# ------------------------start helper methods only -------------------
    def ensureInputDataMakesStats(self, inputData, stats):
        stdout_org = sys.stdout
        my_stdout = MyOutput()
        try:
            # clean up global variables (TODO probably isn't complete)
            del gQData[:]
            sys.stdout = my_stdout
            
            # create outputfile which will be read into qz
            open('mystuff.qz', 'w').write(inputData)
            LoadData(glob.glob('*.qz'))
            S()
            DoListStats()
        finally:
            sys.stdout = stdout_org
        expected = stats
        self.assertEquals( expected, str(my_stdout)) 
# ------------------------end helper methods only -------------------


    
    def test_makeInputFileForQz(self):
        mydata = '''AQT\tQAT\t1\t1505179232\tC\t
IQS\tQIS\t50\t1505179230\tC\t
'''
        open('mystuff.qz', 'w').write(mydata)


    def test_readData(self):
        expected = "IQS"
        DoRunQuiz([])
        self.assertEquals(expected, gQData[6])
        self.assertEquals("1505179230", gQData[9])
    
    
    def test_S(self):
        stdout_org = sys.stdout
        my_stdout = MyOutput()
        try:
            sys.stdout = my_stdout
            S()
        finally:
            sys.stdout = stdout_org
        expected = ('''\nYou answered 0 questions correctly of 0.
Elapsed time: 0:00:00

Current statistics for this question set:\n''')
 
        self.assertEquals( expected, str(my_stdout)) 


    def test_DoListStats(self):
        stdout_org = sys.stdout
        my_stdout = MyOutput()
        try:
            sys.stdout = my_stdout
            DoListStats()
        finally:
            sys.stdout = stdout_org
        expected = ('''Total: 0
Solved: 0
Unsolved: 0
Oldest solution: never
''')
 
        self.assertEquals( expected, str(my_stdout)) 


    def test_ensureInputDataMakesStats(self):
        inputData = '''AQT\tQAT\t1\t1505179232\tC\t
IQS\tQIS\t50\t1505179230\tC\t
'''
        expectedStats = ('''
You answered 0 questions correctly of 0.
Elapsed time: 0:00:00

Current statistics for this question set:
Total: 2
Solved: 2 (100%)
Unsolved: 0 (0%)
Mean solution time: 25.5 s
Mean solution age: 3 d
Oldest solution: never
''')
        self.ensureInputDataMakesStats(inputData, expectedStats)
    
    def test_EnsureInputDataMakesStats_new_questions(self):
        inputData = '''aeiilnr\tairline\t+100\t0\tCO\tairline: +"*turbochargers" [John Chew]<p>airline: h=rs -rs h+s 
aaeeint\ttaeniae\t+100\t0\tCO\t+"l"<p>taeniae: -
aeinstu\taunties sinuate\t+100\t0\tCO\t+"dgklpqrs"<p>aunties: fl+t j+t <br>sinuate: =ds in- in+d in+s 
'''
        expectedStats = ('''
You answered 0 questions correctly of 0.
Elapsed time: 0:00:00

Current statistics for this question set:
Total: 3
Unseen: 3 (100%)
Solved: 0
Unsolved: 0
Mean difficulty: 100.0 s
Mean solution age: 17425 d
Oldest solution: never
''')
        self.ensureInputDataMakesStats(inputData, expectedStats)
    

    def test_EnsureInputDataMakesStats_old_and_new_questions(self):
        inputData = '''AKNPR\tPRANK\t29\t1505481030\tCO\t
IOPTT\tPITOT\t100\t0\tCO\t
AAEPR\tAREPA PARAE\t68\t1505423280\tCO\t
BOOWX\tOXBOW\t29\t1505409667\tCO\t
BOTUY\tOUTBY\t68\t1505482847\tCO\t
ALNOY\tONLAY\t68\t1505481126\tCO\t
BEEOS\tOBESE\t68\t1505482851\tCO\t
AHIKN\tNIKAH\t100\t0\tCO\t
EMOPY\tMOPEY MYOPE\t100\t0\tCO\t
HIMRT\tMIRTH\t100\t0\tCO\t
CEELY\tLYCEE\t29\t1505481155\tCO\t
AEELV\tLEAVE\t+100\t0\tCO\t
AALNU\tLAUAN\t+100\t0\tCO\t
'''
        expectedStats = ('''
You answered 0 questions correctly of 0.
Elapsed time: 0:00:00

Current statistics for this question set:
Total: 13
Unseen: 2 (15%)
Solved: 7 (64%)
Unsolved: 4 (36%)
Mean solution time: 51.3 s
Mean difficulty: 73.8 s
Mean solution age: 8042 d
Oldest solution: never
''')
        self.ensureInputDataMakesStats(inputData, expectedStats)
    




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()