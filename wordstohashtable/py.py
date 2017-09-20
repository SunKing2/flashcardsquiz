with open('words.dat', 'r') as infile:
    k = infile.read().splitlines()


def alpha(word):
    return ''.join(sorted(word))

myhash = {}
for word in k:
    alphagram = ''.join(sorted(word))
    curr = myhash.get(alphagram, [])
    #if (curr) : curr += ' '
    myhash[alphagram] = curr + [word]

let_vals = [1,3,3,2,1,4,2,4,1,8,5,1,3,1,1,3,10,1,1,1,1,4,4,8,4,10]

h_final = {''.join(sorted(word)):[myhash[''.join(sorted(word))], sum([let_vals[ord(let) - ord('a')] for let in word])] for word in k}

print (h_final)
