import socket
# noinspection PyUnresolvedReferences
import sys
# noinspection PyUnresolvedReferences
import json
# create an INET TCP socket
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # connect to the server (change localhost to an IP address if necessary)
    soc.connect((sys.argv[1], int(sys.argv[2])))
    print("Connected to server.")
    f = open(sys.argv[3], 'r')
    data = f.read() + "[END]"
    # Send a message to the server
    msg = data.encode("utf-8")
    soc.send(msg)
    # Receive data from the server
    parts = []
    while True:
        part = soc.recv(1024)
        if part == b'':
            break
        parts.append(part)
    data = b"".join(parts)
    rev_data = json.loads(data.decode('utf-8'))
    words = []
    prop = []
    for x in range(len(rev_data)):
        words.append(rev_data[x][0])
        prop.append(rev_data[x][1])
    print(" ; ".join(words))
    print(" ; ".join(prop))
except socket.error:
    print("Cannot connect to server %s : %s" % (sys.argv[1], sys.argv[2]))
except Exception as err:
    print("Other error. %s" % err)
finally:
    # Always close the socket after use
    soc.close()
