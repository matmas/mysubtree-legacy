#= require common
#= require prettify

$(document).ready( ->
    prettyPrint()
)

$(document).on("ajax", (event, container) ->
    prettyPrint()
)