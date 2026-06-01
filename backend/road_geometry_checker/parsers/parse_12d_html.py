
import re
import math
from bs4 import BeautifulSoup



def parse_12d_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    warnings = []

    tables = soup.find_all('table')
    grids = [_table_to_grid(t) for t in tables]

    horizontal_ips = []
    vertical_ips = []
    grade_sections = []
    superelevation = []

    '''
    For each table:
    Convert table to text
    Does it look horizontal? Parse it.
    Does it look vertical? Parse it.
    Does it look like superelevation? Parse it.
    '''

    for grid in grids:
        cells = []
        for row in grid:
            for cell in row:
                cells.append(cell)
        flat = ' '.join(cells)
        
        if not horizontal_ips and _HORIZ_KW.search(flat):
            horizontal_ips = _parse_horizontal_table(grid)
        if not vertical_ips and _VERT_KW.search(flat):
            result = _parse_vertical_table(grid)
            vertical_ips   = result['vips']
            grade_sections = result['grades']
        if not superelevation and _SUPER_KW.search(flat):
            superelevation = _parse_superelevation_table(grid)

    if not horizontal_ips:
        warnings.append('No horizontal alignment table found.')
    if not vertical_ips:
        warnings.append('No vertical alignment table found.')
    if not superelevation:
        warnings.append('No superelevation table found - suoerelevation checks skipped.')

    all_chainages = (
        [ip['chainage'] for ip in horizontal_ips] +
        [ip['chainage'] for ip in vertical_ips]
    )

    return {
        'name': _extract_alignment_name(soup),
        'design_speed': _extract_design_speed(soup),
        'horizontal_ips': horizontal_ips,
        'vertical_ips':  vertical_ips,
        'grade_sections': grade_sections,
        'superelevation': superelevation,
        'start_chainage': min(all_chainages) if all_chainages else 0,
        'end_chainage': max(all_chainages) if all_chainages else 0,
        'warnings': warnings,
    }

# HELPERS

VALID_SPEEDS = {40, 50, 60, 70, 80, 90, 100}


def _parse_dms_angle(raw):
    clean = re.sub(r"[LlRr°'\"]+", ' ', raw).strip()
    parts = [float(x) for x in re.split(r'[\s\-:]+', clean) if x]
    deg = 0.0
    if len(parts) >= 1: deg += parts[0]
    if len(parts) >= 2: deg += parts[1] / 60
    if len(parts) >= 3: deg += parts[2] / 3600

    return deg

def _parse_chainage(raw):
    m = re.match(r'(\d+)\+(\d+(?:\.\d+)?)', raw)
    if m:
        return int(m.group(1)) * 1000 + float(m.group(2))
    cleaned = re.sub(r'[^\d.\-]', '', raw)
    try:
        return float(cleaned)
    except ValueError:
        return float('nan')

def _parse_num(raw):
    cleaned = re.sub(r'[^\d.\-]', '', str(raw))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def _table_to_grid(table):
    rows = table.find_all('tr')
    grid = []
    for row in rows:
        cells = row.find_all(['td', 'th'])
        grid.append([re.sub(r'\s+', ' ', c.get_text()).strip() for c in cells])
    return grid


def _find_col(headers, *candidates):
    for candidate in candidates:
        pattern = re.compile(candidate, re.IGNORECASE)
        for i, h in enumerate(headers):
            if pattern.search(h):
                return i
    return -1


# HORIZONTAL ALIGNMENT
_HORIZ_KW = re.compile(
    r'a\.\s*len|arc\s*len|defl.*angle|deflect|leading|trailing|tangent\s*len|curve\s*len',
    re.IGNORECASE
)

def _parse_horizontal_table(grid):
    header_idx = next(( i for i, row in enumerate(grid) if _HORIZ_KW.search(' '.join(row))), -1)

    if header_idx == -1:
        return []

    headers = grid[header_idx]
    c = {
        'id':         _find_col(headers, r'^pt$', r'ip\s*no', r'point\s*no', r'^no$', r'id'),
        'chainage':   _find_col(headers, r'raw\s*ch', r'^chainage$', r'chainage', r'chain', r'ch\.'),
        'deflection': _find_col(headers, r'defl.*angle', r'deflect', r'defl\.', r'delta'),
        'radius':     _find_col(headers, r'^radius$', r'^r$'),
        'arc':        _find_col(headers, r'a\.\s*len', r'^arc$', r'arc\s*len', r'curve\s*len'),
        'tangent':    _find_col(headers, r'tangent', r'^t$', r'tan\s*len'),
        'trans_in':   _find_col(headers, r'^leading$', r'trans.*in', r'spiral.*in', r'ls.*in', r'l1'),
        'trans_out':  _find_col(headers, r'^trailing$', r'trans.*out', r'spiral.*out', r'ls.*out', r'l2'),
        'clothoid':   _find_col(headers, r'clothoid', r'^a$', r'param'),
    }

    ips = []
    for row in grid[header_idx + 1:]:
        if len(row) < 3 or all(cell == '' for cell in row):
            continue
        chainage_raw = row[c['chainage']] if c['chainage'] != -1 else ''
        if not chainage_raw:
            continue
        chainage = _parse_chainage(chainage_raw)
        if math.isnan(chainage):
            continue

        radius = _parse_num(row[c['radius']] if c['radius'] != -1 else 0)
        if radius == 0:
            continue

        direction = 'L' if radius < 0 else 'R'
        radius = abs(radius)
        defl_angle = _parse_dms_angle(row[c['deflection']] if c['deflection'] != -1 else '0')

        ips.append({
            'id': row[c['id']] if c['id'] != -1 else f'IP{len(ips) + 1}',
            'chainage': chainage,
            'deflection_angle': defl_angle,
            'direction': direction,
            'radius': radius,
            'arc_length':           _parse_num(row[c['arc']])       if c['arc']       != -1 else 0,
            'tangent_length':       _parse_num(row[c['tangent']])   if c['tangent']   != -1 else 0,
            'transition_length_in': _parse_num(row[c['trans_in']])  if c['trans_in']  != -1 else 0,
            'transition_length_out':_parse_num(row[c['trans_out']]) if c['trans_out'] != -1 else 0,
            'clothoid_parameter':   _parse_num(row[c['clothoid']])  if c['clothoid']  != -1 else None,
        })
    return ips


# VERTICAL ALIGNMENT

_VERT_KW = re.compile(r'vc\s*type|k\s*value|vc\s*len|vertical\s*curve|v\.?c\.?l', re.IGNORECASE)

def _parse_vertical_table(grid):
    header_idx = next((i for i, row in enumerate(grid) if _VERT_KW.search(' '.join(row))), -1)

    if header_idx == -1:
        return {'vips': [], 'grades': []}

    headers = grid[header_idx]
    c = {
        'id':        _find_col(headers, r'^pt$', r'vip', r'ip\s*no', r'point', r'^no$'),
        'chainage':  _find_col(headers, r'raw\s*ch', r'^chainage$', r'chainage', r'chain', r'ch\.'),
        'level':     _find_col(headers, r'^height$', r'level', r'elev', r'rl', r'height'),
        'vc_type':   _find_col(headers, r'vc\s*type'),
        'k_value':   _find_col(headers, r'k\s*val', r'^k$'),
        'vc_radius': _find_col(headers, r'^radius$'),
        'vc_length': _find_col(headers, r'^length$', r'vc\s*len', r'vcl', r'curve\s*len', r'l\s*\(vc\)'),
        'grade_in':  _find_col(headers, r'grade\s*in', r'in\s*grade', r'g1', r'incoming'),
        'grade_out': _find_col(headers, r'grade\s*out', r'out\s*grade', r'g2', r'outgoing'),
    }

    raw = []
    for row in grid[header_idx + 1:]:
        if len(row) < 3 or all(cell == '' for cell in row):
            continue
        chainage_raw = row[c['chainage']] if c['chainage'] != -1 else ''
        if not chainage_raw:
            continue
        chainage = _parse_chainage(chainage_raw)
        if math.isnan(chainage):
            continue
        raw.append({
            'id':          row[c['id']] if c['id'] != -1 else f'VIP{len(raw) + 1}',
            'chainage':    chainage,
            'level':       _parse_num(row[c['level']])     if c['level']     != -1 else 0,
            'vc_type_str': row[c['vc_type']].strip()       if c['vc_type']   != -1 else '',
            'k_value':     _parse_num(row[c['k_value']])   if c['k_value']   != -1 else 0,
            'vc_radius':   _parse_num(row[c['vc_radius']]) if c['vc_radius'] != -1 else 0,
            'vc_length':   _parse_num(row[c['vc_length']]) if c['vc_length'] != -1 else 0,
            'grade_in':    _parse_num(row[c['grade_in']])  if c['grade_in']  != -1 else 0,
            'grade_out':   _parse_num(row[c['grade_out']]) if c['grade_out'] != -1 else 0,
        })

    if c['grade_in'] == -1 and len(raw) >= 2:
        for i, vip in enumerate(raw):
            prev = raw[i-1] if i >0 else None
            nxt = raw[i+1] if i < len(raw) - 1 else None
            grade_from_prev = (vip['level'] - prev['level']) / (vip['chainage'] - prev['chainage']) * 100 if prev else None
            grade_to_next   = (nxt['level']  - vip['level'])  / (nxt['chainage']  - vip['chainage'])  * 100 if nxt  else None
            vip['grade_in']  = grade_from_prev if grade_from_prev is not None else (grade_to_next or 0)
            vip['grade_out'] = grade_to_next   if grade_to_next   is not None else (grade_from_prev or 0)

    vips = []
    for v in raw:
        vc_type_str = v['vc_type_str'].lower()
        vc_type = 'none'
        if v['vc_length'] > 0 and vc_type_str != 'line':
            if v['vc_radius'] != 0:
                vc_type = 'sag' if v['vc_radius'] > 0 else 'crest'
            else:
                vc_type = 'crest' if v['grade_out'] < v['grade_in'] else 'sag'
        vips.append({
            'id':           v['id'],
            'chainage':     v['chainage'],
            'level':        v['level'],
            'grade_in':     v['grade_in'],
            'grade_out':    v['grade_out'],
            'grade_change': abs(v['grade_out'] - v['grade_in']),
            'k_value':      v['k_value'],
            'vc_length':    v['vc_length'],
            'vc_type':      vc_type,
        })

    grades = []
    for i in range(len(vips) - 1):
        grades.append({
            'from_chainage': vips[i]['chainage'],
            'to_chainage':   vips[i + 1]['chainage'],
            'grade':         vips[i]['grade_out'],
        })

    return {'vips': vips, 'grades': grades}

_SUPER_KW = re.compile(
    r'superelevat|crossfall|cross\s*fall|left.*rate|right.*rate',
    re.IGNORECASE
)

def _parse_superelevation_table(grid):

    # populate later when super reports are available.

    return []

def _extract_design_speed(soup):
    text = soup.get_text()
    m = re.search(r'design\s*speed[:\s]+(\d+)\s*km',text, re.IGNORECASE)
    if m:
        v = int(m.group(1))
        if v in VALID_SPEEDS:
            return v
    return None
    

def _extract_alignment_name(soup):
    h3 = soup.find('h3')
    if h3:
        text = h3.get_text().strip()
        m = re.match(r'cen\s+([^-\s>]+)', text, re.IGNORECASE)
        if m:
            return m.group(1)
        return text
    title = soup.find('title')
    if title:
        return title.get_text().strip()
    for tag in ['h1','h2']:
        el = soup.find(tag)
        if el:
            return el.get_text().strip()
    return 'Unknown Alignment'

