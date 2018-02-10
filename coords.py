# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Logic for dealing with coordinates.

This introduces some helpers and terminology that are used throughout MiniGo.

MiniGo Coordinate: This is a tuple of the form (row, column) that is indexed
    starting out at (0, 0) from the upper-left.
Flattened Coordinate: this is a number ranging from 0 - N^2 (so N^2+1
    possible values). The extra value N^2 is used to mark a 'pass' move.
SGF Coordinate: Coordinate used for SGF serialization format. Coordinates use
    two-letter pairs having the form (column, row) indexed from the upper-left
    where 0, 0 = 'aa'.
KGS Coordinate: Human-readable coordinate string indexed from bottom left, with
    the first character a capital letter for the column and the second a number
    from 1-19 for the row. Note that KGS chooses to skip the letter 'I' due to
    its similarity with 'l' (lowercase 'L').
PYGTP Coordinate: Tuple coordinate indexed starting at 1,1 from bottom-left
    in the format (column, row)

So, for a 19x19,

Coord Type      upper_left      upper_right     pass
-------------------------------------------------------
minigo coord    (0, 0)          (0, 18)         None
flat            0               18              361
SGF             'aa'            'sa'            ''
KGS             'A19'           'T19'           'pass'
pygtp           (1, 19)         (19, 19)        (0, 0)
"""

import gtp

import go

MINIGO = 'minigo'
FLAT = 'flat'
SGF = 'sgf'
KGS = 'kgs'
PYGTP = 'pygtp'

# We provide more than 19 entries here in case of boards larger than 19 x 19.
_SGF_COLUMNS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
_KGS_COLUMNS = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'


def from_flat(coord):
    """Converts from a flattened coordinate to a Minigo coordinate."""
    if flat == go.N * go.N:
        return None
    return divmod(flat, go.N)


def to_flat(coord):
    """Converts from a MiniGo coordinate to a flattened coordinate."""
    if coord is None:
        return go.N * go.N
    return go.N * coord[0] + coord[1]


def from_sgf(sgfc):
    if sgfc is None or sgfc == '':
        return None
    return _SGF_COLUMNS.index(sgfc[1]), _SGF_COLUMNS.index(sgfc[0])


def to_sgf(coord):
    if coord is None:
        return ''
    return _SGF_COLUMNS[coord[1]] + _SGF_COLUMNS[coord[0]]


def from_kgs(kgsc):
    if kgsc == 'pass':
        return None
    kgsc = kgsc.upper()
    col = _KGS_COLUMNS.index(kgsc[0])
    row_from_bottom = int(kgsc[1:])
    return go.N - row_from_bottom, col


def to_kgs(coord):
    if coord is None:
        return 'pass'
    y, x = coord
    return '{}{}'.format(_KGS_COLUMNS[x], go.N - y)


def from_pygtp(pygtpc):
    # GTP has a notion of both a Pass and a Resign, both of which are mapped to
    # None, so the conversion is not precisely bijective.
    if pygtpc in (gtp.PASS, gtp.RESIGN):
        return None
    return go.N - pygtpc[1], pygtpc[0] - 1


def to_pygtp(coord):
    if coord is None:
        return gtp.PASS
    return coord[1] + 1, go.N - coord[0]


def convert(coord, from_type, to_type):
    """Converts from one coordinate format to another.

    Args:
        coord: The coordinates to convert.
        from_type: The coordinate type to convert from (e.g., MINIGO).
        to_type: The coordinate type to convert to (e.g., SGF).
    """

    # First, convert to MiniGo format.
    if from_type == FLAT:
        coord = from_flat(coord)
    elif from_type == SGF:
        coord = from_sgf(coord)
    elif from_type == KGS:
        coord = from_kgs(coord)
    elif from_type == PYGTP:
        coord = from_pygtp(coord)

    # Now convert to the desired format.
    if to_type == FLAT:
        coord = to_flat(coord)
    elif to_type == SGF:
        coord = to_sgf(coord)
    elif to_type == KGS:
        coord = to_kgs(coord)
    elif to_type == PYGTP:
        coord = to_pygtp(coord)

    return coord
