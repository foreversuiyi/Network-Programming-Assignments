import random
from commontools import *


class Robot:
    def __init__(self, idx, x, y, ang):
        self.idx = idx
        self.v = 0
        self.w = 0
        self.real_x = x
        self.real_y = y
        self.real_ang = normalize_angle(ang)
        self.calc_x = x
        self.calc_y = y
        self.calc_ang = normalize_angle(ang)
        self.covariance = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def set_state(self, state, covariance, odom):
        self.calc_x = state['x']
        self.calc_y = state['y']
        self.calc_ang = normalize_angle(state['ang'])
        self.covariance = covariance
        self.v = odom['v']
        self.w = odom['w']

    def read_laser(self, landmarks, cov):
        range_measure = []
        for k in range(len(landmarks)):
            lmx = landmarks[k]['x']
            lmy = landmarks[k]['y']
            dist_cov = random.gauss(0, math.sqrt(cov['dist']))
            bear_cov = random.gauss(0, math.sqrt(cov['bear']))
            tmp = {'dist': math.sqrt((lmx - self.real_x)**2 + (lmy - self.real_y)**2) + dist_cov,
                   'bear': math.atan2(lmy - self.real_y, lmx - self.real_x) - self.real_ang + bear_cov,
                   'idx': landmarks[k]['idx']}
            tmp['bear'] = normalize_angle(tmp['bear'])
            range_measure.append(tmp)

        return range_measure

    def read_odom(self):
        odom_measure = dict()
        odom_measure['v'] = self.v
        odom_measure['w'] = self.w

        return odom_measure

    def motion_update(self, v, w, ts):
        if w == 0:
            w = 1e-6
        self.real_x = self.real_x + (-(v/w)*math.sin(self.real_ang)+(v/w)*math.sin(self.real_ang+w*ts))
        self.real_y = self.real_y + (v/w)*math.cos(self.real_ang)-(v/w)*math.cos(self.real_ang+w*ts)
        self.real_ang = normalize_angle(self.real_ang + w*ts)

        real_state = dict()
        real_state['x'] = self.real_x
        real_state['y'] = self.real_y
        real_state['ang'] = self.real_ang
        return real_state
