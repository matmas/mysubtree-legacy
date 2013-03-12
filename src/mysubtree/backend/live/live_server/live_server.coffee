#===================================================================
# CONFIG:
#-------------------------------------------------------------------
LISTEN_PORT = 8125
LISTEN_HOST = "127.0.0.1"
#===================================================================
net = require("net")
http = require('http')
_ = require("underscore")

clients_data = {}

http_server = http.createServer()
http_server.listen(3001, "0.0.0.0")

io = require("socket.io").listen(http_server)
Array::remove = (e) -> @[t..t] = [] if (t = @indexOf(e)) > -1 #http://stackoverflow.com/questions/4825812/clean-way-to-remove-element-from-javascript-array-with-jquery-coffeescript

io.configure( ->
    io.set("transports", [
        'websocket',
        'flashsocket',
        'htmlfile',
        'xhr-polling',
        'jsonp-polling',
    ])
    io.set("log level", 1)
)

io.sockets.on("connection", (socket) ->
    address = socket.handshake.address
    console.log("   info   - " + "client connected - #{address.address}:#{address.port}")
    client = clients_data[socket.id] = {
        "live_ids": [],
        "nodelists": [],
    }
    
    socket.on("watch", (live_ids) ->
        client.live_ids = client.live_ids.concat live_ids
    )
    
    socket.on("unwatch", (live_ids) ->
        for live_id in live_ids
            client.live_ids.remove(live_id) # just one, ignore possible duplicates
    )
    
    socket.on("watchnodelist", (nodelist) ->
        client.nodelists.push({"nparent": nodelist.nparent, "type": nodelist.type})
    )
    
    socket.on("unwatchnodelist", (nodelist) ->
        for other, i in client.nodelists
            if nodelist.nparent == other.nparent and nodelist.type == other.type
                client.nodelists.splice(i, 1) # remove this nodelist
                break
    )
    
    socket.on("user", (user) ->
        client.user = user
    )
    
    socket.on('disconnect', ->
        console.log("   info   - " + "client disconnected - #{address.address}:#{address.port}")
        delete clients_data[socket.id]
    )
)

receiver = (callback) ->
    server = net.createServer( (socket) ->
        incoming_msg = ""
        remaining_length = 0
        socket.on("data", (data) ->
            data = data.toString()
            if remaining_length <= 0
                incoming_msg = ""
                remaining_length = data.substring(0, data.indexOf("\n"))
                remainder = data.substring(data.indexOf("\n")+1)
                if remainder
                    incoming_msg += remainder
                    remaining_length -= remainder.length
            else
                incoming_msg += data
                remaining_length -= data.length
            if remaining_length <= 0
                response = "ok"
                socket.write(response.length + "\n" + response)
                callback(incoming_msg)
                incoming_msg = ""
        )
        socket.on("end", ->
            socket.end()
        )
    )

    server.on("error", (err) ->
        if err.code == 'EADDRINUSE'
            console.log("Address in use, exiting...")
            process.exit()
    )

    server.listen(LISTEN_PORT, LISTEN_HOST, () ->
        console.log("Live running...")
    )


emit_nonempty = (socket, event, array) ->
    if array.length > 0
        socket.emit(event, array)


receiver( (str) ->
    msg = JSON.parse(str)
    
    for socket_id, client of clients_data
        socket = io.sockets.sockets[socket_id]
        emit_nonempty(socket, "changed",     msg.changed.filter(     (id) -> id in client.live_ids ))
        emit_nonempty(socket, "disappeared", msg.disappeared.filter( (id) -> id in client.live_ids ))
        emit_nonempty(socket, "appeared",    msg.appeared.filter( (record) ->
            _.any(client.nodelists, (nodelist) ->
                record.nparent == nodelist.nparent and record.type == nodelist.type
            )
        ))
        if client.user in msg.notifications
            socket.emit("responses")
)



