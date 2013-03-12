# Working:
from mysubtree.tests.root import Root
from mysubtree.tests.account import Account
from mysubtree.tests.longbreadcrumb import LongBreadcrumb
from mysubtree.tests.adding import Adding
from mysubtree.tests.renaming import Renaming
from mysubtree.tests.unread_notifications import UnreadNotifications
from mysubtree.tests.moving import Moving #TODO: test log entries
from mysubtree.tests.cycles import Cycles
from mysubtree.tests.decrementer import Decrementer
from mysubtree.tests.voting import Voting
from mysubtree.tests.editing import Editing
from mysubtree.tests.deleting import Deleting
from mysubtree.tests.paging import Paging
#from mysubtree.tests.icons import Icons

# Not yet complete:
from mysubtree.tests.flagging import Flagging
#TODO: test activity


#TODO: test sorting

import unittest
if __name__ == '__main__':
    unittest.main()
