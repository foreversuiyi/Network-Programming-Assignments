import os
import socket
from urllib import request
import time
import multiprocessing
import sys
import logging
import threadpool
import json
from multiprocessing import Process
import numpy as np
from keras_squeezenet import SqueezeNet
from keras.applications.imagenet_utils import preprocess_input
from keras.applications.imagenet_utils import decode_predictions
from keras.preprocessing import image
import tensorflow as tf


def serve_client(c_soc, c_adr, graph, model, image_index):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("server_log.txt")
    ch = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(processName)s] [%(threadName)s] : %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    try:
        logger.info("Received Client (%s, %s)." % (c_adr[0], c_adr[1]))
        whole_data = ""
        while True:
            data = c_soc.recv(1024).decode("utf-8")
            whole_data += data
            if whole_data.find("[END]") != -1:
                break
        url = whole_data[0:whole_data.find("[END]")]
        logger.info("Client submitted URL " + url)
        img_path = os.getcwd() + '\images'
        if not os.path.exists(img_path):
            os.mkdir(img_path)
        file_name = str(time.time()) + str(image_index) + '.jpg'
        dest_dir = os.path.join(img_path, file_name)
        request.urlretrieve(url, dest_dir)
        logger.info("Image saved to images/" + file_name)
        # process the image
        img = image.load_img(dest_dir, target_size=(227, 227))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        with graph.as_default():
            preds = model.predict(x)
        result = decode_predictions(preds)
        result = result[0][0]
        send_data = (result[1], float(result[2]))
        probability = '%.3f' % float(result[2])
        result_info = (result[1], float(probability))
        logger.info("SqueezeNet result: " + str(result_info))
        # Return the recognition result
        send_msg = json.dumps(send_data)
        c_soc.send(send_msg.encode('utf-8'))
    except Exception as err:
        print(err)
    finally:
        logger.info("Client connection closed")
        c_soc.shutdown()
        c_soc.close()


def process(soc_queue):
    graph = tf.get_default_graph()
    model = SqueezeNet()
    pool = threadpool.ThreadPool(4)
    while True:
        (c_soc, c_adr, image_index) = soc_queue.get()
        dic_vars = {'c_soc': c_soc, 'c_adr': c_adr, 'graph': graph, 'model': model, 'image_index': image_index}
        requests = threadpool.makeRequests(serve_client, args_list=[(None, dic_vars), ])
        for req in requests:
            pool.putRequest(req)


if __name__ == '__main__':
    try:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler("server_log.txt")
        ch = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(processName)s] [%(threadName)s] : %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        logger.addHandler(ch)
        logger.addHandler(fh)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", int(sys.argv[1])))
        server_socket.listen(100)
        logger.info("Listening for incoming connections on port %s" % sys.argv[1])
        socket_queue = multiprocessing.Queue()
        for i in range(int(sys.argv[2])):
            p = Process(target=process, args=(socket_queue, ))
            p.start()
            logger.info("Created process Process-%d" % (i + 1))
        image_index = 0
        while True:
            (client_socket, address) = server_socket.accept()
            image_index = image_index + 1
            logger.info("Client ('%s', %s) connected." % (address[0], address[1]))
            socket_queue.put((client_socket, address, image_index))
    finally:
        pass

