from longclaw import app
import socket
import fcntl
import struct
import sys

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


host = ''
if len(sys.argv) <= 1:
		host = ''
else:
	if sys.argv[1] == 'ip':
		try:
			host = get_ip_address('wlan0')
		except:
			host = get_ip_address('eth0')
	else:
		host = ''

if host == '':
	host = 'localhost'


if __name__ == '__main__':
	
	app.run(
        host=host,
        debug=True)
