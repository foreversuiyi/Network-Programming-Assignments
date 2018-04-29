import numpy as np
from scipy import special
from commontools import *


class Params:
    def __init__(self):
        # Set the motion noise
        self.motion_noise = {'x': 0.1, 'y': 0.1, 'ang': 0.1}

        # Set the laser measurement covariance
        self.laser_cov = {'dist': 0.01, 'bear': 0.001}

        # Set the update time interval
        self.ts = 0.1

        # Set the controller parameters
        self.kp = 10
        self.wheel_base = 2.0
        self.forward_dist = 1.0
        self.forward_gain = 0.1


class RobotMap:
    def __init__(self):
        # Map points
        self.interval = 1
        self.offset = 3

        # Set the landmark positions
        landmarks = list()
        landmarks.append({'x': -10, 'y': -10, 'idx': 0})
        landmarks.append({'x': 20, 'y': -10, 'idx': 1})
        landmarks.append({'x': 50, 'y': -10, 'idx': 2})
        landmarks.append({'x': 80, 'y': -10, 'idx': 3})
        landmarks.append({'x': -10, 'y': 80, 'idx': 4})
        landmarks.append({'x': 20, 'y': 80, 'idx': 5})
        landmarks.append({'x': 50, 'y': 80, 'idx': 6})
        landmarks.append({'x': 80, 'y': 80, 'idx': 7})
        self.landmarks = landmarks

        # Set the outer path points
        outer_path = list()
        outer_path.append([10, 0, 0])
        outer_path.append([60, 0, 0])
        outer_path.append([70, 10, math.pi / 2])
        outer_path.append([70, 60, math.pi / 2])
        outer_path.append([60, 70, math.pi])
        outer_path.append([10, 70, math.pi])
        outer_path.append([0, 60, -math.pi / 2])
        outer_path.append([0, 10, -math.pi / 2])
        outer_path.append([10, 0, 0])
        self.outer_path = outer_path

        # Set the inner path points
        inner_path = list()
        inner_path.append([10, 0, 0])
        inner_path.append([60, 0, 0])
        inner_path.append([70, 10, math.pi / 2])
        inner_path.append([70, 60, math.pi / 2])
        inner_path.append([60, 70, math.pi])
        inner_path.append([10, 70, math.pi])
        inner_path.append([0, 60, -math.pi / 2])
        inner_path.append([0, 10, -math.pi / 2])
        inner_path.append([10, 0, 0])
        self.inner_path = inner_path

    def generate_bezier(self, start_point, end_point):
        interval = self.interval
        offset = self.offset
        sx = start_point[0]
        sy = start_point[1]
        sang = start_point[2]
        ex = end_point[0]
        ey = end_point[1]
        eang = end_point[2]

        D = math.sqrt((sx - ex) ** 2 + (sy - ey) ** 2) / offset
        cp = np.array([[sx, sy], [sx + D * math.cos(sang), sy + D * math.sin(sang)],
                       [ex - D * math.cos(eang), ey - D * math.sin(eang)], [ex, ey]])

        traj = []
        n = 3
        num_points = int(round(math.sqrt((sx - ex) ** 2 + (sy - ey) ** 2) / interval))
        for t in np.linspace(0, 1, num_points):
            p = np.zeros(2)
            for i in range(n + 1):
                bernstein = special.comb(n, i) * t ** i * (1 - t) ** (n - i)
                p += bernstein * cp[i]
            traj.append(p.tolist())

        return traj[:-1]

    def generate_line(self, start_point, end_point):
        interval = self.interval
        line = list()
        dist = math.sqrt((start_point[0] - end_point[0]) ** 2 + (start_point[1] - end_point[1]) ** 2)
        number = round(dist / interval)
        for k in range(number):
            new_point = [start_point[0] + k / number * (end_point[0] - start_point[0]),
                         start_point[1] + k / number * (end_point[1] - start_point[1])]
            line.append(new_point)

        return line

    def generate_path(self):
        path = list()

        for k in range(len(self.outer_path) - 1):
            new_traj = self.generate_bezier(self.outer_path[k], self.outer_path[k + 1])
            path.extend(new_traj)
        path.append([10, 0])

        whole_path = list()
        for k in range(len(path) - 1):
            tmp = dict()
            tmp['idx'] = k
            tmp['x'] = path[k][0]
            tmp['y'] = path[k][1]
            ang = math.atan2(path[k + 1][1] - path[k][1], path[k + 1][0] - path[k][0])
            tmp['ang'] = normalize_angle(ang)
            whole_path.append(tmp)

        return whole_path
