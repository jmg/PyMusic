# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Sep  8 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class LyricReader
###########################################################################

class LyricReader ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 600,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Tema", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer2.Add( self.m_staticText1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.tbTema = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.tbTema, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"Artista", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText11.Wrap( -1 )
        bSizer2.Add( self.m_staticText11, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.tbArtista = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.tbArtista, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.btBuscar = wx.Button( self, wx.ID_ANY, u"Buscar", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.btBuscar, 0, wx.ALL, 5 )

        bSizer1.Add( bSizer2, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )

        self.tbLyric = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
        bSizer1.Add( self.tbLyric, 1, wx.ALL|wx.EXPAND, 5 )

        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.tbTema.Bind( wx.EVT_KEY_DOWN, self.tbTema_change )
        self.tbArtista.Bind( wx.EVT_KEY_DOWN, self.tbArtista_change )
        self.btBuscar.Bind( wx.EVT_BUTTON, self.btBuscar_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def tbTema_change( self, event ):
        event.Skip()

    def tbArtista_change( self, event ):
        event.Skip()

    def btBuscar_click( self, event ):
        event.Skip()


