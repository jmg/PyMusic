import wx
import pygame
from visual.fractals import FractalGen

class VisualizationDisplay(wx.Window):
    def __init__(self, parent, id, sizer):
        wx.Window.__init__(self, parent, id)

        pygame.init()

        self.parent = parent
        self.hwnd = self.GetHandle()

        self.sizer = sizer

        self.SetSize(self.sizer.GetSizeTuple())
        self.size_dirty = True

        #self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.linespacing = 5

        self.gen = FractalGen.FractalGen()
        self.s = ""
        for x in range(3):
            self.s = self.gen.next()


    def Update(self, event):
        # Any update tasks would go here (moving sprites, advancing animation frames etc.)
        self.Redraw()

    def Redraw(self):
        if self.size_dirty:
            self.screen = pygame.Surface(self.sizer.GetSizeTuple(), 0, 32)
            self.size_dirty = False

        self.screen.fill((0,0,0))

        cur = 0

        w, h = self.screen.get_size()
        while cur <= h:
            pygame.draw.aaline(self.screen, (255, 255, 255), (0, h - cur), (cur, 0))
            cur += self.linespacing

        self.pencil = FractalGen.Pencil(self.screen)

        print self.s

        for c in self.s:
            if c == 'A' or c == 'B':
                self.pencil.draw()
            elif c == '+':
                self.pencil.turn_left_with_angle(60)
            elif c == '-':
                self.pencil.turn_left_with_angle(-60)

        s = pygame.image.tostring(self.screen, 'RGB')  # Convert the surface to an RGB string
        img = wx.ImageFromData(500, 500, s)  # Load this string into a wx image
        bmp = wx.BitmapFromImage(img)  # Get the image in bitmap form
        dc = wx.ClientDC(self)  # Device context for drawing the bitmap
        dc.DrawBitmap(bmp, 0, 0, False)  # Blit the bitmap image to the display
        del dc


    def OnPaint(self, event):
        self.Redraw()
        event.Skip()  # Make sure the parent frame gets told to redraw as well

    def OnSize(self, event):
        self.SetSize(self.sizer.GetSizeTuple())
        self.size_dirty = True

    def Kill(self, event):
        # Make sure Pygame can't be asked to redraw /before/ quitting by unbinding all methods which
        # call the Redraw() method
        # (Otherwise wx seems to call Draw between quitting Pygame and destroying the frame)
        # This may or may not be necessary now that Pygame is just drawing to surfaces
        self.Unbind(event = wx.EVT_PAINT, handler = self.OnPaint)
        self.Unbind(event = wx.EVT_TIMER, handler = self.Update, source = self.timer)
