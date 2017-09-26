# qz-python


pytest has to be run from the command line (I can't get it to work in Eclipse, because it's running it in the project's directory and it is trying to write and read files that are in the package directory below it:


cd flashcardsquiz

py.test test*.py

lint the main program:


pylint -rn  quiz.py


The rest of this document is for my own memory:

to generate the quiz data, and paste it into the test*.py files, I had to do the pasting using mousepad (not pydev, because it changes tabs to spaces), and I used this:


cp fiveq.qz.bkp  fiveq.qz; python quiz.py < input_correct.dat


also input.dat for 5 wrong answers (really 5 carriage returns)

