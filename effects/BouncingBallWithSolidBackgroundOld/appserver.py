import socket

class OpenRGBCustomServer:
    def __init__(self, port=50556):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        self.sock.setblocking(False)

    def update(self, cfghelper):
        self.poll_commands(cfghelper)

    def poll_commands(self, cfghelper):
        """Non-blocking UDP command handler."""
        try:
            data, addr = self.sock.recvfrom(1024)
            cmd = data.decode().strip()

            if cmd == "json_reload":
                cfghelper.parson_json()

        except BlockingIOError:
            pass