//===================================================================
// CONFIG:
//-------------------------------------------------------------------
var showdown_path = "../../mysubtree/web/components/ext/wmd/showdown.js"
var LISTEN_PORT = 8124
var LISTEN_HOST = "127.0.0.1"

//===================================================================
var fs = require("fs");
var net = require("net");

eval(fs.readFileSync(__dirname + "/" + showdown_path).toString())
var converter = new Showdown.converter();

var server = net.createServer(function (socket) {
    var text = "";
    var remaining_length = 0;
    socket.on("data", function (data) {
        var data = data.toString();
        if (remaining_length <= 0) {
            text = ""
            remaining_length = data.substring(0, data.indexOf("\n"))
            remainder = data.substring(data.indexOf("\n")+1)
            if (remainder) {
                text += remainder
                remaining_length -= remainder.length
            }
        }
        else {
            text += data
            remaining_length -= data.length
        }
        if (remaining_length <= 0) {
            var html = converter.makeHtml(text)
            socket.write(html.length + "\n" + html);
            text = "";
        }
    });
    socket.on("end", function () {
        socket.end();
    });
})

server.on("error", function(err) {
    if (err.code == 'EADDRINUSE') {
        // console.log("Address in use, exiting...");
        process.exit();
    }
});

server.listen(LISTEN_PORT, LISTEN_HOST, function() {
    // console.log("Markdown running...");
});
