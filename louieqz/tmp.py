import time
#import shutil


class Q():
    def __init__(self, *fields):
        '''
        Quiz question.

        fields are string

        Q(question, answer, rating, age, flags, note)

        when reading or writing age, flags, they are stored as int
            myq.rating = 22
            myq.age = 1504711252

            myint = myq.rating
            myint2 = myq.age

        '''

        field_names = 'question', 'answer', 'rating', 'age', 'flags', 'note'

        for field_name, field in zip(field_names, fields):
            setattr(self, field_name, field)

        self.rating = int(self.rating)
        self.age = int(self.age)

    def __repr__(self):
        '''
        Representation of the object.
        '''
        six_fields = "'{}', " * 6

        # strip off comma and space
        repr_template = '{}(' + six_fields[:-2] + ')'
        return(repr_template.format(self.__class__.__name__,
                                    self.question, self.answer, self.rating, self.age, self.flags, self.note))

    def __str__(self):
        '''
        String of all fields of this question, tab-separated.

        Suitable for writing to a text file, for example

        Each field is shown as a string, no quotes
        '''
        string_fields = [self.question, self.answer, str(
            self.rating), str(self.age), self.flags, self.note]
        return('\t'.join(string_fields))


class QList():
    '''
    A list of quiz questons generated with contents of a file.

    Each file line contains tab-delimited fields.

    QList('myfilename.ext')
    QList()  # defaults to fiveq.qz
    '''

    def __init__(self, file_name="fiveq.qz"):
        self._questions = []

        # Open file, split lines.
        # Create a question for each line consisting of split fields of line
        # Add question to _questions_, which is a list with members of type Q

        with open(file_name, 'r') as fin:
            lines_list = fin.read().splitlines()

        for line in lines_list:
            fields = line.split('\t')

            newq = Q(*fields)
            self._questions.append(newq)

    def __len__(self):
        return len(self._questions)

    def __getitem__(self, position):
        return self._questions[position]

    def write(self, file_name='fiveq.qz'):
        with open(file_name, 'w') as fout:
            for quest in self._questions:
                fout.write(str(quest) + '\n')


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

    # when testing, this creates the same initial .qz file
    # shutil.copyfile('/home/louie/Documents/prog/workspace2017o2/pythonquiz/louieqz/fiveq.qz.bkp',
    #                '/home/louie/Documents/prog/workspace2017o2/pythonquiz/louieqz/fiveq.qz')

    questions = QList()

    show_questions(questions, 'here they are')

    do_quiz(questions)

    show_questions(questions, 'Showing updated questions.')

    questions.write()


quiz()
