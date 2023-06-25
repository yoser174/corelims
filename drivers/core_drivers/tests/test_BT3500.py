
import socket

BUFFER_SIZE = 1024
STX = b'\x02'
ETX = b'\x03'
EOT = b'\x04'
ENQ = b'\x05'
ACK = b'\x06'
NAK = b'\x15'
ETB = b'\x17'
LF  = b'\x0A'
CR  = b'\x0D'

host = '192.168.184.140'
port = 8888

print 'starting TCP server [%s:%s] ...' % (host,port)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port ))
s.listen(1)
conn, addr = s.accept()
print 'Connection address [%s]' % str(addr)


def  make_checksum(message):
    if not isinstance(message[0], int):
        message = map(ord, message)
    return str(int(hex(sum(message) & 0xFF)[2:].upper().zfill(2).encode(),16)).zfill(3)

msg = ''
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    print "data [%s]" % data
    if data == STX:
        conn.send(ACK)
    elif data == 'R':
        #conn.send(ACK)
        print 'R'
    elif data == EOT:
        #conn.send(ACK)
        print "proses data [%s]" % msg
        print 
        print make_checksum(msg[:-3])
        conn.send('Y01')
        msg = ''
        #print '>> STX'
        #conn.send(STX)
        #tmp_data = conn.recv(BUFFER_SIZE)
        #if tmp_data == ACK:
        #    print '<< ACK'
        #    conn.send('Y01')
        #    tmp_data = conn.recv(BUFFER_SIZE)
        #    if tmp_data == ACK:
        #        conn.send(EOT)
            
        
    else:
        msg = msg + data
