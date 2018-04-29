import socket
import sys
import json
import robot
import time
from initialize import Params
from initialize import RobotMap
import matplotlib.pyplot as plt


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    if len(sys.argv) != 7:
        print("Usage Error, launching server failed")
        print("Usage: python3 client.py <server IP> <server port number> <robot index> <robot x> <robot y> <robot ang>")
    else:
        # parameters initialization
        params = Params()
        ts = params.ts
        laser_cov = params.laser_cov

        robot_map = RobotMap()
        landmarks = robot_map.landmarks

        # connect to the server
        soc.connect((sys.argv[1], int(sys.argv[2])))

        # create the new robot
        robot_idx = sys.argv[3]
        x = float(sys.argv[4])
        y = float(sys.argv[5])
        ang = float(sys.argv[6])
        new_robot = robot.Robot(robot_idx, x, y, ang)

        # plot the landmarks
        fig = plt.figure()
        landmarks_x = []
        landmarks_y = []
        for k in range(len(landmarks)):
            landmarks_x.append(landmarks[k]['x'])
            landmarks_y.append(landmarks[k]['y'])

        # plot the path
        path = robot_map.generate_path()
        path_x = []
        path_y = []
        for p in path:
            path_x.append(p['x'])
            path_y.append(p['y'])
        path_x.append(path_x[0])
        path_y.append(path_y[0])

        while True:
            # Frequency Control
            begin = time.time()

            # prior state and motion command
            state = {'x': new_robot.calc_x, 'y': new_robot.calc_y, 'ang': new_robot.calc_ang}
            covariance = new_robot.covariance

            # observations
            real_state = new_robot.motion_update(new_robot.v, new_robot.w, ts)
            odom_measure = new_robot.read_odom()
            laser_measure = new_robot.read_laser(landmarks, laser_cov)

            # send all the data to the server
            send_data = dict()
            send_data['idx'] = new_robot.idx
            send_data['state'] = state
            send_data['covariance'] = covariance
            send_data['odom'] = odom_measure
            send_data['laser'] = laser_measure

            msg = json.dumps(send_data)
            soc.send(msg.encode('utf-8'))

            # compare the real state and calculated state
            new_robot.real_x = real_state['x']
            new_robot.real_y = real_state['y']
            new_robot.real_ang = real_state['ang']

            # receive the calculated state and motion command
            data = soc.recv(2048).decode('utf-8')
            rev_data = json.loads(data)
            new_robot.set_state(rev_data['state'], rev_data['covariance'], rev_data['odom'])

            # plot the real state and calculate state
            '''plt.cla()
            plt.scatter(landmarks_x, landmarks_y, marker='+', color='c')
            plt.plot(path_x, path_y, "--")
            plt.plot(new_robot.calc_x, new_robot.calc_y, "or")
            plt.plot(new_robot.real_x, new_robot.real_y, "xb")
            plt.xlabel("x (m)")
            plt.ylabel("y (m)")
            plt.title("Real time position of the robot")
            plt.pause(0.001)'''

            # if the mission success, break the loop
            if rev_data['success']:
                break

            # control the update frequency
            time.sleep((ts - time.time() + begin) if time.time() - begin < ts else 0.0)

except Exception as err:
    print('Error type: %s' % err)

finally:
    soc.close()
