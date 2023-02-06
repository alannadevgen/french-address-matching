import re
o = re.match("[0-9]{1,4}", "22")
print(o)

test = re.sub('[/_\\.,;:\\-\'\\(\\)!\\?"]', " ",  '0/2 ! ?')
print(test)

t = re.match(".*[A-Z]+.*", "19N4")
print(t)

ex = '1965'
print(not ex.isdigit())

print(sum([1,2,2]))
list_index = [0,1,2,3]
print(sum(list_index) == (len(list_index) * (len(list_index)-1))/2)