import wx

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    _PYGAME_AVAILABLE = False

from visual.fractals import FractalGen


class VisualizationDisplay(wx.Window):

    def __init__(self, parent, id, sizer):
        wx.Window.__init__(self, parent, id)

        if _PYGAME_AVAILABLE:
            pygame.init()

        self.parent = parent
        self.hwnd = self.GetHandle()
        self.sizer = sizer

        size = self.sizer.GetSize()
        self.SetSize(size)
        self.size_dirty = True

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.linespacing = 5

        self.gen = FractalGen.FractalGen()
        self.s = ""
        for _ in range(3):
            self.s = next(self.gen)

    def Update(self, event):
        self.Redraw()

    def Redraw(self):
        if not _PYGAME_AVAILABLE:
            return

        size = self.sizer.GetSize()
        if self.size_dirty:
            self.screen = pygame.Surface((size.GetWidth(), size.GetHeight()), 0, 32)
            self.size_dirty = False

        self.screen.fill((0, 0, 0))

        cur = 0
        w, h = self.screen.get_size()
        while cur <= h:
            pygame.draw.aaline(self.screen, (255, 255, 255), (0, h - cur), (cur, 0))
            cur += self.linespacing

        self.pencil = FractalGen.Pencil(self.screen)

        for c in self.s:
            if c in ('A', 'B'):
                self.pencil.draw()
            elif c == '+':
                self.pencil.turn_left_with_angle(60)
            elif c == '-':
                self.pencil.turn_left_with_angle(-60)

        s = pygame.image.tostring(self.screen, 'RGB')
        img = wx.Image(500, 500, s)
        bmp = wx.Bitmap(img)
        dc = wx.ClientDC(self)
        dc.DrawBitmap(bmp, 0, 0, False)
        del dc

    def OnPaint(self, event):
        self.Redraw()
        event.Skip()

    def OnSize(self, event):
        self.SetSize(self.sizer.GetSize())
        self.size_dirty = True

    def Kill(self, event):
        self.Unbind(event=wx.EVT_PAINT, handler=self.OnPaint)
