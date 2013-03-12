#= require common

Node.prototype.permalinkHref = ->
    return this.inside().permalink().$.attr("href")
