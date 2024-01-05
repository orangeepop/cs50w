li = ['CSS', 'Django', 'Git', 'HTML', 'Python']
query = 'cs'

for i in li:
    if query.lower() not in i.lower():
        li.remove(i)
    print(1)
print(li)