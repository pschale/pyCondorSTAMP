with open('pyCondorSTAMPLib_V3.py','r') as infile:
    data = [line for line in infile]

with open('pyCondorSTAMPLib_V4.py','r') as infile:
    data2 = [line for line in infile]

dif1 = [x for x in data if x not in data2]
dif2 = [x for x in data2 if x not in data]

print(len(dif1))
print(len(dif2))

dif3 = [x for index, x in enumerate(data) if x != data2[index]]

print(dif3)