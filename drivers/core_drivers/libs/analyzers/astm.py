
import logging
import socket
import time
import sys

# reload(sys)  
# sys.setdefaultencoding('ISO-8859-1')


ENCODING = 'latin-1'
NULL = b'\x00'
STX = b'\x02'
ETX = b'\x03'
EOT = b'\x04'
ENQ = b'\x05'
ACK = b'\x06'
NAK = b'\x15'
ETB = b'\x17'
LF  = b'\x0A'
CR  = b'\x0D'
CRLF = CR + LF
VT = b'\x0B'
FS = b'\x1C'
RECORD_SEP    = b'\x0D' # \r #
FIELD_SEP     = b'\x7C' # |  #
REPEAT_SEP    = b'\x5C' # \  #
COMPONENT_SEP = b'\x5E' # ^  #
ESCAPE_SEP    = b'\x26' # &  #

VERSION = '0.0.0.2'

BUFFER_SIZE = 1024
SOCKET_TIMEOUT = 5

class astm(object):
    def __init__(self,conn_type,tcp_conn_type,tcp_host,tcp_port):
        logging.info('astm version [%s]' % VERSION)
        self.connection_type = conn_type
        self.tcp_conn_type = tcp_conn_type
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        logging.info('astm init connection type [%s]' % self.connection_type)

        # fix 
        if self.tcp_conn_type == 'S':
             self.tcp_host = '0.0.0.0'

        if self.tcp_conn_type == 'S':
            logging.info('Connection is Server [%s:%s], open socket...' % (self.tcp_host,self.tcp_port))
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.tcp_host, self.tcp_port))
            self.s.listen(1)
            logging.info('Ok')
            self.conn, self.addr = self.s.accept()
            logging.info('Connection address: [%s]', self.addr)

        elif self.tcp_conn_type == 'C':
            logging.info('Connection is Client.')
            logging.info('trying to make connection to [%s:%s] ...' % (str(self.tcp_host), str(self.tcp_port)))
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.settimeout(SOCKET_TIMEOUT)
                self.conn.connect((self.tcp_host, self.tcp_port))
            except Exception as e:
                logging.error('Failed [%s]' % str(e))
                sys.exit(0)

    

    def  make_checksum(self,message):
        if not isinstance(message[0], int):
            message = map(ord, message)
        return hex(sum(message) & 0xFF)[2:].upper().zfill(2).encode()

    def checksum_verify(self,message):
        if not (message.startswith(STX) and message.endswith(CRLF)):
            logging.error('Malformed ASTM message. Expected that it will started'
                         ' with %x and followed by %x%x characters. Got: %r'
                         ' ' % (ord(STX), ord(CR), ord(LF), message))
            return False
        stx, frame_cs = message[0], message[1:-2]
        frame, cs = frame_cs[:-2], frame_cs[-2:]
        ccs = self.make_checksum(frame)
        if cs == ccs:
            logging.info( 'Checksum is OK')
            return True
        else:
            logging.warning('Checksum failure: expected %r, calculated %r' % (cs, ccs))
            return False

    def decode(self,data):
        if not isinstance(data, bytes):
            logging.error ('bytes expected, got %r' % data)
        if data.startswith(STX):  # may be decode message \x02...\x03CS\r\n
            records = self.decode_message(data)
            return records
        byte = data[:1].decode()
        if  byte.isdigit():
            records = self.decode_frame(data)
            return records
        return [self.decode_record(data)]

    def decode_message(self,message):
        if not isinstance(message, bytes):
            logging.error('bytes expected, got %r' % message)
        if not (message.startswith(STX) and message.endswith(CRLF)):
            logging.error('ERROR Malformed ASTM message. Expected that it will started with %x and followed by %x%x characters. Got: %r' % (ord(STX), ord(CR), ord(LF), message))
        stx, frame_cs = message[0], message[1:-2]
        frame, cs = frame_cs[:-2], frame_cs[-2:]
        ccs = self.make_checksum(frame)
        assert cs == ccs, 'Checksum failure: expected %r, calculated %r' % (cs, ccs)
        records = self.decode_frame(frame)
        return records

    def decode_frame(self,frame):
        if not isinstance(frame,bytes):
            logging.error('bytes expected, got %r' % frame)
        if frame.endswith(CR + ETX):
            frame = frame[:-2]
        elif frame.endswith(ETB):
            frame = frame[:-1]
        else:
            logging.warning('Incomplete frame data %r. Expected trailing <CR><ETX> or <ETB> chars' % frame)
        seq = frame[:1].decode()
        if not seq.isdigit():
            logging.warning('Malformed ASTM frame. Expected leading seq number %r' % frame)
        seq, records = int(seq), frame[1:]
        return  [self.decode_record(record)
                 for record in records.split(RECORD_SEP)]

    def decode_record(self,record):
        fields = []
        for item in record.split(FIELD_SEP):
            if REPEAT_SEP in item:
                item = self.decode_repeated_component(item)
            elif COMPONENT_SEP in item:
                item = self.decode_component(item)
            else:
                item = item
            fields.append([None, item][bool(item)])
        return fields

    def decode_component(self,field):
        return [[None, item][bool(item)]
                for item in field.split(COMPONENT_SEP)]
    
    def decode_repeated_component(self,component):
        return [self.decode_component(item)
            for item in component.split(REPEAT_SEP)]


    def encode_message(self,seq,records):
        data = RECORD_SEP.join(self.encode_record(record)
                               for record in records)
        data = b''.join((str(seq % 8).encode(), data, CR, ETX))
        return b''.join([STX, data, self.make_checksum(data), CR, LF])

    def encode_record(self,record):
        fields = []
        _append = fields.append
        for field in record:
            if isinstance(field, bytes):
                _append(field)
            elif isinstance(field, unicode):
                _append(field.encode(encoding))
            elif isinstance(field, Iterable):
                _append(encode_component(field, encoding))
            elif field is None:
                _append(b'')
            else:
                _append(unicode(field).encode(encoding))
        return FIELD_SEP.join(fields)

    def make_chunks(self,s, n):
        iter_bytes = (s[i:i + 1] for i in range(len(s)))
        return [b''.join(item)
                for item in izip_longest(*[iter_bytes] * n, fillvalue=b'')]

    def split(self,msg, size):
        stx, frame, msg, tail = msg[:1], msg[1:2], msg[2:-6], msg[-6:]
        assert stx == STX
        assert frame.isdigit()
        assert tail.endswith(CRLF)
        assert size is not None and size >= 7
        frame = int(frame)
        chunks = make_chunks(msg, size - 7)
        chunks, last = chunks[:-1], chunks[-1]
        idx = 0
        for idx, chunk in enumerate(chunks):
            item = b''.join([str((idx + frame) % 8).encode(), chunk, ETB])
            yield b''.join([STX, item, make_checksum(item), CRLF])
        item = b''.join([str((idx + frame + 1) % 8).encode(), last, CR, ETX])
        yield b''.join([STX, item, make_checksum(item), CRLF])

    def send(self,msg):
        logging.info('>>%s' % msg)
        if self.connection_type == 'TCP':
            self.conn.send(msg)
        else:
            self.serial.write(msg)
        time.sleep(0.05)

    def send_enq(self):
        logging.info('>>ENQ')
        if self.connection_type == 'TCP':
            self.conn.send(ENQ)
        else:
            self.serial.write(ENQ)
        time.sleep(0.05)

    def send_stx(self):
        logging.info('>>STX')
        if self.connection_type == 'TCP':
            self.conn.send(STX)
        else:
            self.serial.write(STX)
        time.sleep(0.05)
        
    def send_eot(self):
        logging.info('>>EOT')
        if self.connection_type == 'TCP':
            self.conn.send(EOT)
        else:
            self.serial.write(EOT)
        time.sleep(0.05)

    def send_ack(self):
        logging.info('>>ACK')
        if self.connection_type == 'TCP':
            self.conn.send(ACK)
        else:
            self.serial.write(ACK)
        time.sleep(0.05)

    def send_msg(self,msg):
        logging.info('>>%s'%msg)
        data = b''.join((str(1 % 8).encode(ENCODING), msg.encode(ENCODING), CR, ETX))
        data_tx = b''.join([STX, data, self.make_checksum(data), CR, LF])
        logging.info('data to TX:%s' % data_tx)
        if self.connection_type == 'TCP':
            self.conn.send(data_tx)
        else:
            self.serial.write(data_tx)
        time.sleep(0.05)
        
    def conTest(self):
        logging.info('testing connection..')
        self.send_enq()
        time.sleep(0.05)
        data = ''
        while self.serial.inWaiting() > 0:
            data += self.serial.read(1)
        if data == ACK:
            self.send_eot()
            logging.info('OK')
            return True
        else:
            logging.info('KO')
            return False

    def listen(self):
        logging.info('listening..')
        deadline = time.time() + 20.0
        data = ''
        while data =='':
            if self.connection_type == 'TCP':
                try:
                    data = self.conn.recv(BUFFER_SIZE)
                except Exception as e:
                    logging.error(str(e))
                    return False
            else:
                while self.serial.inWaiting() > 0:
                        data += self.serial.read(1)
        return data
