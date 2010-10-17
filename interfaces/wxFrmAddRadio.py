from wxWidgets.frmAddRadio import FrmAddRadio
from logic.player_logic import PlayerLogic, PlayerDataLogic

class wxFrmAddRadio(FrmAddRadio):

    OK = 1
    CANCEL = 0

    data_logic = PlayerDataLogic()
    State = CANCEL

    def __init__( self, parent ):
        FrmAddRadio.__init__(self, parent)

    def btOk_click( self, event ):
        self.data_logic.add_radio(self.tbAddRadio.GetValue())
        self.State = self.OK
        self.Close()

    def btCancel_click( self, event ):
        self.Close()
