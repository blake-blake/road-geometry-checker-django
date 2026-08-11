from ..standards.austroads import(
    get_min_radius,
    get_min_curve_length,
    get_min_transition_length,
    get_min_tangent_between_curves
)

_counter = [0]

def _id(prefix = 'h'):
    _counter[0] += 1
    return f'{prefix}{_counter[0]}'

def check_horizontal_alignment(data, settings, ip_speed_overrides = None):
    _counter[0] = 0
    if ip_speed_overrides is None:
        ip_speed_overrides = {}

    results = []
    horizontal_ips = data.get('horizontal_ips', [])
    if not horizontal_ips:
        return results

   

    for i, ip in enumerate(horizontal_ips):
        if ip['radius'] == 0:
            continue

        _check_horizontal_curve_radius(ip, settings, results, ip_speed_overrides)

        # min_trans = get_min_transition_length(ip_speed, ip['radius'])

        


    return results

def _check_horizontal_curve_radius(ip, settings, results, ip_speed_overrides):
    ip_speed = ip_speed_overrides.get(ip['id'], settings.speed)
    min_r = get_min_radius(ip_speed, settings.emax)
    label = f"H{ip['id']}"
    emax_label = f'emax={settings.emax}%'
    clause = 'AGRD03 Table 3.1 / MRWA Supplement' if settings.emax == 10 else 'AGRD03 Table 3.1'


    results.append({
        'id': _id(),
        'category': 'Horizontal Alignment',
        'element': label,
        'check': 'Minimum curve radius (absolute)',
        'value': f"{ip['radius']} m",
        'limit': f"≥ {min_r} m ({emax_label})",
        'status': 'pass' if ip['radius'] >= min_r else 'fail',
        'clause': clause,
        'notes': None,
    })
    
    return results