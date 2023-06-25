import time
import serial

STX = b'\x02'
ETX = b'\x03'
LF  = b'\x0A'
CR  = b'\x0D'
CRLF = CR + LF
# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='COM11',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS
)

ser.isOpen()

data = ' 29-03-2019 20:51:17'+CRLF
data = data + ' ID:1903300001UR  '+ CRLF
data = data + ' No.: 10293E     (00003940)'+CRLF
data = data + 'Other              Other'+CRLF
data = data + 'LEU         -        neg'+CRLF
data = data + '*BLO          3+              200Ery/uL'+CRLF
data = data + 'pH            7.0 '+CRLF
data = data + 'CRE                          100mg/dL'+CRLF
data = data + 'Nit            -              neg'+CRLF
data = data + '*Ket           3+             80mg/dL'+CRLF
data = data + 'SG             1.015  '+CRLF
data = data + 'ASC            -'+CRLF
data = data + 'GLU           -                neg'+CRLF
data = data + '*PRO           3+            300mg/dL'+CRLF
data = data + 'ALB                          150mg/dL'+CRLF
data = data + '*URO           3+            8mg/dL'+CRLF
data = data + '*LEU           3+            500Leu/ul'+CRLF



data = ' 29-03-2019 20:51:17'+CRLF
data = data + ' ID:1903300001UR  '+CRLF
data = data + ' No.: 10293E     (00003940)'+CRLF
data = data + ' Other              Other'+CRLF
data = data + '*LEU         -        neg'+CRLF
data = data + ' NIT         -        neg'+CRLF
data = data + ' URO         -   0.2mg/dL'+CRLF
data = data + ' PRO        +-    15mg/dL'+CRLF
data = data + ' pH         6.0          '+CRLF
data = data + ' BLO        +-   10Ery/uL'+CRLF
data = data + ' SG         1.025        '+CRLF
data = data + ' KET         -        neg'+CRLF
data = data + ' BIL         -        neg'+CRLF
data = data + ' GLU         -        neg'+CRLF


print data

ser.write(STX+data+ETX)

ser.close()
