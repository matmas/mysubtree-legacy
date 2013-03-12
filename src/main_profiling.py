from main_testing import *
import unittest
import cProfile

if __name__ == '__main__':
    command = "unittest.main()"
    cProfile.runctx(command, globals(), locals(), filename="mysubtree.profile")
