import socket
# noinspection PyUnresolvedReferences
import sys
# noinspection PyUnresolvedReferences
import nltk
# noinspection PyUnresolvedReferences
import json

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", int(sys.argv[1])))
server_socket.listen(10)
print("Listening for incoming connections on port %s" % sys.argv[1])

while True:
    (client_socket, address) = server_socket.accept()
    print("Client %s connected." % address[0])
    whole_data = ""
    try:
        while True:
            data = client_socket.recv(2048).decode("utf-8")
            whole_data += data
            if whole_data.find("[END]") != -1:
                break
        whole_data = whole_data[0:whole_data.find("[END]")]
        print(whole_data)
        tokens = nltk.word_tokenize(whole_data)
        tagged = nltk.pos_tag(tokens)
        send_msg = json.dumps(tagged)
        client_socket.send(send_msg.encode('utf-8'))
    finally:
        print("Client disconnected.")
        client_socket.close()
