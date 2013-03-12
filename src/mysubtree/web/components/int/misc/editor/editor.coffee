#= require common

utils = window.utils

$(document).ready( ->
    $(document).on("wmd-ready", (event, wmdEditor) ->
        $(".wmd-help-button").children("a").on("click", (event) ->
            event.preventDefault()
            url = this.href
            container = $("<div></div>")
            container.load(url, ->
                utils.messageBox("Markdown editing help", container.html())
            )
        )
    )
)