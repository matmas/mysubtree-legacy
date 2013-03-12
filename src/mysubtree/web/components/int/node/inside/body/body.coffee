#= require int/node/node

$(document).ready( ->
    $(".less").show()
)

$(document).on("ajax", (container) ->
    $(".less").show()
)

$(document).on("click", "a.more", (event) ->
    event.preventDefault()
    body = $(this).closest(".body")
    teaser = body.children(".teaser")
    full_version = body.children(".full-version")
    
    teaser.hide()
    full_version.show()
)

$(document).on("click", ".less", (event) ->
    event.preventDefault()
    body = $(this).closest(".body")
    teaser = body.children(".teaser")
    full_version = body.children(".full-version")
    
    full_version.hide()
    teaser.show()
)
