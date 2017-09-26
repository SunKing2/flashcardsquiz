'''
Created on Sep 25, 2017

@author: louie
'''

from flashcardsquiz.myrunner import MyRunner
import time
import shutil

# start helper methods


def console_run_with_capture(expected, time_in_expected_run, responses_file):
    myrunner = MyRunner()
    shutil.copy('fiveq.qz.bkp', 'fiveq.qz')
    results = myrunner.run_with_input_from_file(
        args='quiz.py', input_file=responses_file)

    time_of_run = str(int(time.time()))

    expected = expected.replace(time_in_expected_run, time_of_run)
    print('======================')
    print(expected)
    print('2======================')
    print(results)
    print('3======================')

    return expected, results
# end helper methods


def test_run_all_cr():
    expected = '''here they are  
HOP 71 1504097032
BLO 33 1504711252
EGHU 67 1503419418
EEGH 45 1503750431
AEINOST 24 1504796064
  
Starting do_quiz_with_files.  
[1]HOP:wrong, actual answer is: HOP PHO POH  
[1]BLO:wrong, actual answer is: LOB  
[1]EGHU:wrong, actual answer is: HUGE  
[1]EEGH:wrong, actual answer is: GHEE  
[1]AEINOST:wrong, actual answer is: ATONIES  
  
Showing updated questions.  
HOP 100 1506381473
BLO 100 1506381473
EGHU 100 1506381473
EEGH 100 1506381473
AEINOST 100 1506381473
  
'''

    (expected, results) = console_run_with_capture(
        expected, '1506381473', 'input.dat')
    assert(expected == results)


def test_run_all_correct():
    expected = '''here they are  
HOP 71 1504097032
BLO 33 1504711252
EGHU 67 1503419418
EEGH 45 1503750431
AEINOST 24 1504796064
  
Starting do_quiz_with_files.  
[1]HOP:correct  
HOP	HOP PHO POH	71	1504097032	CO	  
HOP	HOP PHO POH	47	1506387777	CO	  
[1]BLO:correct  
BLO	LOB	33	1504711252	CO	  
BLO	LOB	22	1506387777	CO	  
[1]EGHU:correct  
EGHU	HUGE	67	1503419418	CO	  
EGHU	HUGE	45	1506387777	CO	  
[1]EEGH:correct  
EEGH	GHEE	45	1503750431	CO	  
EEGH	GHEE	30	1506387777	CO	  
[1]AEINOST:correct  
AEINOST	ATONIES	24	1504796064	CO	  
AEINOST	ATONIES	16	1506387777	CO	  
  
Showing updated questions.  
HOP 47 1506387777
BLO 22 1506387777
EGHU 45 1506387777
EEGH 30 1506387777
AEINOST 16 1506387777
  
'''

    (expected, results) = console_run_with_capture(
        expected, '1506387777', 'input_correct.dat')
    assert(expected == results)
