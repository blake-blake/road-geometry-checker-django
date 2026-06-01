import math

_MIN_RADIUS_EMAX6 = {
    40: {'absolute': 45, 'desirable': 60},
    50:  {'absolute': 90,   'desirable': 120},
    60:  {'absolute': 145,  'desirable': 210},
    70:  {'absolute': 220,  'desirable': 320},
    80:  {'absolute': 350,  'desirable': 485},
    90:  {'absolute': 495,  'desirable': 680},
    100: {'absolute': 680,  'desirable': 920},
    110: {'absolute': 890,  'desirable': 1205},
    120: {'absolute': 1125, 'desirable': 1510},
    130: {'absolute': 1470, 'desirable': 1970},
}

_MIN_RADIUS_EMAX7 = {
    40:  {'absolute': 40,   'desirable': 55},
    50:  {'absolute': 80,   'desirable': 110},
    60:  {'absolute': 130,  'desirable': 190},
    70:  {'absolute': 200,  'desirable': 290},
    80:  {'absolute': 310,  'desirable': 440},
    90:  {'absolute': 440,  'desirable': 620},
    100: {'absolute': 600,  'desirable': 840},
    110: {'absolute': 790,  'desirable': 1100},
    120: {'absolute': 1000, 'desirable': 1380},
    130: {'absolute': 1300, 'desirable': 1800},
}

_MIN_RADIUS_EMAX10 = {
    40:  {'absolute': 30,   'desirable': 40},
    50:  {'absolute': 55,   'desirable': 80},
    60:  {'absolute': 90,   'desirable': 130},
    70:  {'absolute': 140,  'desirable': 200},
    80:  {'absolute': 200,  'desirable': 310},
    90:  {'absolute': 280,  'desirable': 440},
    100: {'absolute': 370,  'desirable': 600},
    110: {'absolute': 490,  'desirable': 800},
    120: {'absolute': 630,  'desirable': 1000},
    130: {'absolute': 800,  'desirable': 1300},
}

def get_min_radius(speed, emax):
    if emax == 10:
        return _MIN_RADIUS_EMAX10[speed]
    if emax == 6:
        return _MIN_RADIUS_EMAX6[speed]
    return _MIN_RADIUS_EMAX7[speed]

def get_min_curve_length(speed):
    # Calculates for 3s of travel 
    return (speed / 3.6) * 3

def get_min_transition_length(speed, radius):
    v = speed / 3.6
    absolute = math.ceil(v ** 3 / (radius * 0.6)) #uses rate of rotation
    desirable = math.ceil(v **3 / (radius * 0.3))
    return {'absolute': absolute, 'desirable': desirable}

def get_min_tangent_between_curves(speed):
    return {'absolute': speed, 'desirable': speed *2}

