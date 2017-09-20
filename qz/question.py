'''
Created on Sep 17, 2017

@author: louie
'''

import json

class Question(object):

    question = 'abd'
    answer = ['bad', 'dab']
    rating = 67 
    def __init__(self, answer):
        self.question = ''.join(sorted(self.answer[0]))
        self.answer = answer.split(' ')
        self.rating = 67
        self.age = 0
        self.flags = 'C'
        self.note = ''


question = Question("dog god")
jsondata=json.dumps(question.__dict__)
print ("objects serialized: " + jsondata)

