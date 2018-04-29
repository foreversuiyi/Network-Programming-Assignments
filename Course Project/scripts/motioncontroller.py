from commontools import *


class MotionController:
    def __init__(self, state, params):
        self.state = state
        self.v = 0
        self.w = 0
        self.nxt_point = dict()
        self.ending = False
        self.kp = params.kp
        self.ts = params.ts
        self.wheel_base = params.wheel_base
        self.forward_dist = params.forward_dist
        self.forward_gain = params.forward_gain

    def next_point(self, path):
        min_idx = 0
        min_dist = 1000.0
        robot_x = self.state['x']
        robot_y = self.state['y']
        for k, point in enumerate(path):
            point_x = point['x']
            point_y = point['y']
            dist = math.sqrt((point_x - robot_x)**2 + (point_y - robot_y)**2)
            if dist < min_dist:
                min_dist = dist
                min_idx = k
        if min_idx - len(path) < -1 and not self.ending:
            dist = 0
            forward_dist = self.forward_gain * self.v + self.forward_dist
            while forward_dist > dist:
                nxt_idx = (min_idx+1) % len(path)
                dx = path[nxt_idx]['x'] - path[min_idx]['x']
                dy = path[nxt_idx]['y'] - path[min_idx]['y']

                dist += math.sqrt(dx**2 + dy**2)
                min_idx += 1
                min_idx = min_idx % len(path)
            self.ending = False
        elif min_dist < 2:
            self.ending = True
        self.nxt_point['idx'] = min_idx
        self.nxt_point['x'] = path[min_idx]['x']
        self.nxt_point['y'] = path[min_idx]['y']

    def generate_cmd(self):
        tx = self.nxt_point['x']
        ty = self.nxt_point['y']
        error_ang = normalize_angle(math.atan2(ty - self.state['y'], tx - self.state['x']) - self.state['ang'])
        if self.ending:
            target_vel = 0.0
        else:
            target_vel = 5.0

        self.v += self.kp*(target_vel - self.v)*self.ts

        if self.v < 0:
            error_ang = normalize_angle(math.pi - error_ang)

        forward_dist = self.forward_gain*self.v + self.forward_dist
        delta = math.atan2(2.0 * self.wheel_base * math.sin(error_ang)/forward_dist, 1.0)

        self.w = self.v/self.wheel_base * math.tan(delta)

    def get_cmd(self):
        cmd = dict()
        cmd['v'] = self.v
        cmd['w'] = self.w
        cmd_out = (cmd, self.ending)
        return cmd_out
