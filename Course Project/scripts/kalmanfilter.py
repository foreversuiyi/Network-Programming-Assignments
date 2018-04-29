import numpy as np
from commontools import *


class EKF:

    def __init__(self, state, covariance, params):
        self.state = np.mat([[state['x']], [state['y']], [state['ang']]])
        self.covariance = np.mat(covariance)
        self.params = params

    def prediction(self, odom_cmd):
        ts = self.params.ts
        motion_noise = self.params.motion_noise

        v = odom_cmd['v']
        w = odom_cmd['w']
        x = float(self.state[0, 0])
        y = float(self.state[1, 0])
        ang = float(self.state[2, 0])

        if w > 1e-10:
            x_bar = x - (v / w) * math.sin(ang) + (v / w) * math.sin(ang + w * ts)
            y_bar = y + (v / w) * math.cos(ang) - (v / w) * math.cos(ang + w * ts)
            ang_bar = normalize_angle(ang + w * ts)

            G = np.mat(np.eye(3))
            G[0, 2] = - v/w*math.cos(ang) + v/w*math.cos(ang + w*ts)
            G[1, 2] = - v/w*math.sin(ang) + v/w*math.sin(ang + w*ts)
        else:
            x_bar = x + v*math.cos(ang)*ts
            y_bar = y + v*math.sin(ang)*ts
            ang_bar = ang
            G = np.mat(np.eye(3))
            G[0, 2] = -v*math.sin(ang)*ts
            G[1, 2] = v*math.cos(ang)*ts
        R = np.mat(np.diag([motion_noise['x'], motion_noise['y'], motion_noise['ang']]))
        self.state = np.mat([[x_bar], [y_bar], [ang_bar]])
        self.covariance = G * self.covariance * G.T + R

    def correction(self, laser_obs, landmarks):
        laser_cov = self.params.laser_cov

        x = float(self.state[0, 0])
        y = float(self.state[1, 0])
        ang = float(self.state[2, 0])

        num_lms = len(landmarks)

        error = np.mat(np.zeros((2*num_lms, 1)))

        H = np.mat(np.zeros((2*num_lms, 3)))
        measure_cov = []
        for k in range(num_lms):
            lmx = landmarks[k]['x']
            lmy = landmarks[k]['y']

            delta_x = lmx - x
            delta_y = lmy - y

            q = delta_x**2 + delta_y**2
            if q == 0:
                q = 1e-6
            calc_dist = math.sqrt(q)

            bear = math.atan2(lmy - y, lmx - x) - ang
            calc_bear = normalize_angle(bear)

            error[2*k, 0] = laser_obs[k]['dist'] - calc_dist
            error[2*k+1, 0] = normalize_angle(laser_obs[k]['bear'] - calc_bear)

            measure_cov.append(laser_cov['dist'])
            measure_cov.append(laser_cov['bear'])

            H[2 * k, 0] = -delta_x*calc_dist/q
            H[2 * k, 1] = -delta_y*calc_dist/q
            H[2 * k, 2] = 0

            H[2 * k+1, 0] = delta_y/q
            H[2 * k+1, 1] = -delta_x/q
            H[2 * k+1, 2] = -1

        Q = np.mat(np.diag(measure_cov))
        tmp_cov = H*self.covariance*H.T + Q

        K = self.covariance*H.T*tmp_cov.I

        self.state = self.state + K*error
        self.state[2][0] = normalize_angle(self.state[2][0])
        self.covariance = (np.mat(np.eye(3)) - K*H)*self.covariance

    def posterior(self):
        pos_state = dict()
        pos_state['x'] = float(self.state[0, 0])
        pos_state['y'] = float(self.state[1, 0])
        pos_state['ang'] = float(self.state[2, 0])
        pos_cov = self.covariance.tolist()
        result = (pos_state, pos_cov)
        return result
