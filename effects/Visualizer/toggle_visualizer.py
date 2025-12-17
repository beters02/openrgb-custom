import socket
socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(b"toggle_visualizer", ("127.0.0.1", 50555))