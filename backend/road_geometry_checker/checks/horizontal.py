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

def check_horizontal_alignment(data, speed, emax, ip_speed_overrides = None):
    _counter[0] = 0
    if ip_speed_overrides is None:
        ip_speed_overrides = {}

    results = []
    horizontal_ips = data.get('horizontal_ips', [])
    if not horizontal_ips:
        return results

    emax_label = f'emax={emax}%'
    clause = 'AGRD03 Table 3.1 / MRWA Supplement' if emax == 10 else 'AGRD03 Table 3.1'


    for i, ip in enumerate(horizontal_ips):
        if ip['radius'] == 0:
            continue

        ip_speed = ip_speed_overrides.get(ip['id'], speed)
        min_r = get_min_radius(ip_speed, emax)
        min_trans = get_min_transition_length(ip_speed, ip['radius'])
        label = f"IP {ip['id']}"

        results.append({
            'id': _id(),
            'category': 'Horizontal Alignment',
            'element': label,
            'check': 'Minimum curve radius (absolute)',
            'value': f"{ip['radius']} m",
            'limit': f"≥ {min_r['absolute']} m ({emax_label})",
            'status': 'pass' if ip['radius'] >= min_r['absolute'] else 'fail',
            'clause': clause,
            'notes': None,
        })

        if min_r['absolute'] <= ip['radius'] < min_r['desirable']:
            results.append({
                'id': _id(),
                'category': 'Horizontal Alignment',
                'element': label,
                'check': 'Minimum curve radius (desirable)',
                'value': f"{ip['radius']} m",
                'limit': f"≥ {min_r['desirable']} m ({emax_label})",
                'status': 'warning',
                'clause': clause,
                'notes': 'Radius meets absolute minimum but not desirable. Justification required.',
            })

    return results