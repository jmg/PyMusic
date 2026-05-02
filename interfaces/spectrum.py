"""Frequency-style spectrum visualizer.

Bars drawn with wx that animate while music plays. The values are
synthesised (no real FFT — VLC audio callbacks would replace audio
output) but the motion gives a live, organic look that reacts to
play / pause / stop.
"""

import colorsys
import math
import random

import wx


class SpectrumDisplay(wx.Panel):

    NUM_BARS = 48
    FRAME_MS = 50
    EASE = 0.25            # how fast bars approach target
    DECAY = 0.88           # decay factor when not playing
    HEIGHT = 90

    def __init__(self, parent, player_provider):
        super().__init__(parent, size=(-1, self.HEIGHT), style=wx.NO_BORDER)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize((-1, self.HEIGHT))

        self._player_provider = player_provider
        self._heights = [0.0] * self.NUM_BARS
        self._targets = [0.0] * self.NUM_BARS
        self._phase = 0.0

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_tick, self._timer)

    def start(self):
        if not self._timer.IsRunning():
            self._timer.Start(self.FRAME_MS)

    def stop(self):
        if self._timer.IsRunning():
            self._timer.Stop()
        # let bars decay visually for a moment
        self._targets = [0.0] * self.NUM_BARS
        self.Refresh()

    # ------------------------------------------------------------------
    def _player_active(self):
        try:
            p = self._player_provider()
            return bool(p) and p.isPlaying()
        except Exception:
            return False

    def _on_tick(self, event):
        self._phase += 0.15
        playing = self._player_active()

        if playing:
            for i in range(self.NUM_BARS):
                # Pseudo-spectrum: lower bins get more energy, modulated by
                # several sine waves to produce a "music-like" envelope.
                base = (math.sin(self._phase * 1.7 + i * 0.4)
                        + math.sin(self._phase * 0.8 + i * 0.13) * 0.5
                        + math.sin(self._phase * 3.1 + i * 0.07) * 0.3)
                # Shape so low bins are louder, high bins quieter.
                falloff = math.exp(-i / (self.NUM_BARS * 0.7))
                noise = random.uniform(-0.15, 0.25)
                target = max(0.05, falloff * (0.55 + 0.4 * base) + noise)
                self._targets[i] = min(1.0, target)
        else:
            for i in range(self.NUM_BARS):
                self._targets[i] *= self.DECAY

        for i in range(self.NUM_BARS):
            diff = self._targets[i] - self._heights[i]
            self._heights[i] += diff * self.EASE

        self.Refresh(eraseBackground=False)

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return

        w, h = self.GetClientSize()
        if w <= 0 or h <= 0:
            return

        # Background gradient
        gc.SetBrush(gc.CreateLinearGradientBrush(
            0, 0, 0, h,
            wx.Colour(15, 15, 30), wx.Colour(8, 8, 18),
        ))
        gc.DrawRectangle(0, 0, w, h)

        gap = 2
        bar_w = max(1.0, (w - gap * (self.NUM_BARS + 1)) / self.NUM_BARS)
        x = gap

        for i, hv in enumerate(self._heights):
            bar_h = max(1.0, hv * (h - 4))
            y = h - bar_h - 2

            # Color: hue depends on bar index + slow phase.
            hue = ((i / self.NUM_BARS) * 0.65 + self._phase * 0.01) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.95)
            top = wx.Colour(int(r * 255), int(g * 255), int(b * 255))
            r2, g2, b2 = colorsys.hsv_to_rgb(hue, 0.8, 0.4)
            bottom = wx.Colour(int(r2 * 255), int(g2 * 255), int(b2 * 255))

            brush = gc.CreateLinearGradientBrush(x, y, x, y + bar_h, top, bottom)
            gc.SetBrush(brush)
            gc.SetPen(wx.TRANSPARENT_PEN)
            path = gc.CreatePath()
            radius = min(3.0, bar_w / 2)
            path.AddRoundedRectangle(x, y, bar_w, bar_h, radius)
            gc.FillPath(path)

            x += bar_w + gap
