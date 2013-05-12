$(document).ready( ->
    form = $('form.ajax_validate')
    if form
        $("input[type=text], input[type=password], input[type=email], input[type=checkbox]", form).on("blur", (event) ->
            if $(this).val() != "" and $()
                controls = $(this).closest(".controls")
                control_group = $(this).closest(".control-group")
                if this.name
                    $.ajax({
                        type: "POST",
                        url: form.attr("action"),
                        data: form.serialize() + "&validate_field=#{this.name}"
                        success: (response, textStatus, jqXHR) ->
                            
                            # remove any ul.errors
                            previous_errors = controls.find("ul.errors")
                            if previous_errors.length != 0
                                previous_errors.remove()
                            
                            # ensure help-inline:
                            help_inline = controls.find(".help-inline")
                            if help_inline.length == 0
                                help_inline = $("""<span class="help-inline"></span>""").appendTo(controls)
                            
                            # ensure validation-result:
                            validation_result = help_inline.find(".validation-result")
                            if validation_result.length == 0
                                validation_result = $("""<span class="validation-result"></span>""").appendTo(help_inline)
                            
                            validation_result.html(response)
                            
                            if validation_result.find(".errors").length == 0
                                control_group.removeClass("error")
                                control_group.addClass("success")
                            else
                                control_group.removeClass("success")
                                control_group.addClass("error")
                    })
        )
#         $("input[type=password]", form).on("keyup", (event) ->
#             strength = 0
#             regexps = [
#                 /[a-z]+/,        # contains lowercase characters
#                 /[0-9]+/,        # contains digits
#                 /[A-Z]+/,        # contains uppercase characters
#                 /[^A-Za-z0-9]+/, # contains special characters
#             ]
#             if this.value.length >= 8
#                 strength++       # length 8 characters or more
#             for regexp in regexps
#                 if this.value.match(regexp)
#                     strength++
#             console.log(strength)
#         )
)