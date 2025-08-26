from typing import Iterable, Tuple

def summarize(data: Iterable[float]) -> Tuple[float, float, float]:
    """
    Return (min, max, mean) for an iterable of floats.
    Raises ValueError if data is empty.
    """
    it = iter(data)
    try:
        first = next(it)
    except StopIteration:
        raise ValueError("summarize() requires at least one number")

    mn = mx = float(first)
    total = float(first)
    n = 1

    for v in it:
        v = float(v)
        if v < mn:
            mn = v
        if v > mx:
            mx = v
        total += v
        n += 1

    return mn, mx, (total / n)