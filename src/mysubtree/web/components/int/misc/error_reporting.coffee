#= require common
utils = window.utils

$.ajaxSetup({
    timeout: 30000,
})

# AJAX error handling:
$(document).ajaxError( (event, jqXHR, ajaxSettings, exception) ->
    message = "#{jqXHR.status} (#{jqXHR.statusText})"
    if jqXHR.status == 0
        message = conn_failed_msg or "Unable to connect to the server. Check your internet connection."
    if exception == "timeout"
        message = "Timeout."
    else if exception == "parsererror"
        message = "JSON parse error."
    else if exception == "abort"
        message = "Aborted."
    utils.messageBox(error_msg or "error", """
    <p>
        #{message}
    </p>
    <p>
        #{jqXHR.responseText}
    </p>
    <p>
        <b>URL:</b>
        #{ajaxSettings.url}
    </p>
    """)
)
