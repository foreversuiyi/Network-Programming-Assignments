import math


def normalize_angle(phi):
    while phi > math.pi:
        phi = phi - 2*math.pi
    while phi < -math.pi:
        phi = phi + 2*math.pi
    return phi
