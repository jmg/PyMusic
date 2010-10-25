from wxWidgets.frmGenList import FrmGenList
from logic.player_logic import PlayerLogic, PlayerDataLogic

class wxFrmGenList(FrmGenList):

    OK = 1
    CANCEL = 0

    data_logic = PlayerDataLogic()
    State = CANCEL

    def __init__( self, parent ):
        FrmGenList.__init__(self, parent)

    def btOk_click( self, event ):
        self.size = self.tbSize.GetValue()
        self.filter = self.tbFilter.GetValue()
        self.dir = self.dpDir.GetPath()
        self.State = self.OK
        self.Close()

    def btCancel_click( self, event ):
        self.Close()
