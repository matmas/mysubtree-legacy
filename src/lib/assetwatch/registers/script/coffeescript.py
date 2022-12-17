from lib.check_output import check_output
from subprocess import CalledProcessError
import subprocess


def convert_to_javascript(filename):
    coffee_with_args = ["coffee", "--print", "--compile", "--bare", filename]
    try:
        javascript = check_output(coffee_with_args, stderr=subprocess.PIPE)
        return javascript
    except CalledProcessError:
        error_output = check_output(" ".join(coffee_with_args) + "; exit 0", shell=True, stderr=subprocess.STDOUT)
        output = """
        message_box = function(title, text) {
            if (typeof(jQuery) === 'function' && typeof($().dialog) == 'function') {
                jQuery(function() {
                    jQuery("<pre style=\\"font-size: 100%%;\\">" + text + "</pre>").appendTo(jQuery(document.body)).dialog({
                        title: title,
                        width: "auto",
                        modal: true,
                    });
                });
            }
            else {
                alert(title + "\\n" + text);
            }
        }
        message_box('CoffeeScript error:', %s);
        """ % " + \n".join("'%s\\n'" % line for line in error_output.replace("'", r"\x27").split("\n"))
        return output

