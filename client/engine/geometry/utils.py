def orient(a, b, c):

    "Determines the position of point c relative to the directed line\
    formed by points a and b.\
    If the return value is greater than 0, point c is to its left,\
    if less than 0, it is to the right,\
    and 0 means it is located on the line."

    return a.x*(b.y - c.y) - a.y*(b.x - c.x) + b.x*c.y - b.y*c.x
