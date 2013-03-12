#= require common

Node.prototype.getNid = ->
    return this.inside().$[0].id 
