# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Sep  8 2010)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx

###########################################################################
## Class FrmAddRadio
###########################################################################

class FrmAddRadio ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Add Radio Url ", pos = wx.DefaultPosition, size = wx.Size( 577,98 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer11 = wx.BoxSizer( wx.VERTICAL )

        bSizer13 = wx.BoxSizer( wx.VERTICAL )

        self.tbAddRadio = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer13.Add( self.tbAddRadio, 0, wx.ALL|wx.EXPAND, 5 )

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


