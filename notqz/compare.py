#not used.  it's kept here so i can refer to it when 
# making a real comparator
def make_comparator(less_than):
    def compare(x, y):
        if less_than(x, y):
            return -1
        elif less_than(y, x):
            return 1
        else:
            return 0
    return compare

subjects = ['k', 'a', 'x', 'b', 'z', 'y']

#sortedDict = sorted(subjects, cmp=make_comparator(cmpValue), reverse=True)

def my_comparison_function(a, b):
    if (a.lower() < b.lower()):
        return -1
    if (a.lower() == b.lower()):
        return 0
    return 1

from functools import  cmp_to_key 

mylets =  ['k', 'a', 'x', 'b', 'z', 'y']
print (mylets)

sorted(mylets, key=cmp_to_key(my_comparison_function))

print (mylets)

