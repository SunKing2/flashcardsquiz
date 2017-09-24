from collections import namedtuple
import csv
import time


class Q():
    def __init__(self, question, answer, rating, age, flags, note):
        self.question = question
        self.answer = answer
        self.rating = rating
        self.age = age
        self.flags = flags
        self.note = note

    def __repr__(self):
        '''Returns representation of the object'''
        return("{}('{} {} {}')".format(self.__class__.__name__, self.question, self.rating, self.age))


class QList():
    def __init__(self, file_name="fiveq.qz"):
        Question = namedtuple(
            'Question', 'question, answer, rating, age, flags, note')
        f = open(file_name)
        qs = map(Question._make, csv.reader(f, delimiter='\t'))
        qx = [Question(q.question, q.answer, int(q.rating),
                       int(q.age), q.flags, q.note) for q in qs]
        self._questions = [Q(q.question, q.answer, q.rating,
                             q.age, q.flags, q.note) for q in qx]

    def __len__(self):
        return len(self._questions)

    def __getitem__(self, position):
        return self._questions[position]


def mylog(s1, s2='', s3=''):
    print(s1, s2, s3)


def conout(s1, s2='', s3=''):
    print(s1, s2, s3)


def show_questions(questions, log_message):
    mylog(log_message)
    for q in questions:
        mylog(q.question, q.rating, q.age)
    mylog('')


def do_quiz(questions):
    mylog('Starting quiz.')
    for q in questions:
        response = input('[%d]%s:' % (1, q.question))
        now = int(time.time())
        if (response.lower() == q.answer.lower()):
            conout('correct')
            conout(q)
            q.rating = int((1 + 2 * q.rating) / 3)
            q.age = now
            conout(q)
        else:
            conout('wrong, actual answer is: %s' % q.answer)
            q.rating = 100
            q.age = now

    mylog('')


def quiz():
    questions = QList()

    show_questions(questions, 'here they are')

    do_quiz(questions)

    show_questions(questions, 'Showing updated questions.')


quiz()
