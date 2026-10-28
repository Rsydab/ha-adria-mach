"""Tilt angles from the unit's accelerometer.

The unit reports gravity as (x, y, z) in g. With a reference vector r taken
when the vehicle was level, the tilt around the unit's two horizontal axes is
the component of the current gravity vector along those axes, orthogonalised
against r. Without a reference the X axis is assumed vertical.
"""

from __future__ import annotations

import math
from typing import Any

DEFAULT_REFERENCE = (1.0, 0.0, 0.0)
_AXIS_Y = (0.0, 1.0, 0.0)
_AXIS_Z = (0.0, 0.0, 1.0)


def _norm(v: tuple[float, float, float]) -> tuple[float, float, float] | None:
    length = math.sqrt(sum(c * c for c in v))
    if length < 1e-6:
        return None
    return (v[0] / length, v[1] / length, v[2] / length)


def _dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _orthogonalise(axis, *against):
    v = list(axis)
    for base in against:
        d = _dot(v, base)
        v = [v[i] - d * base[i] for i in range(3)]
    return _norm((v[0], v[1], v[2]))


def accel_vector(data: dict[str, Any]) -> tuple[float, float, float] | None:
    try:
        return (
            float(data["ACCELERATION_X"]),
            float(data["ACCELERATION_Y"]),
            float(data["ACCELERATION_Z"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def tilt_angles(
    acc: tuple[float, float, float],
    reference: tuple[float, float, float] | list[float] | None,
) -> tuple[float, float] | None:
    """Return (tilt along Y axis, tilt along Z axis) in degrees, or None."""
    g = _norm(acc)
    ref = _norm(tuple(reference) if reference else DEFAULT_REFERENCE)  # type: ignore[arg-type]
    if g is None or ref is None:
        return None
    axis_y = _orthogonalise(_AXIS_Y, ref)
    if axis_y is None:
        axis_y = _orthogonalise(_AXIS_Z, ref)
    axis_z = _orthogonalise(_AXIS_Z, ref, axis_y) if axis_y else None
    if axis_y is None or axis_z is None:
        return None
    tilt_y = math.degrees(math.asin(max(-1.0, min(1.0, _dot(g, axis_y)))))
    tilt_z = math.degrees(math.asin(max(-1.0, min(1.0, _dot(g, axis_z)))))
    return (round(tilt_y, 1), round(tilt_z, 1))
