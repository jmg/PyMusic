import colorsys
import math

import wx

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    _PYGAME_AVAILABLE = False

from visual.fractals.lindenmayer import (
    Gen, kochRule, dragonRule, sierpinskiRule,
)


# (name, axiom, rule_fn, turn_angle_deg, iterations, draw_chars, start_offset_factor)
FRACTALS = [
    ("Sierpinski", 'A', sierpinskiRule, 60, 5, ('A', 'B'), (-0.25, 0.25)),
    ("Koch",       'F', kochRule,       90, 4, ('F',),     (-0.45, 0.0)),
    ("Dragon",     'FX', dragonRule,    90, 11, ('F',),    (0.0, 0.0)),
]


class VisualizationDisplay(wx.Window):

    FRAME_MS = 40              # ~25 fps
    DRAW_CHUNK = 60            # chars revealed per tick
    HOLD_TICKS = 60            # frames to hold the completed fractal before switching

    def __init__(self, parent, id, sizer):
        wx.Window.__init__(self, parent, id)

        if _PYGAME_AVAILABLE:
            pygame.init()

        self.parent = parent
        self.sizer = sizer

        size = self.sizer.GetSize()
        self.SetSize(size)
        self.size_dirty = True
        self.screen = None

        self._terms = [self._build_term(f) for f in FRACTALS]
        self._fractal_idx = 0
        self._reveal = 0
        self._hold = 0
        self._phase = 0.0

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTick, self.timer)

    def start(self):
        if not self.timer.IsRunning():
            self.timer.Start(self.FRAME_MS)

    def stop(self):
        if self.timer.IsRunning():
            self.timer.Stop()

    def _build_term(self, fractal):
        _, axiom, rule_fn, _, iterations, _, _ = fractal
        gen = Gen(axiom, rule_fn)
        s = axiom
        for _ in range(iterations):
            s = next(gen)
        return s

    def OnTick(self, event):
        self._phase += 0.03
        term = self._terms[self._fractal_idx]

        if self._reveal < len(term):
            self._reveal += self.DRAW_CHUNK
            if self._reveal > len(term):
                self._reveal = len(term)
        else:
            self._hold += 1
            if self._hold >= self.HOLD_TICKS:
                self._hold = 0
                self._reveal = 0
                self._fractal_idx = (self._fractal_idx + 1) % len(FRACTALS)

        self.Refresh(eraseBackground=False)

    def OnPaint(self, event):
        self.Redraw()
        event.Skip()

    def OnSize(self, event):
        self.SetSize(self.sizer.GetSize())
        self.size_dirty = True

    def Redraw(self):
        if not _PYGAME_AVAILABLE:
            return

        size = self.GetSize()
        w, h = size.GetWidth(), size.GetHeight()
        if w <= 0 or h <= 0:
            return

        if self.size_dirty or self.screen is None:
            self.screen = pygame.Surface((w, h), 0, 32)
            self.size_dirty = False

        self.screen.fill((10, 10, 25))

        fractal = FRACTALS[self._fractal_idx]
        name, _, _, turn_angle, _, draw_chars, (ox, oy) = fractal
        term = self._terms[self._fractal_idx][: self._reveal]

        if not term:
            self._blit()
            return

        # Pre-pass: walk the term to find bounding box, then scale to fit.
        path = self._walk(term, draw_chars, turn_angle, math.degrees(self._phase) % 360)
        if len(path) < 2:
            self._blit()
            return

        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        bw = max(1e-6, max_x - min_x)
        bh = max(1e-6, max_y - min_y)
        margin = 30
        scale = min((w - 2 * margin) / bw, (h - 2 * margin) / bh)
        cx = w / 2 - (min_x + bw / 2) * scale + ox * w
        cy = h / 2 - (min_y + bh / 2) * scale + oy * h

        # Color cycles with phase + along the path for a tracer effect.
        base_hue = (self._phase * 0.04) % 1.0
        n = len(path) - 1
        for i in range(n):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            hue = (base_hue + i / max(n, 1) * 0.3) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            color = (int(r * 255), int(g * 255), int(b * 255))
            pygame.draw.aaline(
                self.screen, color,
                (x1 * scale + cx, y1 * scale + cy),
                (x2 * scale + cx, y2 * scale + cy),
            )

        # Title overlay
        try:
            font = pygame.font.SysFont(None, 22)
            label = font.render(name, True, (200, 200, 220))
            self.screen.blit(label, (10, 8))
        except Exception:
            pass

        self._blit()

    def _walk(self, term, draw_chars, turn_angle, start_angle):
        path = [(0.0, 0.0)]
        x, y = 0.0, 0.0
        angle = start_angle
        for c in term:
            if c in draw_chars:
                x += math.cos(math.radians(angle))
                y += math.sin(math.radians(angle))
                path.append((x, y))
            elif c == '+':
                angle += turn_angle
            elif c == '-':
                angle -= turn_angle
        return path

    def _blit(self):
        s = pygame.image.tostring(self.screen, 'RGB')
        w, h = self.screen.get_size()
        img = wx.Image(w, h, s)
        bmp = wx.Bitmap(img)
        dc = wx.ClientDC(self)
        dc.DrawBitmap(bmp, 0, 0, False)
        del dc

    def Kill(self, event):
        self.timer.Stop()
        self.Unbind(event=wx.EVT_PAINT, handler=self.OnPaint)
