#!/usr/bin/env python3
"""Dependency-free PNG reading, writing and scaling.

The classroom Mac runs this scanner offline with a stock Python 3, so this
module deliberately uses nothing outside the standard library (zlib, struct,
hashlib). It covers what MicroStudio exports actually contain: non-interlaced
PNG in every colour type and bit depth. Files that are not decodable PNG
(students often rename JPEG/WebP downloads to .png) are reported by sniff()
so callers can skip them rather than crash.
"""

import hashlib
import struct
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class UnsupportedImage(Exception):
    """Raised when a file is not a PNG this module can decode."""


def sniff(data):
    """Return the real image format of a byte string, ignoring its filename."""
    if data[:8] == PNG_MAGIC:
        return "png"
    if data[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data[:2] == b"BM":
        return "bmp"
    return None


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _chunks(data):
    offset = 8
    while offset + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[offset:offset + 8])
        body = data[offset + 8:offset + 8 + length]
        if len(body) != length:
            raise UnsupportedImage("truncated PNG chunk")
        yield kind, body
        offset += 12 + length


def read_header(data):
    """Return (width, height) from IHDR without decoding pixels."""
    if data[:8] != PNG_MAGIC or len(data) < 26:
        raise UnsupportedImage("not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if width == 0 or height == 0:
        raise UnsupportedImage("zero-sized PNG")
    return width, height


_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


def _unfilter(raw, width, height, bit_depth, channels):
    stride = (width * channels * bit_depth + 7) // 8
    step = max(1, (channels * bit_depth) // 8)
    expected = (stride + 1) * height
    if len(raw) < expected:
        raise UnsupportedImage("PNG pixel data is short")
    out = bytearray(stride * height)
    previous = bytearray(stride)
    position = 0
    for row in range(height):
        filter_type = raw[position]
        position += 1
        line = bytearray(raw[position:position + stride])
        position += stride
        if filter_type == 1:
            for i in range(step, stride):
                line[i] = (line[i] + line[i - step]) & 0xFF
        elif filter_type == 2:
            for i in range(stride):
                line[i] = (line[i] + previous[i]) & 0xFF
        elif filter_type == 3:
            for i in range(stride):
                left = line[i - step] if i >= step else 0
                line[i] = (line[i] + ((left + previous[i]) >> 1)) & 0xFF
        elif filter_type == 4:
            for i in range(stride):
                left = line[i - step] if i >= step else 0
                upleft = previous[i - step] if i >= step else 0
                up = previous[i]
                p = left + up - upleft
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - upleft)
                if pa <= pb and pa <= pc:
                    predictor = left
                elif pb <= pc:
                    predictor = up
                else:
                    predictor = upleft
                line[i] = (line[i] + predictor) & 0xFF
        elif filter_type != 0:
            raise UnsupportedImage(f"unknown PNG filter {filter_type}")
        out[row * stride:(row + 1) * stride] = line
        previous = line
    return out, stride


def _samples(row_bytes, width, channels, bit_depth):
    """Expand one unfiltered row into a flat list of integer samples."""
    count = width * channels
    if bit_depth == 8:
        return list(row_bytes[:count])
    if bit_depth == 16:
        return [row_bytes[i * 2] for i in range(count)]
    values = []
    mask = (1 << bit_depth) - 1
    per_byte = 8 // bit_depth
    for index in range(count):
        byte = row_bytes[index // per_byte]
        shift = 8 - bit_depth * (index % per_byte + 1)
        values.append((byte >> shift) & mask)
    return values


def decode(data):
    """Decode a non-interlaced PNG into (width, height, RGBA bytearray)."""
    width, height = read_header(data)
    bit_depth, colour_type, compression, filter_method, interlace = struct.unpack(
        ">BBBBB", data[24:29]
    )
    if compression != 0 or filter_method != 0:
        raise UnsupportedImage("unsupported PNG compression or filter method")
    if interlace != 0:
        raise UnsupportedImage("interlaced PNG is not supported")
    if colour_type not in _CHANNELS:
        raise UnsupportedImage(f"unsupported PNG colour type {colour_type}")

    channels = _CHANNELS[colour_type]
    palette = b""
    transparency = b""
    compressed = bytearray()
    for kind, body in _chunks(data):
        if kind == b"PLTE":
            palette = body
        elif kind == b"tRNS":
            transparency = body
        elif kind == b"IDAT":
            compressed += body
        elif kind == b"IEND":
            break
    if not compressed:
        raise UnsupportedImage("PNG has no image data")
    try:
        raw = zlib.decompress(bytes(compressed))
    except zlib.error as error:
        raise UnsupportedImage(f"corrupt PNG stream ({error})") from error

    rows, stride = _unfilter(raw, width, height, bit_depth, channels)

    # Fast paths for the two layouts MicroStudio actually exports. The generic
    # loop below is correct for everything but is far too slow on large images.
    if bit_depth == 8 and colour_type == 6:
        return width, height, bytearray(rows)
    if bit_depth == 8 and colour_type == 2 and not transparency:
        rgba = bytearray(width * height * 4)
        rgba[3::4] = b"\xff" * (width * height)
        rgba[0::4] = rows[0::3]
        rgba[1::4] = rows[1::3]
        rgba[2::4] = rows[2::3]
        return width, height, rgba

    maximum = (1 << bit_depth) - 1
    scale = 255 / maximum if maximum else 1
    rgba = bytearray(width * height * 4)

    # Colour keys from tRNS, for the colour types that support them.
    key = None
    if transparency:
        if colour_type == 0:
            key = (struct.unpack(">H", transparency[:2])[0],)
        elif colour_type == 2:
            key = struct.unpack(">HHH", transparency[:6])

    for row in range(height):
        values = _samples(rows[row * stride:(row + 1) * stride], width, channels, bit_depth)
        base = row * width * 4
        for column in range(width):
            offset = column * channels
            if colour_type == 6:
                r, g, b, a = values[offset:offset + 4]
            elif colour_type == 2:
                r, g, b = values[offset:offset + 3]
                a = maximum
                if key and (r, g, b) == key:
                    a = 0
            elif colour_type == 4:
                r = g = b = values[offset]
                a = values[offset + 1]
            elif colour_type == 0:
                r = g = b = values[offset]
                a = 0 if key and (r,) == key else maximum
            else:  # palette
                index = values[offset]
                if (index + 1) * 3 > len(palette):
                    raise UnsupportedImage("PNG palette index out of range")
                r, g, b = palette[index * 3:index * 3 + 3]
                alpha = transparency[index] if index < len(transparency) else 255
                position = base + column * 4
                rgba[position:position + 4] = bytes((r, g, b, alpha))
                continue
            position = base + column * 4
            rgba[position] = round(r * scale)
            rgba[position + 1] = round(g * scale)
            rgba[position + 2] = round(b * scale)
            rgba[position + 3] = round(a * scale)
    return width, height, rgba


def encode(width, height, rgba):
    """Encode an RGBA bytearray as an 8-bit RGBA PNG."""
    stride = width * 4
    raw = bytearray()
    for row in range(height):
        raw.append(0)
        raw += rgba[row * stride:(row + 1) * stride]

    def chunk(kind, body):
        payload = kind + body
        return struct.pack(">I", len(body)) + payload + struct.pack(
            ">I", zlib.crc32(payload) & 0xFFFFFFFF
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        PNG_MAGIC
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def scale(rgba, width, height, new_width, new_height):
    """Resample RGBA pixels.

    Downscaling uses an alpha-weighted box average so photographic sprites stay
    smooth; upscaling uses nearest neighbour so pixel art stays crisp instead of
    turning to mush.
    """
    if (new_width, new_height) == (width, height):
        return bytearray(rgba)
    out = bytearray(new_width * new_height * 4)
    shrinking = new_width < width or new_height < height
    for y in range(new_height):
        y0 = y * height // new_height
        y1 = max(y0 + 1, (y + 1) * height // new_height)
        for x in range(new_width):
            x0 = x * width // new_width
            x1 = max(x0 + 1, (x + 1) * width // new_width)
            position = (y * new_width + x) * 4
            if not shrinking:
                source = ((y0 * width) + x0) * 4
                out[position:position + 4] = rgba[source:source + 4]
                continue
            # Premultiply by alpha so transparent pixels do not bleed colour.
            red = green = blue = alpha = 0
            count = 0
            for sy in range(y0, y1):
                row = sy * width
                for sx in range(x0, x1):
                    source = (row + sx) * 4
                    a = rgba[source + 3]
                    red += rgba[source] * a
                    green += rgba[source + 1] * a
                    blue += rgba[source + 2] * a
                    alpha += a
                    count += 1
            if alpha:
                out[position] = min(255, red // alpha)
                out[position + 1] = min(255, green // alpha)
                out[position + 2] = min(255, blue // alpha)
            out[position + 3] = alpha // count if count else 0
    return out


def fit_square(rgba, width, height, size, background):
    """Scale to fit inside `size` preserving aspect ratio, pad with `background`.

    Never distorts: the source keeps its proportions and the leftover space is
    filled with a plain colour.
    """
    ratio = min(size / width, size / height)
    new_width = max(1, min(size, round(width * ratio)))
    new_height = max(1, min(size, round(height * ratio)))
    scaled = scale(rgba, width, height, new_width, new_height)
    canvas = bytearray(bytes(tuple(background) + (255,)) * (size * size))
    offset_x = (size - new_width) // 2
    offset_y = (size - new_height) // 2
    for y in range(new_height):
        target = ((y + offset_y) * size + offset_x) * 4
        source = y * new_width * 4
        for x in range(new_width):
            a = scaled[source + 3]
            if a == 255:
                canvas[target:target + 4] = scaled[source:source + 4]
            elif a:
                for channel in range(3):
                    over = scaled[source + channel] * a
                    under = canvas[target + channel] * (255 - a)
                    canvas[target + channel] = (over + under) // 255
            target += 4
            source += 4
    return canvas


def dominant_background(rgba, width, height):
    """Pick a plain backdrop colour: the sprite's own average, darkened.

    Keeps generated icons feeling like they belong to their game rather than
    sitting on an arbitrary swatch.
    """
    red = green = blue = weight = 0
    for position in range(0, width * height * 4, 4):
        a = rgba[position + 3]
        if a < 8:
            continue
        red += rgba[position] * a
        green += rgba[position + 1] * a
        blue += rgba[position + 2] * a
        weight += a
    if not weight:
        return (43, 57, 69)
    average = (red // weight, green // weight, blue // weight)
    # Darken towards the hub's panel tone so the sprite reads against it.
    return tuple(max(18, min(90, round(channel * 0.42))) for channel in average)


# A 5x7 bitmap font, enough to draw initials on the last-resort placeholder
# without shipping a font file or a rendering library.
_FONT = {
    "A": (0x04, 0x0A, 0x11, 0x11, 0x1F, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
}

_GLYPH_WIDTH = 5
_GLYPH_HEIGHT = 7


def placeholder(size, text, background, foreground):
    """Draw a filled circle carrying up to two initials."""
    letters = [character for character in text.upper() if character in _FONT][:2] or ["?"]
    canvas = bytearray(bytes(tuple(background) + (255,)) * (size * size))

    # Circle, slightly inset, with a lighter fill than the square backdrop.
    centre = (size - 1) / 2
    radius = size * 0.42
    disc = tuple(min(255, round(channel * 0.55 + 46)) for channel in background)
    for y in range(size):
        dy = y - centre
        for x in range(size):
            dx = x - centre
            if dx * dx + dy * dy <= radius * radius:
                position = (y * size + x) * 4
                canvas[position:position + 4] = bytes(disc + (255,))

    # Initials, scaled up from the 5x7 bitmap font and centred on the circle.
    gap = 1
    columns = len(letters) * _GLYPH_WIDTH + (len(letters) - 1) * gap
    pixel = max(1, min(size // (columns + 2), size // (_GLYPH_HEIGHT + 2)))
    text_width = columns * pixel
    text_height = _GLYPH_HEIGHT * pixel
    start_x = (size - text_width) // 2
    start_y = (size - text_height) // 2
    ink = bytes(tuple(foreground) + (255,))
    for index, letter in enumerate(letters):
        glyph = _FONT[letter]
        origin = start_x + index * (_GLYPH_WIDTH + gap) * pixel
        for row in range(_GLYPH_HEIGHT):
            bits = glyph[row]
            for column in range(_GLYPH_WIDTH):
                if not (bits >> (_GLYPH_WIDTH - 1 - column)) & 1:
                    continue
                for dy in range(pixel):
                    y = start_y + row * pixel + dy
                    base = (y * size + origin + column * pixel) * 4
                    for dx in range(pixel):
                        canvas[base + dx * 4:base + dx * 4 + 4] = ink
    return canvas
