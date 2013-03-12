window.mysubtree = window.mysubtree or {}
mysubtree = window.mysubtree

mysubtree.getCurrentUser = ->
    $("#account > .user").data("user")+""