#= require common

Node.prototype.parentNode = ->
    return new Node(this.$.parent())

Node.prototype.exists = ->
    return this.$.length >= 1
    
Node.prototype.parentNodes = ->
    parentNodes = []
    node = this.parentNode()
    while node.exists()
        parentNodes.push(node)
        node = node.parentNode()
    return parentNodes


init_unread = (container) ->
    $(".reading", container).effect("highlight", {}, 2000)

$(document).ready( ->
    init_unread($(document))
)

$(document).on("ajax", (event, container) ->
    init_unread(container)
)