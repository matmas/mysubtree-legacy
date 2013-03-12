$(document).ready( ->
  $.ajaxSetup({cache: false}) # fix Internet Explorer caching AJAX responses
)

$(document).ready( ->
    if $.browser.msie and $.browser.version < 8
        title = "Unsupported browser (Internet Explorer #{$.browser.version})"
        html = """
            <p>Your browser is too old and is not supported.</p>
            <p>
                Quick fix: <a href="http://www.google.com/chromeframe/eula.html?quickenable=true">install Google Chrome Frame plugin</a>
                and after the installation, close and start Internet Explorer again.
            </p>
            <small>
                For more information visit it's <a href="http://code.google.com/chrome/chromeframe/">homepage</a>.
            </small>
            <hr />
            <small>
                If you can, you should install a more modern browser, such as:
                <a href="http://www.firefox.com/">Mozilla Firefox</a>,
                <a href="http://www.google.com/chrome">Google Chrome</a>,
                <a href="http://www.apple.com/safari/">Safari</a>
                or recent version of <a href="http://www.microsoft.com/windows/internet-explorer/">Internet Explorer</a>.
            </small>
        """
        $("<div>#{html}</div>").appendTo($(document.body)).dialog({
            title: title,
            width: 800,
            height: 500,
            modal: true,
        })
)

init_ie = (container) ->
    $("p:first-of-type", container).addClass("first-of-type")
    $("p:last-of-type", container).addClass("last-of-type")

$(document).ready( ->
    init_ie($(document))
)

$(document).on("ajax", (event, container) ->
    init_ie(container)
)