# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Sep  8 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class frmLogo
###########################################################################

class frmLogo ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 340,360 ), style = 0|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer18 = wx.BoxSizer( wx.VERTICAL )

        self.bmLogo = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( u"logo.bmp", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer18.Add( self.bmLogo, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.SetSizer( bSizer18 )
        self.Layout()

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


