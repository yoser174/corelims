"""Module tes simulate raw data end from BW300."""
import socket

STX = b"\x02"
ETX = b"\x03"
LF = b"\x0A"
CR = b"\x0D"
CRLF = CR + LF


def client_program():
    """client program main"""
    host = socket.gethostname()
    port = 5050
    client_socket = socket.socket()
    client_socket.connect((host, port))

    message = (
        STX.decode()
        + """DATE:2023-08-17 17:12
NO.:90000
ID :
 ORU         +- 3.3 umol/L
 BIL         -0  umol/L
"""
        + ETX.decode()
    )
    message_part1 = (
        STX.decode()
        + """DATE:2023-08-17 17:12
NO.:90000
"""
    )
    message_part2 = (
        """ID :
 ORU         +- 3.3 umol/L
 BIL         -0  umol/L
"""
        + ETX.decode()
    )
    client_socket.send(message_part1.encode())
    client_socket.send(message_part2.encode())
    client_socket.close()


if __name__ == "__main__":
    client_program()
