def button(x: int):
    return 1 << (x - 1)


LEFT = 1
MIDDLE = 2
RIGHT = 3
X1 = 4
X2 = 5
LMASK = button(LEFT)
MMASK = button(MIDDLE)
RMASK = button(RIGHT)
X1MASK = button(X1)
X2MASK = button(X2)
