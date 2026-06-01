import math

# HORIZONTAL

_MIN_RADIUS_EMAX6 = {
    40:  45,
    50:  90,
    60:  140,
    70:  220,
    80:  350,
    90:  490,
    100: 680,
    110: 890,
    120: 112,
    130: 147,
}

_MIN_RADIUS_EMAX7 = {
    40:  40,
    50:  80, 
    60:  130,
    70:  200,
    80:  310,
    90:  440,
    100: 600,
    110: 790, 
    120: 1000,
    130: 1300,
}

_MIN_RADIUS_EMAX10 = {
    40:  30,
    50:  55,
    60:  90, 
    70:  140,
    80:  200,
    90:  280,
    100: 370,
    110: 490,
    120: 630, 
    130: 800, 
}

_SSD = {
    40: 40,
    50: 60,
    60: 85,
    70: 110,
    80: 140,
    90: 170,
    100: 210,
}

_MAX_GRADE = {
    40: 16, 50: 12, 60: 10, 70: 9,
    80: 8,  90: 7,  100: 6,
}

MIN_GRADE = 0.3
MIN_VCL = 50

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
    # desirable = math.ceil(v **3 / (radius * 0.3))
    # return {'absolute': absolute, 'desirable': desirable}
    return absolute

def get_min_tangent_between_curves(speed):
    # return {'absolute': speed, 'desirable': speed *2}
    return speed

def get_ssd(speed):
    return _SSD[speed]

def get_max_grade(speed):
    return _MAX_GRADE[speed]

def get_sag_k(speed):
    ssd = _SSD[speed]
    k = ssd * ssd/(120+3.5 * ssd)
    return k

def get_crest_k(speed):
    ssd = _SSD[speed]
    H = math.sqrt(2 * 1.15) + math.sqrt(2 * 0.2)
    k = ssd * ssd / (200 * H ** 2)
    return k



