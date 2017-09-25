'''
Reads .qz file, prompts user using data from each line, write .qz file
'''
import time


def mylog(arg1, arg2='', arg3=''):
    '''
    Output, using same format as print(), but intended for log stuff
    '''
    print(arg1, arg2, arg3)


def conout(arg1, arg2='', arg3=''):
    '''
    Output, using same format as print(), but intended for console output stuff
    '''
    print(arg1, arg2, arg3)


class _QuizQuestion():
    def __init__(self, question, answer, rating, age):
        '''
        Quiz question.

        fields are string

        Q(question, answer, rating, age)

        when reading or writing rating, age, they are stored as int
            myq.rating = 22
            myq.age = 1504711252

            myint = myq.rating
            myint2 = myq.age

        '''
        self.question = question
        self.answer = answer
        self.rating = int(rating)
        self.age = int(age)
        self.flags = 'CO'
        self.note = ''

    def __repr__(self):
        '''
        Representation of the object.
        '''
        six_fields = "'{}', " * 6

        # strip off comma and space
        repr_template = '{}(' + six_fields[:-2] + ')'
        return(repr_template.format(self.__class__.__name__,
                                    self.question, self.answer, self.rating,
                                    self.age, self.flags, self.note))

    def __str__(self):
        '''
        String of all fields of this question, tab-separated.

        Suitable for writing to a text file, for example

        Each field is shown as a string, no quotes
        '''
        string_fields = [self.question, self.answer, str(
            self.rating), str(self.age), self.flags, self.note]
        return '\t'.join(string_fields)


class QList():
    '''
    A list of do_quiz_with_files questons generated with contents of a file.

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

            # the file has 2 more fields in it, that we ignore
            # this is because the _QuizQuestion() won't take them
            newq = _QuizQuestion(*(fields[:4]))
            self._questions.append(newq)

    def __len__(self):
        return len(self._questions)

    def __getitem__(self, position):
        return self._questions[position]

    def write(self, file_name='fiveq.qz'):
        '''
        Write, as text, a line for each question in this object.

        Fields are written delimited by tabs.
        '''
        with open(file_name, 'w') as fout:
            for quest in self._questions:
                fout.write(str(quest) + '\n')


class Quiz():
    '''
    Retrieve existing quiz questions, ask all questions, write.
    '''

    def show_questions(self, questions, log_message):
        '''
        Debugging, log all the questions in this object, one per line
        '''
        mylog(log_message)
        for quest in questions:
            mylog(quest.question, quest.rating, quest.age)
        mylog('')

    def do_quiz_with_questions(self, questions):
        '''
        Using data from questions, prompt user once per question.

        Does not read data or write it.  Data gets modified in questions object.
        '''
        mylog('Starting do_quiz_with_files.')
        for quest in questions:
            response = input('[%d]%s:' % (1, quest.question))
            now = int(time.time())
            if response.lower() == quest.answer.lower():
                conout('correct')
                conout(quest)
                quest.rating = int((1 + 2 * quest.rating) / 3)
                quest.age = now
                conout(quest)
            else:
                conout('wrong, actual answer is: %s' % quest.answer)
                quest.rating = 100
                quest.age = now

        mylog('')

    def do_quiz_with_files(self):
        '''
        Reads .qz file, prompts user using data from each line, write .qz file
        '''

        questions = QList()

        self.show_questions(questions, 'here they are')

        self.do_quiz_with_questions(questions)

        self.show_questions(questions, 'Showing updated questions.')

        questions.write()


if __name__ == '__main__':
    Quiz().do_quiz_with_files()
