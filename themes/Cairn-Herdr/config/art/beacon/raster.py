"""A small RGB raster board with procedural paper, dry brush and PNG output."""

from contextlib import contextmanager
from math import ceil, cos, floor, hypot, radians, sin
from pathlib import Path
from random import Random
import struct
import zlib


def smooth(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3.0 - 2.0 * value)


def mix(first, second, amount):
    return tuple(a + (b - a) * amount for a, b in zip(first, second))


def paper(x, y):
    """Coordinate-based grain lets the same texture show through every layer."""
    bits = ((x * 374761393 + y * 668265263) ^ (x * y * 2246822519)) & 0xFFFFFFFF
    bits = ((bits ^ (bits >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((bits ^ (bits >> 16)) & 255) / 255


class Noise:
    def __init__(self, columns, rows, seed):
        rng = Random(seed)
        self.columns, self.rows = columns, rows
        self.values = [[rng.random() for _ in range(columns + 1)] for _ in range(rows + 1)]

    def __call__(self, x, y):
        x = min(max(0, x), 0.999999) * self.columns
        y = min(max(0, y), 0.999999) * self.rows
        ix, iy = int(x), int(y)
        dx, dy = smooth(x - ix), smooth(y - iy)
        a, b = self.values[iy], self.values[iy + 1]
        top = a[ix] + (a[ix + 1] - a[ix]) * dx
        bottom = b[ix] + (b[ix + 1] - b[ix]) * dx
        return top + (bottom - top) * dy


class Canvas:
    def __init__(self, width, height, samples=1):
        if width < 1 or height < 1:
            raise ValueError("Canvas dimensions must be positive")
        if not 1 <= samples <= 8:
            raise ValueError("Choose between one and eight scanline samples")
        self.width, self.height = width, height
        self.samples = samples
        self.pixels = bytearray(3 * width * height)
        self._clip = None

    def field(self, color_at):
        """Paint the ground from a function of normalized coordinates."""
        for y in range(self.height):
            v = (y + 0.5) / self.height
            for x in range(self.width):
                u = (x + 0.5) / self.width
                grain = (paper(x, y) - 0.5) * 5
                rgb = color_at(u, v)
                i = 3 * (y * self.width + x)
                for channel, value in enumerate(rgb):
                    self.pixels[i + channel] = int(min(255, max(0, value + grain + 0.5)))

    def blend(self, x, y, rgb, alpha):
        if not (0 <= x < self.width and 0 <= y < self.height) or alpha <= 0:
            return
        index = y * self.width + x
        alpha = min(alpha, 1)
        if self._clip is not None:
            alpha *= self._clip[index] / 255
            if not alpha:
                return
        offset = 3 * index
        for c in range(3):
            base = self.pixels[offset + c]
            self.pixels[offset + c] = round(base + (rgb[c] - base) * alpha)

    def dab(self, x, y, rx, ry, rgb, alpha, dry=0.25, angle=0):
        """Lay down a feathered elliptical mark rotated in pixel space."""
        x, y = x*self.width, y*self.height
        rx, ry = max(rx*self.width, 0.7), max(ry*self.height, 0.7)
        c, s = cos(radians(angle)), sin(radians(angle))
        reach_x, reach_y = hypot(rx*c, ry*s), hypot(rx*s, ry*c)
        for py in range(max(0, floor(y-reach_y)), min(self.height, ceil(y+reach_y))):
            dy = py + .5 - y
            for px in range(max(0, floor(x-reach_x)), min(self.width, ceil(x+reach_x))):
                dx = px + .5 - x
                across = (dx*c + dy*s)/rx
                along = (dy*c - dx*s)/ry
                distance = across*across + along*along
                if distance < 1:
                    edge = min(1, (1-distance)*2.8)
                    tooth = 1 - dry + dry*paper(px, py)
                    self.blend(px, py, rgb, alpha*edge*tooth)

    def stroke(self, points, rgb, width, alpha, dry=0.25):
        """Join samples with overlapping brush marks at increasing taper."""
        distances = [hypot((b[0]-a[0])*self.width, (b[1]-a[1])*self.height)
                     for a, b in zip(points, points[1:])]
        length = sum(distances)
        if length == 0:
            return
        traveled = 0
        radius = width * self.width
        for a, b, distance in zip(points, points[1:], distances):
            steps = max(1, ceil(distance / max(1, radius * 0.9)))
            for step in range(steps):
                t = step / steps
                along = (traveled + t * distance) / length
                taper = 0.40 + 0.60 * min(1, (1 - along) * 4)
                x, y = mix(a, b, t)
                self.dab(x, y, width*taper, width*taper*self.width/self.height, rgb, alpha, dry)
            traveled += distance

    def curve(self, start, control_a, control_b, end, rgb, width, alpha, dry=0.25):
        """Paint a cubic Bézier, sampling according to its pixel length."""
        controls = (start, control_a, control_b, end)
        length = sum(hypot((b[0]-a[0])*self.width, (b[1]-a[1])*self.height)
                     for a,b in zip(controls, controls[1:]))
        steps = max(4, ceil(length/5))
        points = []
        for i in range(steps+1):
            t = i/steps
            u = 1-t
            weights = (u**3, 3*u*u*t, 3*u*t*t, t**3)
            points.append(tuple(sum(w*p[axis] for w,p in zip(weights,controls)) for axis in (0,1)))
        self.stroke(points, rgb, width, alpha, dry)

    def _coverage(self, points):
        """Yield covered pixels with exact horizontal and sampled vertical coverage."""
        if len(points) < 3:
            return
        pixels = [(x*self.width, y*self.height) for x,y in points]
        edges = []
        for (ax,ay),(bx,by) in zip(pixels,pixels[1:]+pixels[:1]):
            if ay != by:
                edges.append((ax,ay,min(ay,by),max(ay,by),(bx-ax)/(by-ay)))
        first = max(0, floor(min(y for _,y in pixels)))
        last = min(self.height, ceil(max(y for _,y in pixels)))
        for py in range(first,last):
            if self.samples == 1:
                y = py+.5
                hits = sorted(ax+(y-ay)*slope for ax,ay,low,high,slope in edges if low<=y<high)
                for left,right in zip(hits[::2],hits[1::2]):
                    for px in range(max(0,ceil(left-.5)),min(self.width,ceil(right-.5))):
                        yield px,py,1.0
                continue
            amounts = {}
            for sample in range(self.samples):
                y = py+(sample+.5)/self.samples
                hits = sorted(ax+(y-ay)*slope for ax,ay,low,high,slope in edges if low<=y<high)
                for left,right in zip(hits[::2],hits[1::2]):
                    for px in range(max(0,floor(left)),min(self.width,ceil(right))):
                        fraction = min(px+1,right)-max(px,left)
                        amounts[px] = amounts.get(px,0)+fraction
            for px,amount in amounts.items():
                yield px,py,amount/self.samples

    def polygon(self, points, rgb, alpha=1.0, tooth=0.08):
        """Fill a silhouette using a solid color or normalized color field."""
        color_at = rgb if callable(rgb) else None
        for px,py,coverage in self._coverage(points):
            color = color_at((px+.5)/self.width,(py+.5)/self.height) if color_at else rgb
            self.blend(px,py,color,coverage*alpha*(1-tooth*paper(px,py)))

    @contextmanager
    def clip(self, points):
        """Limit subsequent marks to a mask. Nested masks intersect."""
        parent = self._clip
        mask = bytearray(self.width*self.height)
        for x,y,amount in self._coverage(points):
            i = y*self.width+x
            mask[i] = round(amount*(parent[i] if parent is not None else 255))
        self._clip = mask
        try:
            yield
        finally:
            self._clip = parent

    def save(self, path):
        def chunk(name, data):
            return (struct.pack(">I", len(data)) + name + data
                    + struct.pack(">I", zlib.crc32(name + data)))
        stride = self.width * 3
        scanlines = b"".join(b"\x00" + self.pixels[i:i+stride]
                             for i in range(0, len(self.pixels), stride))
        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(scanlines, 8)) + chunk(b"IEND", b"")
        Path(path).write_bytes(png)


def self_test():
    board = Canvas(32, 32)
    board.blend(0, 0, (200, 100, 50), 0.5)
    assert board.pixels[:3] == bytearray((100, 50, 25))
    board.polygon([(0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.75)],
                  (100, 80, 30), tooth=0)
    center = 3 * (16 * board.width + 16)
    assert board.pixels[center:center+3] == bytearray((100, 80, 30))
    board.polygon([(0,0), (1,0), (1,1), (0,1)], lambda x, y: (80*x, 0, 80*y), tooth=0)
    assert board.pixels[center:center+3] == bytearray((41, 0, 41))
    assert Noise(4, 9, 42)(0.27, 0.33) == Noise(4, 9, 42)(0.27, 0.33)
    edge = Canvas(8, 8, samples=4)
    edge.polygon([(0,0), (0.3125,0), (0.3125,1), (0,1)], (200,100,50), tooth=0)
    assert tuple(edge.pixels[6:12]) == (100,50,25,0,0,0)
    left = [(0,0), (.5,0), (.5,1), (0,1)]
    top = [(0,0), (1,0), (1,.5), (0,.5)]
    with edge.clip(left), edge.clip(top):
        edge.blend(0,0,(20,40,60),1)
        edge.blend(0,7,(20,40,60),1)
        edge.blend(7,0,(20,40,60),1)
    assert tuple(edge.pixels[:3]) == (20,40,60)
    assert tuple(edge.pixels[3*56:3*57]) == (200,100,50)
    assert tuple(edge.pixels[21:24]) == (0,0,0)
    edge.blend(7,7,(80,70,60),1)
    assert tuple(edge.pixels[-3:]) == (80,70,60)
    edge.curve((0,.8),(.25,.5),(.75,.5),(1,.8),(230,200,170),.12,.7)
    assert any(value > 200 for value in edge.pixels)
    edge.dab(.5,.5,.4,.06,(255,255,255),1,0,angle=45)
    assert edge.pixels[3*(3*8+3)] >= 230


if __name__ == "__main__":
    self_test()
