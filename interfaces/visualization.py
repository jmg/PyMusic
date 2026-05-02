import colorsys
import math

import wx

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    _PYGAME_AVAILABLE = False

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    np = None
    _NUMPY_AVAILABLE = False

from visual.fractals.lindenmayer import (
    Gen, apply_rule, kochRule, dragonRule, sierpinskiRule,
)


def hilbertRule(s):
    return apply_rule(s, {'A': '-BF+AFA+FB-', 'B': '+AF-BFB-FA+'})


def levyRule(s):
    return apply_rule(s, {'F': '+F--F+'})


# Each fractal is a dict; "kind" selects the renderer.
FRACTALS = [
    {
        "name": "Sierpinski", "kind": "lsystem",
        "axiom": "A", "rule": sierpinskiRule,
        "turn": 60, "iterations": 5, "draw": ("A", "B"),
    },
    {
        "name": "Koch", "kind": "lsystem",
        "axiom": "F", "rule": kochRule,
        "turn": 90, "iterations": 4, "draw": ("F",),
    },
    {
        "name": "Dragon", "kind": "lsystem",
        "axiom": "FX", "rule": dragonRule,
        "turn": 90, "iterations": 11, "draw": ("F",),
    },
    {
        "name": "Hilbert", "kind": "lsystem",
        "axiom": "A", "rule": hilbertRule,
        "turn": 90, "iterations": 5, "draw": ("F",),
    },
    {
        "name": "Lévy C", "kind": "lsystem",
        "axiom": "F", "rule": levyRule,
        "turn": 45, "iterations": 10, "draw": ("F",),
    },
    {
        "name": "Mandelbrot", "kind": "escape",
        "fn": "mandelbrot",
        "center": (-0.743643887037151, 0.131825904205330),
        "init_scale": 3.0, "zoom_speed": 0.97, "max_zoom_steps": 200,
        "max_iter": 80,
    },
    {
        "name": "Julia", "kind": "escape",
        "fn": "julia",
        "center": (0.0, 0.0),
        "init_scale": 3.2, "zoom_speed": 1.0, "max_zoom_steps": 0,
        "max_iter": 100,
    },
    {
        "name": "Burning Ship", "kind": "escape",
        "fn": "burning_ship",
        "center": (-1.762, -0.028),
        "init_scale": 0.06, "zoom_speed": 0.985, "max_zoom_steps": 200,
        "max_iter": 120,
    },
]


class VisualizationDisplay(wx.Window):

    FRAME_MS = 40              # ~25 fps
    DRAW_CHUNK = 60            # chars revealed per tick (lsystem)
    HOLD_TICKS_LSYS = 60       # ticks holding a finished lsystem
    HOLD_TICKS_ESCAPE = 200    # ticks animating an escape fractal
    ESCAPE_RES = (320, 240)    # render resolution for escape fractals (scaled up)

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

        self._terms = {}
        for f in FRACTALS:
            if f["kind"] == "lsystem":
                self._terms[f["name"]] = self._build_term(f)

        self._fractal_idx = 0
        self._reveal = 0
        self._hold = 0
        self._phase = 0.0
        self._escape_step = 0
        self._effect_idx = 0
        self._trail = None

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
        gen = Gen(fractal["axiom"], fractal["rule"])
        s = fractal["axiom"]
        for _ in range(fractal["iterations"]):
            s = next(gen)
        return s

    EFFECTS = ("none", "trail", "mirror", "kaleidoscope", "pulse", "invert")

    def _next_fractal(self):
        self._hold = 0
        self._reveal = 0
        self._escape_step = 0
        self._trail = None
        self._fractal_idx = (self._fractal_idx + 1) % len(FRACTALS)
        self._effect_idx = (self._effect_idx + 1) % len(self.EFFECTS)

    def OnTick(self, event):
        self._phase += 0.03
        fractal = FRACTALS[self._fractal_idx]

        if fractal["kind"] == "lsystem":
            term = self._terms[fractal["name"]]
            if self._reveal < len(term):
                self._reveal = min(len(term), self._reveal + self.DRAW_CHUNK)
            else:
                self._hold += 1
                if self._hold >= self.HOLD_TICKS_LSYS:
                    self._next_fractal()
        else:
            self._escape_step += 1
            if self._escape_step >= self.HOLD_TICKS_ESCAPE:
                self._next_fractal()

        self.Refresh(eraseBackground=False)

    def OnPaint(self, event):
        self.Redraw()
        event.Skip()

    def OnSize(self, event):
        self.SetSize(self.sizer.GetSize())
        self.size_dirty = True

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def Redraw(self):
        if not _PYGAME_AVAILABLE:
            return

        size = self.GetSize()
        w, h = size.GetWidth(), size.GetHeight()
        if w <= 0 or h <= 0:
            return

        if self.size_dirty or self.screen is None:
            self.screen = pygame.Surface((w, h), 0, 32)
            self._trail = None
            self.size_dirty = False

        effect = self.EFFECTS[self._effect_idx]

        if effect == "trail" and self._trail is not None:
            # fade previous frame instead of clearing
            fade = pygame.Surface((w, h))
            fade.fill((10, 10, 25))
            fade.set_alpha(40)
            self.screen.blit(self._trail, (0, 0))
            self.screen.blit(fade, (0, 0))
        else:
            self.screen.fill((10, 10, 25))

        fractal = FRACTALS[self._fractal_idx]
        if fractal["kind"] == "lsystem":
            self._render_lsystem(fractal, w, h)
        else:
            self._render_escape(fractal, w, h)

        if effect == "mirror":
            self._apply_mirror(w, h)
        elif effect == "kaleidoscope":
            self._apply_kaleidoscope(w, h)
        elif effect == "pulse":
            self._apply_pulse(w, h)
        elif effect == "invert":
            self._apply_invert()

        if effect == "trail":
            self._trail = self.screen.copy()

        # Title overlay (centered top)
        try:
            font_big = pygame.font.SysFont(None, 38, bold=True)
            font_small = pygame.font.SysFont(None, 20)
            name_lbl = font_big.render(fractal["name"], True, (240, 240, 255))
            fx_lbl = font_small.render(f"fx: {effect}", True, (180, 180, 210))
            nx = (w - name_lbl.get_width()) // 2
            fx_x = (w - fx_lbl.get_width()) // 2
            self.screen.blit(name_lbl, (nx, 10))
            self.screen.blit(fx_lbl, (fx_x, 10 + name_lbl.get_height() + 2))
        except Exception:
            pass

        self._blit()

    def _apply_mirror(self, w, h):
        half = self.screen.subsurface((0, 0, w // 2, h)).copy()
        flipped = pygame.transform.flip(half, True, False)
        self.screen.blit(flipped, (w // 2, 0))

    def _apply_kaleidoscope(self, w, h):
        quad = self.screen.subsurface((0, 0, w // 2, h // 2)).copy()
        self.screen.blit(pygame.transform.flip(quad, True, False), (w // 2, 0))
        self.screen.blit(pygame.transform.flip(quad, False, True), (0, h // 2))
        self.screen.blit(pygame.transform.flip(quad, True, True), (w // 2, h // 2))

    def _apply_pulse(self, w, h):
        scale = 1.0 + 0.08 * math.sin(self._phase * 2)
        sw, sh = max(1, int(w * scale)), max(1, int(h * scale))
        scaled = pygame.transform.smoothscale(self.screen, (sw, sh))
        out = pygame.Surface((w, h))
        out.fill((10, 10, 25))
        out.blit(scaled, ((w - sw) // 2, (h - sh) // 2))
        self.screen.blit(out, (0, 0))

    def _apply_invert(self):
        if not _NUMPY_AVAILABLE:
            return
        arr = pygame.surfarray.pixels3d(self.screen)
        arr[:] = 255 - arr
        del arr

    def _render_lsystem(self, fractal, w, h):
        term = self._terms[fractal["name"]][: self._reveal]
        if not term:
            return

        path = self._walk(
            term, fractal["draw"], fractal["turn"],
            math.degrees(self._phase) % 360,
        )
        if len(path) < 2:
            return

        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        bw = max(1e-6, max_x - min_x)
        bh = max(1e-6, max_y - min_y)
        margin = 30
        scale = min((w - 2 * margin) / bw, (h - 2 * margin) / bh)
        cx = w / 2 - (min_x + bw / 2) * scale
        cy = h / 2 - (min_y + bh / 2) * scale

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

    def _render_escape(self, fractal, w, h):
        if not _NUMPY_AVAILABLE:
            return

        rw, rh = self.ESCAPE_RES
        cx, cy = fractal["center"]
        max_iter = fractal["max_iter"]

        # Animation
        zoom_factor = fractal["zoom_speed"] ** min(self._escape_step, fractal["max_zoom_steps"])
        scale = fractal["init_scale"] * zoom_factor

        x = np.linspace(cx - scale / 2, cx + scale / 2, rw)
        y = np.linspace(cy - scale * rh / rw / 2, cy + scale * rh / rw / 2, rh)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y

        if fractal["fn"] == "mandelbrot":
            iters = self._iterate_mandelbrot(C, max_iter)
        elif fractal["fn"] == "julia":
            theta = self._phase * 0.7
            c_param = 0.7885 * np.exp(1j * theta)
            iters = self._iterate_julia(C, c_param, max_iter)
        elif fractal["fn"] == "burning_ship":
            iters = self._iterate_burning_ship(C, max_iter)
        else:
            return

        # Map iterations → color (HSV with phase shift).
        hue_shift = (self._phase * 0.05) % 1.0
        norm = iters / max_iter
        in_set = iters >= max_iter

        hue = (norm + hue_shift) % 1.0
        sat = np.where(in_set, 0.0, 0.85)
        val = np.where(in_set, 0.0, np.minimum(1.0, norm * 3.0))

        rgb = self._hsv_to_rgb_array(hue, sat, val)  # (rh, rw, 3) uint8

        surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        scaled = pygame.transform.smoothscale(surf, (w, h))
        self.screen.blit(scaled, (0, 0))

    @staticmethod
    def _iterate_mandelbrot(C, max_iter):
        Z = np.zeros_like(C)
        iters = np.zeros(C.shape, dtype=np.int32)
        mask = np.ones(C.shape, dtype=bool)
        for i in range(max_iter):
            Z[mask] = Z[mask] * Z[mask] + C[mask]
            escaped = np.abs(Z) > 2
            new = mask & escaped
            iters[new] = i
            mask &= ~escaped
            if not mask.any():
                break
        iters[mask] = max_iter
        return iters

    @staticmethod
    def _iterate_julia(C, c_param, max_iter):
        Z = C.copy()
        iters = np.zeros(C.shape, dtype=np.int32)
        mask = np.ones(C.shape, dtype=bool)
        for i in range(max_iter):
            Z[mask] = Z[mask] * Z[mask] + c_param
            escaped = np.abs(Z) > 2
            new = mask & escaped
            iters[new] = i
            mask &= ~escaped
            if not mask.any():
                break
        iters[mask] = max_iter
        return iters

    @staticmethod
    def _iterate_burning_ship(C, max_iter):
        Z = np.zeros_like(C)
        iters = np.zeros(C.shape, dtype=np.int32)
        mask = np.ones(C.shape, dtype=bool)
        for i in range(max_iter):
            zr = np.abs(Z[mask].real)
            zi = np.abs(Z[mask].imag)
            Z[mask] = (zr + 1j * zi) ** 2 + C[mask]
            escaped = np.abs(Z) > 2
            new = mask & escaped
            iters[new] = i
            mask &= ~escaped
            if not mask.any():
                break
        iters[mask] = max_iter
        return iters

    @staticmethod
    def _hsv_to_rgb_array(h, s, v):
        # Vectorized HSV→RGB; inputs are arrays in [0,1].
        i = np.floor(h * 6).astype(int)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        i = i % 6

        r = np.choose(i, [v, q, p, p, t, v])
        g = np.choose(i, [t, v, v, q, p, p])
        b = np.choose(i, [p, p, t, v, v, q])

        rgb = np.stack([r, g, b], axis=-1)
        return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)

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
