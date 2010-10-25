# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Sep  8 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class FrmGenList
###########################################################################

class FrmGenList ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Add Radio Url ", pos = wx.DefaultPosition, size = wx.Size( 352,188 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer11 = wx.BoxSizer( wx.VERTICAL )

        bSizer13 = wx.BoxSizer( wx.VERTICAL )

        bSizer25 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Size", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer25.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.tbSize = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer25.Add( self.tbSize, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer13.Add( bSizer25, 1, wx.EXPAND, 5 )

        bSizer26 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Filter", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer26.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.tbFilter = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer26.Add( self.tbFilter, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer13.Add( bSizer26, 1, wx.EXPAND, 5 )

        self.dpDir = wx.DirPickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE )
        bSizer13.Add( self.dpDir, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer11.Add( bSizer13, 0, wx.EXPAND, 5 )

        bSizer12 = wx.BoxSizer( wx.HORIZONTAL )

        self.btOk = wx.Button( self, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer12.Add( self.btOk, 1, wx.ALL, 5 )

        self.btCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer12.Add( self.btCancel, 1, wx.ALL, 5 )

        bSizer11.Add( bSizer12, 0, wx.EXPAND, 5 )

        self.SetSizer( bSizer11 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.btOk.Bind( wx.EVT_BUTTON, self.btOk_click )
        self.btCancel.Bind( wx.EVT_BUTTON, self.btCancel_click )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def btOk_click( self, event ):
        event.Skip()

    def btCancel_click( self, event ):
        event.Skip()


