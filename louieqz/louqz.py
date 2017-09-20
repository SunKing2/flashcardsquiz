'''
Created on Sep 20, 2017

@author: louie
'''
def ask_all(questions):
    for question in questions:
        response = input(question + ":")
        if (response.lower() == questions[question].lower()):
            print('yep')
        else:
            print('nope')

def do_it():
    with open('twolines.qz', 'r') as fin:
        lines_list = fin.read().splitlines()
    
    questions = {}    
    for line in lines_list:
        fields = line.split('\t')
        print('alphagram=' + fields[0])
    
        questions[fields[0]] = fields[1]
    
    ask_all(questions)  

if __name__ == '__main__':
    do_it()