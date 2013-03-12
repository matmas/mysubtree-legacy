# if typeof String.prototype.startsWith != 'function'
#     String.prototype.startsWith = (str) ->
#         return this.slice(0, str.length) == str

# replaceHtml = (container, response) ->
# #     if response.startsWith("<td")
# #         temp = $("<div></div>").html(response)
# #         container.children().each( ->
# #             class_ = $(this).attr("class")
# #             td = temp.children("td.#{class_}").html()
# #             $(this).html(td)
# #         )
# #     else
#     container.html(response)

window.utils = window.utils or {}
utils = window.utils

utils.stripQueryString = (url) ->
    return url.split("?", 1)[0]

utils.ajax = (container, href, callback) ->
    loadingHtml = '<div class="loading" title="loading..." />'
    if container.is("tr")
        loading = $("<td>#{loadingHtml}</td>")
    else
        loading = $("#{loadingHtml}")
    loading.appendTo(container).hide()
    setTimeout( ->
        loading.show()
    , 250) # 0 to debug

    setTimeout( ->
        $.get(href, (response) ->
            container.html(response)
            if typeof(callback) == "function"
                callback(container)
            $(document).trigger("ajax", [container, href])
        ).error( ->
            container.empty()
        )
    , 0) # 500 to debug

utils.messageBox = (title, html, options={}) ->
    dialog = $("<div>#{html}</div>")
    settings = {
        title: title,
        width: "auto",
        modal: true,
        close: (event, ui) ->
#             event.preventDefault()
#             console.log(dialog)
#             console.log(event)
#             console.log(ui)
            # remove div with all data and events
#             dialog.remove() # TODO: prevent cluttering <body> with leftover closed dialogs without hampering multi-dialog possibilities
    }
    $.extend(settings, options)
    dialog.appendTo($(document.body)).dialog(settings)
    return dialog

utils.clearTextSelection = ->
    selection = if window.getSelection then window.getSelection() else document.selection
    if selection
        if selection.removeAllRanges
            selection.removeAllRanges()
        else
            selection.empty()

utils.raising_effect = (element) ->
    return element.clone()
        .appendTo($(document.body))
        .css({
            position: "absolute",
            top: element.offset().top,
            left: element.offset().left
        })
        .animate(
            {
                top: "-=50px",
                opacity: 0
            }, 1000, -> $(this).remove()
        )

utils.getCSS = (selector) ->
    style = null
    for stylesheet in document.styleSheets
        rules = stylesheet.cssRules or stylesheet.rules
        if rules != null
            for rule in rules
                if rule.selectorText and rule.selectorText.toLowerCase() == selector.toLowerCase() # IE has html tags in uppercase, but not class names (tested with IE8)
                    style = rule.style
    return style

cachedStyles = {}

utils.setCSS = (selector, ruleText) ->
    createStyle = (selector, ruleText) ->
        stylesheet = document.styleSheets[0]
        rules = stylesheet.cssRules or stylesheet.rules
        if stylesheet.insertRule != undefined
            stylesheet.insertRule("#{selector} { #{ruleText} }", rules.length)
        else
            stylesheet.addRule(selector, ruleText, rules.length)
        return rules[rules.length-1].style
    if not cachedStyles[selector]
        cachedStyles[selector] = createStyle(selector, ruleText)
    cachedStyles[selector].cssText = ruleText
    return cachedStyles[selector]

utils.load = (key) ->
    return try localStorage[key] catch error

utils.save = (value, key) ->
    try localStorage[key] = value catch error

utils.get_options = (select) ->
    options = []
    $.each($(select).children("option"), (index, option) ->
        options.push(option.value)
    )
    return options

utils.focus_form = (context) ->
    input = $("form :input:visible:enabled:first", context).focus()
    defaultText = input.val()
    input.val("").val(defaultText) # move text cursor to the end