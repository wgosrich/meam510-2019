from UIUtility import _Getch as getch

keyInput = getch()
print("Enter:")
k = keyInput()
print(str(k))
if k == b'q':
    print(True)
