import math
import re


def load_fleet(path, require_runnable=True):
    import yaml
    with open(path, encoding='utf-8') as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('schema_version must be 1')
    devices = data.get('devices')
    if not isinstance(devices, list) or not devices:
        raise ValueError('non-empty devices list required')
    ids, namespaces = set(), set()
    for item in devices:
        if not isinstance(item, dict):
            raise ValueError('device must be a mapping')
        name, ns = item.get('device_id'), item.get('namespace')
        if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9_]*', name):
            raise ValueError('device_id must match [a-z][a-z0-9_]*')
        if not isinstance(ns, str) or not re.fullmatch(r'(?:/[a-z][a-z0-9_]*)+', ns):
            raise ValueError('namespace must be an absolute ROS name')
        if name in ids or ns in namespaces:
            raise ValueError('duplicate device_id or namespace')
        ids.add(name)
        namespaces.add(ns)
        if item.get('type') not in ('amr', 'cobot', 'equipment'):
            raise ValueError('unknown device type')
        pose = item.get('initial_position', [0.0, 0.0])
        if (not isinstance(pose, list) or len(pose) != 2
                or not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                           and math.isfinite(v) for v in pose)):
            raise ValueError('initial_position requires 2 finite numbers')
        if require_runnable and item['type'] != 'amr':
            raise ValueError('Only AMR is implemented; target fleet is a planning file')
        speed = item.get('speed_mps', 1.0)
        if (not isinstance(speed, (int, float)) or isinstance(speed, bool)
                or not math.isfinite(speed) or speed <= 0):
            raise ValueError('speed_mps must be positive finite')
    return data
