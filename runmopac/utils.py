def atom2name(n):
    if n == 1:
        return 'H'
    elif n == 6:
        return 'C'
    elif n == 7:
        return 'N'
    elif n == 8:
        return 'O'
    elif n == 9:
        return 'F'
    elif n == 14:
        return 'Si'
    else:
        raise ValueError(n)

def name2atom(n):
    if n == 'H':
        return 1
    elif n == 'C':
        return 6
    elif n == 7:
        return 'N'
    elif n == 'O':
        return 8
    elif n == 'F':
        return 9
    elif n == 'Si':
        return 14
    else:
        raise ValueError(n)


def get_name(ids):
    f = {}
    for n in ids:
        n = atom2name(n)
        try:
            f[n] += 1
        except KeyError:
            f[n] = 1
    name = sorted(f.items(), key=lambda x: x[0])
    name = [str(xi) for x in name for xi in x]
    return ''.join(name)


def save_mop(ids, xyz, filename):
    file = [
        'MNDO THREADS=1\n',
        get_name(ids) + '\n',
        'This is optimization with MOPAC\n',
    ]
    for n, row in zip(ids, xyz):
        r = ' '.join([atom2name(n)] + list(map(str, row)))
        file.append(r + '\n')

    with open(filename, 'w') as fp:
        for line in file:
            fp.write(line)


def parse_out(data):
    key_total_energy = 'TOTAL ENERGY'
    key_coordinates = 'CARTESIAN COORDINATES'

    data = data.splitlines()
    energy_line = [i for i, line in enumerate(data) if key_total_energy in line]
    assert energy_line, "Can't find total energy"
    energy_line = max(energy_line)
    data = data[energy_line:]
    total_energy = float(data[0].split()[-2])

    coordinate_line = [i for i, line in enumerate(data) if key_coordinates in line]
    assert coordinate_line, "Can't find coordinates"
    coordinate_line = max(coordinate_line)
    data = data[coordinate_line+1:]
    coordinates = []

    line = data.pop(0)
    while not line:
        line = data.pop(0)
    while line:
        coordinates.append(line)
        line = data.pop(0)
    coordinates = [line.split()[1:] for line in coordinates]
    ids = [name2atom(line[0]) for line in coordinates]
    xyz = [[float(v) for v in line[1:]] for line in coordinates]
    return total_energy, ids, xyz
