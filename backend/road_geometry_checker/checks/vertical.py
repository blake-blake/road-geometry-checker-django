from ..standards.austroads import (
    get_max_grade,
    get_sag_k,
    get_crest_k,
    MIN_GRADE,
    MIN_VCL,
)

_counter = [0]

def _id():
    _counter[0] += 1
    return f'v{_counter[0]}'

def check_vertical_alignment(data, speed, emax, ip_speed_overrides=None):
    _counter[0] = 0
    if ip_speed_overrides is None:
        ip_speed_overrides = {}

    results = []

    vertical_ips = data.get('vertical_ips', [])
    grade_sections = data.get('grade_sections', [])

    if not vertical_ips:
        return results

    max_grade = get_max_grade(speed)

    for section in grade_sections:
        grade = abs(section['grade'])
        results.append({
            'id': _id(),
            'category': 'Vertical Alignment',
            'element':  f"CH {section['from_chainage']:.0f}–{section['to_chainage']:.0f}",
            'check':    'Maximum grade',
            'value':    f"{section['grade']:.2f}%",
            'limit':    f"≤ {max_grade}%",
            'status':   'pass' if grade <= max_grade else 'fail',
            'clause':   'AGRD03 Table 4.1',
            'notes':    None,
        })
    
        if abs(grade) < MIN_GRADE:
            results.append({
                'id': _id(),
                'category': 'Vertical Alignment',
                'element':  f"CH {section['from_chainage']:.0f}–{section['to_chainage']:.0f}",
                'check':    'Minimum grade (drainage)',
                'value':    f"{section['grade']:.2f}%",
                'limit':    f"≥ {MIN_GRADE}%",
                'status':   'warning',
                'clause':   'AGRD03 Section 4.3',
                'notes':    'Grade below minimum - drainage may be insufficient',
            })

    for vip in vertical_ips:
        if vip['vc_type'] == 'none' or vip['vc_length'] == 0:
            continue

        label = f"V{vip['id']}"

        if vip['vc_type'] == 'crest':
            k_limits = get_crest_k(speed)
            clause = "AGRD03 Table 4.4"
        else:
            k_limits = get_sag_k(speed)
            clause = "AGRD04 Table 4.5"

        k = vip['k_value'] if vip['k_value'] > 0 else (
            vip['vc_length'] / vip['grade_change']
        )

        results.append({
            'id': _id(),
            'category': 'Vertical Alignment',
            'element':  label,
            'check':    f"K value ({vip['vc_type']})",
            'value':    f"K = {k:.1f}",
            'limit':    f"≥ {k_limits:.1f}",
            'status':   'fail' if k < k_limits else 'pass',
            'clause':   clause,
            'notes':    None,
        })

        if vip['vc_length'] < MIN_VCL:
            results.append({
                'id':       _id(),
                'category': 'Vertical Alignment',
                'element':  label,
                'check':    'Minimum vertical curve length',
                'value':    f"{vip['vc_length']:.1f} m",
                'limit':    f"≥ {MIN_VCL} m",
                'status':   'fail',
                'clause':   'AGRD03 Section 4.4',
                'notes':    None,
            })

    return results