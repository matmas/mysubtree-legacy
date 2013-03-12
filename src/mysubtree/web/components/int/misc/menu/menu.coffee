initMenus = (container) ->
    links = $(".menu", container)
    menus = $(".menu ul", container)
    
    menus
        .css({visibility: "visible"}) # otherwise it will hide on mouseout automatically because of fallback css rules
        .hide()
    links.click( ->
        menu = $(this).find("ul")
        visible = menu.is(":visible")
        menus.hide()
        if visible
            menu.hide()
        else
            menu.show()
        
    ).hover( ->
        $(this).css("cursor", "pointer")
        window.clearTimeout(this.closeTimer)
    , -> # mouse out
        menu = $(this).find("ul")
        this.closeTimer = window.setTimeout( ->
            menu.hide()
        , 250)
    )
    
    container.on("click", (event) ->
        target = event.target or event.srcElement
        if not (target in links)
            menus.hide()
    )

$(document).ready( ->
    initMenus($(document))
)

$(document).on("ajax", (event, container) ->
    initMenus(container)
)

$(document).on("click", ".menu ul a", "click", (event) ->
    $(this).closest(".menu ul").hide()
)
