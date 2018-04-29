import socket
import json
import sys
import multiprocessing
import threadpool
from kalmanfilter import EKF
from motioncontroller import MotionController
from initialize import RobotMap
from initialize import Params
import matplotlib.pyplot as plt
import math


def serve_client(c_soc, c_address, robot_dict):
    params = Params()
    robot_map = RobotMap()
    landmarks = robot_map.landmarks
    whole_path = robot_map.generate_path()
    print("Robot %s is running." % c_address[0])
    served = False
    while True:
        rev_data = c_soc.recv(2048).decode('utf-8')
        robot_data = json.loads(rev_data)
        prior_state = robot_data['state']
        prior_covariance = robot_data['covariance']
        odom_cmd = robot_data['odom']
        laser_obs = robot_data['laser']
        robot_idx = robot_data['idx']

        # If the robot index is wrong
        if not served:
            if robot_idx in robot_dict:
                send_data = dict()
                send_data['state'] = prior_state
                send_data['covariance'] = prior_covariance
                send_data['odom'] = odom_cmd
                send_data['success'] = True
                msg = json.dumps(send_data)
                c_soc.send(msg.encode('utf-8'))
                print("[Error] Duplicate Robot Index, Robot %s Terminated." % c_address[0])
                break
            served = True

        kalman_filter = EKF(prior_state, prior_covariance, params)
        kalman_filter.prediction(odom_cmd)
        kalman_filter.correction(laser_obs, landmarks)
        (post_state, post_covariance) = kalman_filter.posterior()

        controller = MotionController(post_state, params)
        controller.next_point(whole_path)
        controller.generate_cmd()
        (new_odom_cmd, success_flag) = controller.get_cmd()

        send_data = dict()
        send_data['state'] = post_state
        send_data['covariance'] = post_covariance
        send_data['odom'] = new_odom_cmd
        send_data['success'] = success_flag
        msg = json.dumps(send_data)
        c_soc.send(msg.encode('utf-8'))

        robot_dict[robot_idx] = post_state
        if send_data['success']:
            print("Robot %s is completed." % c_address[0])
            del robot_dict[robot_idx]
            break


def localization_process(soc_queue, robot_dict):
    pool = threadpool.ThreadPool(4)
    while True:
        (c_soc, c_adr) = soc_queue.get()
        dict_vars = {'c_soc': c_soc, 'c_address': c_adr, 'robot_dict': robot_dict}
        requests = threadpool.makeRequests(serve_client, args_list=[(None, dict_vars), ])
        for req in requests:
            pool.putRequest(req)


def plot_process(robot_dict):
    # plot all stuff
    robot_map = RobotMap()
    landmarks = robot_map.landmarks

    fig = plt.figure()
    landmarks_x = []
    landmarks_y = []
    for k in range(len(landmarks)):
        landmarks_x.append(landmarks[k]['x'])
        landmarks_y.append(landmarks[k]['y'])

    path = robot_map.generate_path()
    path_x = []
    path_y = []
    for p in path:
        path_x.append(p['x'])
        path_y.append(p['y'])
    path_x.append(path_x[0])
    path_y.append(path_y[0])
    while True:
        plt.cla()
        plt.scatter(landmarks_x, landmarks_y, marker='*', color='c', s=200)
        plt.plot(path_x, path_y, "--")
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")
        plt.title("Real time position of the robots")

        if len(robot_dict) > 0:
            plt_robots = robot_dict
        else:
            plt_robots = dict()

        for (key, value) in plt_robots.items():
            plt.plot(value['x'], value['y'], "ro")
            plt.text(value['x']+1, value['y']+1, ('Robot '+key), color='black', fontsize=5)
            plt.arrow(value['x'], value['y'], 5*math.cos(value['ang']), 5*math.sin(value['ang']),
                      length_includes_head=True, head_width=2, head_length=2, fc='y', ec='g')
        plt.pause(0.01)


if __name__ == '__main__':
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if len(sys.argv) != 3:
            print("Usage Error, launching server failed")
            print("Usage: python3 server.py <port number> <number of serve processes>")
        else:
            print("Server launched successfully.")
            soc.bind(("localhost", int(sys.argv[1])))
            soc.listen(10)
            print("Listening for incoming connections on port %s" % sys.argv[1])

            socket_queue = multiprocessing.Queue()
            m = multiprocessing.Manager()
            robot_dict = m.dict()
            for i in range(int(sys.argv[2])):
                p = multiprocessing.Process(target=localization_process, args=(socket_queue, robot_dict))
                p.start()
            plt_p = multiprocessing.Process(target=plot_process, args=(robot_dict, ))
            plt_p.start()

            while True:
                (client_socket, address) = soc.accept()
                print("Robot %s connected." % address[0])
                socket_queue.put((client_socket, address))
    except Exception as err:
        print("Error type: %s" % err)
    finally:
        soc.close()
