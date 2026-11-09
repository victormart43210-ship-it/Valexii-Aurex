"""Small, parameterised image measurements. None of these identify a letter."""

from __future__ import annotations


def grayscale(pixels: list[tuple[int, int, int]]) -> list[int]:
    """ITU-R BT.601 integer weights. This is a channel mix, not a recovery."""
    return [(pixel[0] * 299 + pixel[1] * 587 + pixel[2] * 114) // 1000 for pixel in pixels]


def channel(pixels: list[tuple[int, int, int]], index: int) -> list[int]:
    return [pixel[index] for pixel in pixels]


def stretch(values: list[int], low_percent: int, high_percent: int) -> list[int]:
    ordered = sorted(values)
    last = len(ordered) - 1
    low = ordered[max(0, min(last, last * low_percent // 100))]
    high = ordered[max(0, min(last, last * high_percent // 100))]
    if high <= low:
        return list(values)
    span = high - low
    return [max(0, min(255, (value - low) * 255 // span)) for value in values]


def box_mean(values: list[int], width: int, height: int, radius: int) -> list[int]:
    """A separable box mean. The window is (2*radius+1) pixels on each axis."""
    if radius < 1:
        return list(values)
    horizontal = [0] * len(values)
    for y in range(height):
        row = y * width
        for x in range(width):
            total = 0
            count = 0
            for offset in range(-radius, radius + 1):
                sample = x + offset
                if 0 <= sample < width:
                    total += values[row + sample]
                    count += 1
            horizontal[row + x] = total // count
    out = [0] * len(values)
    for y in range(height):
        for x in range(width):
            total = 0
            count = 0
            for offset in range(-radius, radius + 1):
                sample = y + offset
                if 0 <= sample < height:
                    total += horizontal[sample * width + x]
                    count += 1
            out[y * width + x] = total // count
    return out


def darker_than_background(values: list[int], background: list[int], margin: int) -> list[int]:
    """Ink candidate is 0. Background is 255. A dark pixel is not a character."""
    return [0 if values[index] + margin < background[index] else 255 for index in range(len(values))]


def median3(values: list[int], width: int, height: int) -> list[int]:
    out = [0] * len(values)
    for y in range(height):
        for x in range(width):
            window: list[int] = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    sy = min(height - 1, max(0, y + dy))
                    sx = min(width - 1, max(0, x + dx))
                    window.append(values[sy * width + sx])
            window.sort()
            out[y * width + x] = window[4]
    return out


def gradient(values: list[int], width: int, height: int) -> list[int]:
    out = [0] * len(values)
    for y in range(height):
        for x in range(width):
            left = values[y * width + max(0, x - 1)]
            right = values[y * width + min(width - 1, x + 1)]
            up = values[max(0, y - 1) * width + x]
            down = values[min(height - 1, y + 1) * width + x]
            magnitude = abs(right - left) + abs(down - up)
            out[y * width + x] = min(255, magnitude)
    return out


def close_ink(binary: list[int], width: int, height: int) -> list[int]:
    """Dilate then erode ink (value 0). This can join noise. It does not read it."""
    dilated = _dilate_ink(binary, width, height)
    return _erode_ink(dilated, width, height)


def _dilate_ink(binary: list[int], width: int, height: int) -> list[int]:
    out = [255] * len(binary)
    for y in range(height):
        for x in range(width):
            ink = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    sy = y + dy
                    sx = x + dx
                    if 0 <= sy < height and 0 <= sx < width and binary[sy * width + sx] == 0:
                        ink = True
            out[y * width + x] = 0 if ink else 255
    return out


def _erode_ink(binary: list[int], width: int, height: int) -> list[int]:
    out = [255] * len(binary)
    for y in range(height):
        for x in range(width):
            if binary[y * width + x] != 0:
                continue
            keep = True
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    sy = y + dy
                    sx = x + dx
                    if not (0 <= sy < height and 0 <= sx < width) or binary[sy * width + sx] != 0:
                        keep = False
            out[y * width + x] = 0 if keep else 255
    return out


def components(
    binary: list[int], width: int, height: int, *, minimum: int, limit: int
) -> list[dict[str, int]]:
    """4-connected groups of ink pixels. Small groups are discarded as noise."""
    seen = bytearray(len(binary))
    found: list[dict[str, int]] = []
    for start in range(len(binary)):
        if binary[start] != 0 or seen[start]:
            continue
        stack = [start]
        seen[start] = 1
        count = 0
        min_x = width
        min_y = height
        max_x = 0
        max_y = 0
        while stack:
            current = stack.pop()
            count += 1
            x = current % width
            y = current // width
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            for nxt in (current - 1, current + 1, current - width, current + width):
                if nxt < 0 or nxt >= len(binary) or seen[nxt] or binary[nxt] != 0:
                    continue
                if abs((nxt % width) - x) + abs((nxt // width) - y) != 1:
                    continue
                seen[nxt] = 1
                stack.append(nxt)
        if count >= minimum:
            found.append(
                {
                    "x0": min_x,
                    "y0": min_y,
                    "x1": max_x + 1,
                    "y1": max_y + 1,
                    "pixels": count,
                }
            )
    found.sort(key=lambda item: (-item["pixels"], item["y0"], item["x0"]))
    return found[:limit]


def crop(values: list[int], width: int, box: dict[str, int]) -> tuple[list[int], int, int]:
    cropped: list[int] = []
    for y in range(box["y0"], box["y1"]):
        row = y * width
        cropped.extend(values[row + box["x0"] : row + box["x1"]])
    return cropped, box["x1"] - box["x0"], box["y1"] - box["y0"]
