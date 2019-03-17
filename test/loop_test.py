l1 = [1, 2, 3]
l2 = [4, 5, 6]

while l1 or l2:
    if l1:
        print(l1.pop())
    else:
        print(l2.pop())
