import time
import glob
import sys
import re
import random
from os import rename
from qz import config
from qz import g
from qz import k
from qz import prompt


# ============================= begin lvb created procedures =======================
def printf(sformat, *args):
    sys.stdout.write(sformat % args)
def myfprintf(myfile, sformat, *args):
    myfile.write(sformat % args)
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
    qIndex = k.fRating
    #offsetq = k.fQuestion - k.fRating
    #offseta = k.fAnswer - k.fRating
    offsetage = k.fAge - k.fRating
    while (qIndex <= len(g.gQData)):
        #next unless & config::question_filter(g.gQData[qIndex + offsetq]) && & config::answer_filter(g.gQData[qIndex + offseta])
        age_sum += int(g.gQData[qIndex + offsetage])
        count += 1
        sRating = g.gQData[qIndex]
        rating = int(sRating)
        if (re.match(r"^\+", sRating)):
            unseen +=1
        elif(rating == config.max_rating):
            unsolved += 1
        else:
            solved += 1
            totalRating += rating
        qIndex += k.fields

    #print report
    seen = solved + unsolved
    printf("Total: %d\n", unseen + seen)
    if (unseen): printf("Unseen: %d (%d%%)\n", unseen, 0.5 + 100.0 * (1.0 * unseen / (seen + unseen)))
    sys.stdout.write ("Solved: " + str(solved))
    if (seen): printf(" (%d%%)", 0.5 + 100.0 * solved / seen)
    sys.stdout.write  ("\nUnsolved: " + str(unsolved))
    if (seen): printf(" (%d%%)", 0.5 + 100.0 * unsolved / seen)
    print("")
    if (solved): printf("Mean solution time: %.1f s\n", 1.0 * totalRating / solved)
    if (unsolved or unseen): printf("Mean difficulty: %.1f s\n", (100.0 * (unsolved + unseen) + totalRating) / (seen + unseen))
    if (count): print("Mean solution age: " +
        FormatTime(int(now - 1.0 * age_sum / count)))
    t = 0
    i = 0
    #offsetq = k.fQuestion - k.fAge
    #offseta = k.fAnswer - k.fAge
    while (g.gQByAge and i <= len(g.gQByAge)):
        qIndex = g.gQByAge[i] * k.fields + k.fAge
        i += 1
        #next unless & config::question_filter(g.gQData[qIndex + offsetq]) && & config::answer_filter(g.gQData[qIndex + offseta])
        t = g.gQData[qIndex]
        #last
    print("Oldest solution: " + (FormatTime(now - t) if t else 'never'))
#DoListStats

def DoRunQuiz(argv):
    g.gSessionStart = time.time()
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
    g.gQCount = 0
    for ffile in files:
        fileQCount = 0
        with open(ffile, 'r') as infile:
            for line in infile.read().splitlines():
                fields = line.split('\t')
                if not fields: continue
                g.gQData.extend(fields)
                g.gQCount += 1
                fileQCount += 1
        g.gFileNum_Dirty.append(0)
        g.gFileNum_FileName.append(ffile)
        g.gFileNum_QuestionCount.append(fileQCount)

# MungeData - precalculate information useful for running a quiz
def MungeData ():

    # round g.gQCount up to a power of two
    g.gQCount2 = 1
    while(g.gQCount2 < g.gQCount):
        g.gQCount2 <<= 1

    # calculate rating information
    g.gQByRating = [''] * (config.max_rating + 2)

    g.gTotalRating = 0
    def fun_loop():
        q = 0
        qIndex = k.fRating
        while (q<g.gQCount): # a fun loop
            rating = g.gQData[qIndex]
            print(q)
            g.gRatingTree.append(rating)
            g.gTotalRating += int(g.gRatingTree[q])
            g.gQByRating[int(rating)] += "%d " % q
            if not (q % 2):
                q += 1
                continue
            t1 = q-1
            g.gRatingTree[q] += g.gRatingTree[t1]
            t2 = 1
            t3 = q & (1 + q)

            t1 -= t2
            while t1 > t3:
                t2 += t2
                g.gRatingTree[q] += g.gRatingTree[t1]
                t1-=t2
            q += 1
            qIndex += k.fields
    fun_loop()

    # ($u1,$s1) = times printf "time: %5.2f %5.2f\n", $u1-$u0, $s1-$s0 # DEBUG

    # build chronological list
    def build_chronological_list():
        g.gQByAge = [0] * g.gQCount
        q = g.gQCount
        qIndex = q * k.fields + k.fAge
        while (q > 0):
            q -=1
            qIndex -= k.fields
            print('q=' + str(q))
            g.gQByAge[q] = qIndex
    build_chronological_list()

    # perl 5.10.0 segfaults if the following line is in the preceding block.
    # if placed here, it silently fails when returning from MungeData.
    # @gQByAge = sort { $gQData[$a] <=> $gQData[$b] || int(rand(3))-1; } @gQByAge;
    # TODO translate this properly, no shortcuts!
    g.gQByAge.sort(key=lambda x: int(g.gQData[x]) + random.random())
  
    for q1 in g.gQByAge:
        q1 = int(q1/k.fields)

    # build last-asked list
    g.gWhenAsked = [-config.mri] * g.gQCount

def S():
    printf("\nYou answered %d question%s correctly of %d",\
    g.gQCorrect, '' if (g.gQCorrect == 1) else 's', prompt.qord)
    #if prompt.qord: printf(" (%.1f%%)", 100 * g.gQCorrect/prompt.qord, end="")
    if prompt.qord: printf(" (%.1f%%)", 100 * g.gQCorrect/prompt.qord)
    print(".")
    if g.gQCorrect: printf("You took on average %.1f seconds to answer correctly.",
    g.gTotalTime/g.gQCorrect)
    if prompt.qord and g.gQCorrect/prompt.qord > 0.9: print("Congratulations!")
    elapsed = time.time() - g.gSessionStart
    printf("Elapsed time: %d:%02d:%02d\n",
    int(elapsed/3600), int(elapsed/60) % 60, elapsed % 60)
    print("\nCurrent statistics for this question set:")
    #DoListStats()


# SaveData() - save quiz data
def SaveData():
    qIndex = 0
    for fileNumber in range (0, len(g.gFileNum_Dirty)):
        if g.gFileNum_Dirty[fileNumber]:
            tName = g.gFileNum_FileName[fileNumber]
            tNewName = tName

            tNewName = re.sub(r'\.[^.]*', '', tNewName)
            tNewName += '.new'
            FILE = open(tNewName, 'w')
            tCount = g.gFileNum_QuestionCount[fileNumber]
            tFormat = "\t".join(['%s'] * k.fields) + "\n"
            while tCount > 0:
                try:
                    myfprintf(FILE, tFormat,*g.gQData[qIndex:qIndex+k.fields-0])
                except:
                    print("Error writing to %s (!)\nAborting" % tNewName)
                    raise
                qIndex += k.fields
                tCount -= 1
            try:
                FILE.close()
            except:
                print("Error closing %s\nAborting" % tNewName)
                raise
            try:
                rename(tNewName, tName)
            except:
                print("Error renaming tNewName to tName\nAborting")
                raise
            g.gFileNum_Dirty[fileNumber] = 0
        else:
            qIndex += k.fields*g.gFileNum_QuestionCount[fileNumber]

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
import shutil

class Test(unittest.TestCase):

# ------------------------start helper methods only -------------------
    def ensureInputDataMakesStats(self, inputData, stats):
        stdout_org = sys.stdout
        my_stdout = MyOutput()
        try:
            # clean up global variables (TODO probably isn't complete)
            del g.gQData[:]
            sys.stdout = my_stdout

            # create outputfile which will be read into qz
            f = open('mystuff.qz', 'w')
            f.write(inputData)
            f.close()
            LoadData(glob.glob('*.qz'))
            S()
            DoListStats()
        finally:
            sys.stdout = stdout_org
        expected = stats
        self.assertEqual(expected, str(my_stdout))
    
    def ginitialize(self):
        g.gSessionStart = time.time()
        g.gQCount = 0
        g.gQData = []
        
        g.gFileNum_Dirty = []
        g.gFileNum_FileName = []
        g.gFileNum_QuestionCount = []
        
        g.gQCorrect = 0
        g.gTotalTime = 0
        
        g.gQByAge = []
        
        # added after save working
        g.gQCount2 = 0
        g.gQByRating = []
        g.gRatingTree = [] 

    def ensureReadData(self, expected_time="1505179230"):
        expected = "IQS"
        DoRunQuiz([])
        self.assertEqual(expected, g.gQData[6])
        self.assertEqual(expected_time, g.gQData[9])

# ------------------------end helper methods only -------------------


# ------------------------start before test methods only -------------------

    @classmethod
    def setUpClass(cls):
        print("Starting all the tests.")    
        mydata = '''AQT\tQAT\t1\t1505179232\tC\t
IQS\tQIS\t50\t1505179230\tC\t
'''
        f = open('mystuff.qz', 'w')
        f.write(mydata)
        f.close()
    
    def setUp(self):
        self.ginitialize()
        

# ------------------------end before test methods only -------------------

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

        self.assertEqual(expected, str(my_stdout))


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

        self.assertEqual(expected, str(my_stdout))


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
Mean solution age: 9 d
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
Mean solution age: 17430 d
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
Mean solution age: 8047 d
Oldest solution: never
''')
        self.ensureInputDataMakesStats(inputData, expectedStats)

# file writing

    def test_fileWriting(self):
        expected = "IQS"

        # reset global data
        self.ginitialize()

        # load starting sane data from .qz file
        DoRunQuiz([])
        self.assertEqual(expected, g.gQData[6])
        self.assertEqual("1505179230", g.gQData[9])

        # cheat a little by modifying a global variable:
        # the save program will only save if dirty for that
        # file is set
        g.gFileNum_Dirty[0] = 1
        
        # cheat an modify some data, so the written file differs
        g.gQData[9] = '1505100000'
        SaveData()
        
        self.ginitialize()
        DoRunQuiz([])
        self.assertEqual("1505100000", g.gQData[9])

    def test_MungeData(self):
        expected = "IQS"

        # reset global data
        self.ginitialize()

        # load starting sane data from .qz file
        shutil.copyfile('mystuff.qz.bkp', 'mystuff.qz')
        DoRunQuiz([])


        MungeData()
        #self.assertEqual("1505100000", g.gQData[9])

if __name__ == "__main__":
    #import syssys.argv = ['', 'Test.testName']
    unittest.main()