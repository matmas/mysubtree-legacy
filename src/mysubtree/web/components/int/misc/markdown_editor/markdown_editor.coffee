jQuery.fn.extend({
    insertAtCaret: (myValue) ->
        return this.each((i) ->
            if document.selection
                # For browsers like Internet Explorer
                this.focus()
                sel = document.selection.createRange()
                sel.text = myValue
                this.focus()
            else if this.selectionStart
                # For browsers like Firefox and Webkit based
                startPos = this.selectionStart
                endPos = this.selectionEnd
                scrollTop = this.scrollTop
                this.value = this.value.substring(0, startPos) + myValue + this.value.substring(endPos, this.value.length)
                this.focus()
                this.selectionStart = startPos + myValue.length
                this.selectionEnd = startPos + myValue.length
                this.scrollTop = scrollTop
            else
                this.value += myValue
                this.focus()
        )
})


$(document).on("click", ".mde-buttons > .strong", ->
    buttons = $(this).closest(".mde-buttons")
    textarea = buttons.parent().children(".mde-textarea")
    
#     if textarea.isSelection
    textarea.insertAtCaret("text")
)