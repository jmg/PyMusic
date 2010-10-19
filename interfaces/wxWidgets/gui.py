# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Sep  8 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class wxGui
###########################################################################

class wxGui ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1200,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.tbSong = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.tbSong, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.tbTime = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.tbTime, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        bSizer4.Add( bSizer2, 0, wx.EXPAND, 5 )

        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

        self.btPlay = wx.Button( self, wx.ID_ANY, u"Play", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.btPlay, 1, wx.ALL|wx.EXPAND, 5 )

        self.btStop = wx.Button( self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.btStop, 1, wx.ALL, 5 )

        self.btPause = wx.Button( self, wx.ID_ANY, u"Pause", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.btPause, 1, wx.ALL, 5 )

        self.tgRandom = wx.ToggleButton( self, wx.ID_ANY, u"Random", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.tgRandom, 1, wx.ALL, 5 )

        bSizer4.Add( bSizer3, 0, wx.EXPAND, 5 )

        bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Search", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer21.Add( self.m_staticText1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.tbFinder = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer21.Add( self.tbFinder, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )

        bSizer4.Add( bSizer21, 0, wx.EXPAND, 5 )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        self.ntDown = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.pnPlayList = wx.Panel( self.ntDown, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer7 = wx.BoxSizer( wx.VERTICAL )

        self.lbSongs = wx.ListCtrl( self.pnPlayList, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_VRULES|wx.HSCROLL|wx.RAISED_BORDER|wx.VSCROLL )
        bSizer7.Add( self.lbSongs, 1, wx.ALL|wx.EXPAND, 5 )

        self.pnPlayList.SetSizer( bSizer7 )
        self.pnPlayList.Layout()
        bSizer7.Fit( self.pnPlayList )
        self.ntDown.AddPage( self.pnPlayList, u"PlayList", True )
        self.pnRadios = wx.Panel( self.ntDown, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer8 = wx.BoxSizer( wx.VERTICAL )

        self.lbRadios = wx.ListCtrl( self.pnRadios, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_VRULES )
        bSizer8.Add( self.lbRadios, 1, wx.ALL|wx.EXPAND, 5 )

        self.pnRadios.SetSizer( bSizer8 )
        self.pnRadios.Layout()
        bSizer8.Fit( self.pnRadios )
        self.ntDown.AddPage( self.pnRadios, u"Radios", False )

        bSizer6.Add( self.ntDown, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        bSizer4.Add( bSizer6, 1, wx.EXPAND, 5 )

        bSizer1.Add( bSizer4, 1, wx.EXPAND, 5 )

        bSizer5 = wx.BoxSizer( wx.VERTICAL )

        self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_panel3 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer9 = wx.BoxSizer( wx.VERTICAL )

        self.tbLyrics = wx.TextCtrl( self.m_panel3, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
        bSizer9.Add( self.tbLyrics, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_panel3.SetSizer( bSizer9 )
        self.m_panel3.Layout()
        bSizer9.Fit( self.m_panel3 )
        self.m_notebook1.AddPage( self.m_panel3, u"Lyrics", False )

        bSizer5.Add( self.m_notebook1, 1, wx.EXPAND |wx.ALL, 5 )

        bSizer1.Add( bSizer5, 1, wx.EXPAND, 5 )

        self.SetSizer( bSizer1 )
        self.Layout()
        self.m_statusBar1 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
        self.mnBar = wx.MenuBar( 0 )
        self.mnFile = wx.Menu()
        self.itAddList = wx.MenuItem( self.mnFile, wx.ID_ANY, u"Add List", wx.EmptyString, wx.ITEM_NORMAL )
        self.mnFile.AppendItem( self.itAddList )

        self.itAddRadio = wx.MenuItem( self.mnFile, wx.ID_ANY, u"Add Radio", wx.EmptyString, wx.ITEM_NORMAL )
        self.mnFile.AppendItem( self.itAddRadio )

        self.itGenList = wx.MenuItem( self.mnFile, wx.ID_ANY, u"Generate List", wx.EmptyString, wx.ITEM_NORMAL )
        self.mnFile.AppendItem( self.itGenList )

        self.mnBar.Append( self.mnFile, u"File" )

        self.mnView = wx.Menu()
        self.itAddList1 = wx.MenuItem( self.mnView, wx.ID_ANY, u"Lyrics", wx.EmptyString, wx.ITEM_NORMAL )
        self.mnView.AppendItem( self.itAddList1 )

        self.mnBar.Append( self.mnView, u"View" )

        self.SetMenuBar( self.mnBar )


        self.Centre( wx.BOTH )

        # Connect Events
        self.btPlay.Bind( wx.EVT_BUTTON, self.btPlay_click )
        self.btStop.Bind( wx.EVT_BUTTON, self.btStop_click )
        self.btPause.Bind( wx.EVT_BUTTON, self.btPause_click )
        self.tgRandom.Bind( wx.EVT_TOGGLEBUTTON, self.tgRandom_click )
        self.tbFinder.Bind( wx.EVT_KEY_DOWN, self.tbFinder_click )
        self.ntDown.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.ntDown_Changed )
        self.lbSongs.Bind( wx.EVT_LEFT_DCLICK, self.lbSongs_dbClick )
        self.lbRadios.Bind( wx.EVT_KEY_DOWN, self.lbRadios_keyDown )
        self.lbRadios.Bind( wx.EVT_LEFT_DCLICK, self.lbRadios_dbClick )
        self.Bind( wx.EVT_MENU, self.itAddList_click, id = self.itAddList.GetId() )
        self.Bind( wx.EVT_MENU, self.itAddRadio_click, id = self.itAddRadio.GetId() )
        self.Bind( wx.EVT_MENU, self.itAddList_click, id = self.itGenList.GetId() )
        self.Bind( wx.EVT_MENU, self.itAddList_click, id = self.itAddList1.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def btPlay_click( self, event ):
        event.Skip()

    def btStop_click( self, event ):
        event.Skip()

    def btPause_click( self, event ):
        event.Skip()

    def tgRandom_click( self, event ):
        event.Skip()

    def tbFinder_click( self, event ):
        event.Skip()

    def ntDown_Changed( self, event ):
        event.Skip()

    def lbSongs_dbClick( self, event ):
        event.Skip()

    def lbRadios_keyDown( self, event ):
        event.Skip()

    def lbRadios_dbClick( self, event ):
        event.Skip()

    def itAddList_click( self, event ):
        event.Skip()

    def itAddRadio_click( self, event ):
        event.Skip()




