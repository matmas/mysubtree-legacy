from collections import OrderedDict
from flask import request
from mysubtree.backend import common
from mysubtree.backend.models.node.types.all import get_model

all_sort_types = ["newest", "1day", "1week", "1month", "1year", "alltime"] #, "activity"] # disabled activity for now until there is a non-confusing way to present it to the users
default_sort_type = "newest"

def get_sort_types(node, branching_type):
    node_count = node.count(branching_type)
    
    if node_count <= 1:
        return [default_sort_type]
    
    sort_types = all_sort_types[:]
    sum_properties = OrderedDict([
        ("1day", "votes_sum_%s_d" % branching_type),
        ("1week", "votes_sum_%s_w" % branching_type),
        ("1month", "votes_sum_%s_m" % branching_type),
        ("1year", "votes_sum_%s_y" % branching_type),
        ("alltime", "votes_sum_%s_a" % branching_type),
    ])
    last_sum = 0
    for sort_type, sum_property in sum_properties.items():
        if last_sum == getattr(node, sum_property):
            sort_types.remove(sort_type)
        last_sum = getattr(node, sum_property)
    #if node.count_of_active_grandchildren == 0: # this method is probably not enough, so disabling activity sort for now...
        #sort_types.remove("activity")
    
    return sort_types
    
def correct_sort_type_of_subnodes(sort, node, branching_type):
    if sort not in get_sort_types(node, branching_type):
        return default_sort_type
    return sort

def correct_sort_type(sort):
    if sort not in all_sort_types:
        return default_sort_type
    return sort
