from flask import escape
import socket
import sys
import re

class MarkdownClient():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected = False

    def connect(self):
        assert not self.connected
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
        except socket.error, error:
            if error.errno == 111: # Connection refused, server not running
                self.connected = False
            else:
                raise error
        return self.connected
    
    def get_html(self, input):
        return self._markdown_js(escape(input))
    
    #def strip_unnecessary_p_tags(self, html):
        #p_tags = re.compile("(<p>|</p>)")
        #if len(p_tags.findall(html)) == 2:
            #html = p_tags.sub("", html)
        #return html
    
    def _markdown_js(self, input):
        buffer_len = 40960
        self.sock.sendall("%d\n%s" % (len(input), input.encode('utf-8')))
        buffer = self.sock.recv(buffer_len)
        if len(buffer) == 0: # connection to server lost
            self.connected = False
            raise ConnectionLostException()

        length, string = buffer.split("\n", 1)
        remaining_length = int(length) - len(string)

        while remaining_length > 0:
            data = self.sock.recv(buffer_len)
            string += data
            remaining_length -= len(data)
        return string
    
    def close(self):
        self.sock.close()

class ConnectionLostException(Exception):
    pass
