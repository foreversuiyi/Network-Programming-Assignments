import socket
import sys
import logging
import json
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("client_log.txt")
    ch = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(processName)s] [%(threadName)s] : %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    # connect to the server (change localhost to an IP address if necessary)
    soc.connect((sys.argv[1], int(sys.argv[2])))
    logger.info("Connected to server at (%s, %s)" % (sys.argv[1], sys.argv[2]))
    data = sys.argv[3] + "[END]"
    # Send a message to the server
    msg = data.encode("utf-8")
    soc.send(msg)
    logger.info("URL sent to the server.")
    data = soc.recv(1024)
    rev_data = json.loads(data.decode('utf-8'))
    # Receive data from the server
    logger.info("Server response: " + str(tuple(rev_data)))
except socket.error:
    print("Cannot connect to server %s : %s" % (sys.argv[1], sys.argv[2]))
except Exception as err:
    print("Other error. %s" % err)
finally:
    # Always close the socket after use
    soc.close()
