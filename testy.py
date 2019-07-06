import timeit
from timecomp import create_base
from test import Skeleton
g, ml=create_base(2)
print(ml)
Skeleton(g, ml)
print(timeit.timeit(setup="from __main__ import create_base\nfrom test import Skeleton\ng, ml=create_base({})\nprint(ml)".format(4), stmt="Skeleton(g, ml)", number=1))
