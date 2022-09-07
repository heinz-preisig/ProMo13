# ===============================================================================
# qt resources
# ===============================================================================


from PyQt5 import QtCore
from PyQt5 import QtWidgets

# from PyQt5 import QtGui  as Q_Gui

Qt = QtCore.Qt
# caused some problems when saving automaton to file.....

left = int(Qt.LeftButton)
right = int(Qt.RightButton)
middle = int(Qt.MidButton)
nobut = int(Qt.NoButton)
LEFT = left  # Qt.LeftButton
MIDDLE = middle  # Qt.MidButton
RIGHT = right  # Qt.RightButton
NO_BUT = nobut  # Qt.NoButton
YES = QtWidgets.QMessageBox.Yes
NO = QtWidgets.QMessageBox.No
OK = QtWidgets.QMessageBox.Ok

KEYS = {
        Qt.Key_Escape        : 'Key_Escape',
        Qt.Key_Tab           : 'Key_Tab',
        Qt.Key_Backtab       : 'Key_Backtab',
        Qt.Key_Backspace     : 'Key_Backspace',
        Qt.Key_Return        : 'Key_Return',
        Qt.Key_Enter         : 'Key_Enter',
        Qt.Key_Insert        : 'Key_Insert',
        Qt.Key_Delete        : 'Key_Delete',
        Qt.Key_Pause         : 'Key_Pause',
        Qt.Key_Print         : 'Key_Print',
        Qt.Key_SysReq        : 'Key_SysReq',
        Qt.Key_Home          : 'Key_Home',
        Qt.Key_End           : 'Key_End',
        Qt.Key_Left          : 'Key_Left',
        Qt.Key_Up            : 'Key_Up',
        Qt.Key_Right         : 'Key_Right',
        Qt.Key_Down          : 'Key_Down',
        # Qt.Key_Prior        :                'Key_Prior'     ,
        # Qt.Key_Next        :                'Key_Next'     ,
        Qt.Key_Shift         : 'Key_Shift',
        Qt.Key_Control       : 'Key_Control',
        Qt.Key_Meta          : 'Key_Meta',
        Qt.Key_Alt           : 'Key_Alt',
        Qt.Key_CapsLock      : 'Key_CapsLock',
        Qt.Key_NumLock       : 'Key_NumLock',
        Qt.Key_ScrollLock    : 'Key_ScrollLock',
        Qt.Key_Clear         : 'Key_Clear',
        Qt.Key_F1            : 'Key_F1',
        Qt.Key_F2            : 'Key_F2',
        Qt.Key_F3            : 'Key_F3',
        Qt.Key_F4            : 'Key_F4',
        Qt.Key_F5            : 'Key_F5',
        Qt.Key_F6            : 'Key_F6',
        Qt.Key_F7            : 'Key_F7',
        Qt.Key_F8            : 'Key_F8',
        Qt.Key_F9            : 'Key_F9',
        Qt.Key_F10           : 'Key_F10',
        Qt.Key_F11           : 'Key_F11',
        Qt.Key_F12           : 'Key_F12',
        Qt.Key_F13           : 'Key_F13',
        Qt.Key_F14           : 'Key_F14',
        Qt.Key_F15           : 'Key_F15',
        Qt.Key_F16           : 'Key_F16',
        Qt.Key_F17           : 'Key_F17',
        Qt.Key_F18           : 'Key_F18',
        Qt.Key_F19           : 'Key_F19',
        Qt.Key_F20           : 'Key_F20',
        Qt.Key_F21           : 'Key_F21',
        Qt.Key_F22           : 'Key_F22',
        Qt.Key_F23           : 'Key_F23',
        Qt.Key_F24           : 'Key_F24',
        Qt.Key_F25           : 'Key_F25',
        Qt.Key_F26           : 'Key_F26',
        Qt.Key_F27           : 'Key_F27',
        Qt.Key_F28           : 'Key_F28',
        Qt.Key_F29           : 'Key_F29',
        Qt.Key_F30           : 'Key_F30',
        Qt.Key_F31           : 'Key_F31',
        Qt.Key_F32           : 'Key_F32',
        Qt.Key_F33           : 'Key_F33',
        Qt.Key_F34           : 'Key_F34',
        Qt.Key_F35           : 'Key_F35',
        Qt.Key_Super_L       : 'Key_Super_L',
        Qt.Key_Super_R       : 'Key_Super_R',
        Qt.Key_Menu          : 'Key_Menu',
        Qt.Key_Hyper_L       : 'Key_Hyper_L',
        Qt.Key_Hyper_R       : 'Key_Hyper_R',
        Qt.Key_Help          : 'Key_Help',
        Qt.Key_Space         : 'Key_Space',
        Qt.Key_Any           : 'Key_Any',
        Qt.Key_Exclam        : 'Key_Exclam',
        Qt.Key_QuoteDbl      : 'Key_QuoteDbl',
        Qt.Key_NumberSign    : 'Key_NumberSign',
        Qt.Key_Dollar        : 'Key_Dollar',
        Qt.Key_Percent       : 'Key_Percent',
        Qt.Key_Ampersand     : 'Key_Ampersand',
        Qt.Key_Apostrophe    : 'Key_Apostrophe',
        Qt.Key_ParenLeft     : 'Key_ParenLeft',
        Qt.Key_ParenRight    : 'Key_ParenRight',
        Qt.Key_Asterisk      : 'Key_Asterisk',
        Qt.Key_Plus          : 'Key_Plus',
        Qt.Key_Comma         : 'Key_Comma',
        Qt.Key_Minus         : 'Key_Minus',
        Qt.Key_Period        : 'Key_Period',
        Qt.Key_Slash         : 'Key_Slash',
        Qt.Key_0             : 'Key_0',
        Qt.Key_1             : 'Key_1',
        Qt.Key_2             : 'Key_2',
        Qt.Key_3             : 'Key_3',
        Qt.Key_4             : 'Key_4',
        Qt.Key_5             : 'Key_5',
        Qt.Key_6             : 'Key_6',
        Qt.Key_7             : 'Key_7',
        Qt.Key_8             : 'Key_8',
        Qt.Key_9             : 'Key_9',
        Qt.Key_Colon         : 'Key_Colon',
        Qt.Key_Semicolon     : 'Key_Semicolon',
        Qt.Key_Less          : 'Key_Less',
        Qt.Key_Equal         : 'Key_Equal',
        Qt.Key_Greater       : 'Key_Greater',
        Qt.Key_Question      : 'Key_Question',
        Qt.Key_At            : 'Key_At',
        Qt.Key_A             : 'Key_A',
        Qt.Key_B             : 'Key_B',
        Qt.Key_C             : 'Key_C',
        Qt.Key_D             : 'Key_D',
        Qt.Key_E             : 'Key_E',
        Qt.Key_F             : 'Key_F',
        Qt.Key_G             : 'Key_G',
        Qt.Key_H             : 'Key_H',
        Qt.Key_I             : 'Key_I',
        Qt.Key_J             : 'Key_J',
        Qt.Key_K             : 'Key_K',
        Qt.Key_L             : 'Key_L',
        Qt.Key_M             : 'Key_M',
        Qt.Key_N             : 'Key_N',
        Qt.Key_O             : 'Key_O',
        Qt.Key_P             : 'Key_P',
        Qt.Key_Q             : 'Key_Q',
        Qt.Key_R             : 'Key_R',
        Qt.Key_S             : 'Key_S',
        Qt.Key_T             : 'Key_T',
        Qt.Key_U             : 'Key_U',
        Qt.Key_V             : 'Key_V',
        Qt.Key_W             : 'Key_W',
        Qt.Key_X             : 'Key_X',
        Qt.Key_Y             : 'Key_Y',
        Qt.Key_Z             : 'Key_Z',
        Qt.Key_BracketLeft   : 'Key_BracketLeft',
        Qt.Key_Backslash     : 'Key_Backslash',
        Qt.Key_BracketRight  : 'Key_BracketRight',
        Qt.Key_AsciiCircum   : 'Key_AsciiCircum',
        Qt.Key_Underscore    : 'Key_Underscore',
        Qt.Key_QuoteLeft     : 'Key_QuoteLeft',
        Qt.Key_BraceLeft     : 'Key_BraceLeft',
        Qt.Key_Bar           : 'Key_Bar',
        Qt.Key_BraceRight    : 'Key_BraceRight',
        Qt.Key_AsciiTilde    : 'Key_AsciiTilde',
        Qt.Key_nobreakspace  : 'Key_nobreakspace',
        Qt.Key_exclamdown    : 'Key_exclamdown',
        Qt.Key_cent          : 'Key_cent',
        Qt.Key_sterling      : 'Key_sterling',
        Qt.Key_currency      : 'Key_currency',
        Qt.Key_yen           : 'Key_yen',
        Qt.Key_brokenbar     : 'Key_brokenbar',
        Qt.Key_section       : 'Key_section',
        Qt.Key_diaeresis     : 'Key_diaeresis',
        Qt.Key_copyright     : 'Key_copyright',
        Qt.Key_ordfeminine   : 'Key_ordfeminine',
        Qt.Key_guillemotleft : 'Key_guillemotleft',
        Qt.Key_notsign       : 'Key_notsign',
        Qt.Key_hyphen        : 'Key_hyphen',
        Qt.Key_registered    : 'Key_registered',
        Qt.Key_macron        : 'Key_macron',
        Qt.Key_degree        : 'Key_degree',
        Qt.Key_plusminus     : 'Key_plusminus',
        Qt.Key_twosuperior   : 'Key_twosuperior',
        Qt.Key_threesuperior : 'Key_threesuperior',
        Qt.Key_acute         : 'Key_acute',
        Qt.Key_mu            : 'Key_mu',
        Qt.Key_paragraph     : 'Key_paragraph',
        Qt.Key_periodcentered: 'Key_periodcentered',
        Qt.Key_cedilla       : 'Key_cedilla',
        Qt.Key_onesuperior   : 'Key_onesuperior',
        Qt.Key_masculine     : 'Key_masculine',
        Qt.Key_guillemotright: 'Key_guillemotright',
        Qt.Key_onequarter    : 'Key_onequarter',
        Qt.Key_onehalf       : 'Key_onehalf',
        Qt.Key_threequarters : 'Key_threequarters',
        Qt.Key_questiondown  : 'Key_questiondown',
        Qt.Key_Agrave        : 'Key_Agrave',
        Qt.Key_Aacute        : 'Key_Aacute',
        Qt.Key_Acircumflex   : 'Key_Acircumflex',
        Qt.Key_Atilde        : 'Key_Atilde',
        Qt.Key_Adiaeresis    : 'Key_Adiaeresis',
        Qt.Key_Aring         : 'Key_Aring',
        Qt.Key_AE            : 'Key_AE',
        Qt.Key_Ccedilla      : 'Key_Ccedilla',
        Qt.Key_Egrave        : 'Key_Egrave',
        Qt.Key_Eacute        : 'Key_Eacute',
        Qt.Key_Ecircumflex   : 'Key_Ecircumflex',
        Qt.Key_Ediaeresis    : 'Key_Ediaeresis',
        Qt.Key_Igrave        : 'Key_Igrave',
        Qt.Key_Iacute        : 'Key_Iacute',
        Qt.Key_Icircumflex   : 'Key_Icircumflex',
        Qt.Key_Idiaeresis    : 'Key_Idiaeresis',
        Qt.Key_ETH           : 'Key_ETH',
        Qt.Key_Ntilde        : 'Key_Ntilde',
        Qt.Key_Ograve        : 'Key_Ograve',
        Qt.Key_Oacute        : 'Key_Oacute',
        Qt.Key_Ocircumflex   : 'Key_Ocircumflex',
        Qt.Key_Otilde        : 'Key_Otilde',
        Qt.Key_Odiaeresis    : 'Key_Odiaeresis',
        Qt.Key_multiply      : 'Key_multiply',
        Qt.Key_Ooblique      : 'Key_Ooblique',
        Qt.Key_Ugrave        : 'Key_Ugrave',
        Qt.Key_Uacute        : 'Key_Uacute',
        Qt.Key_Ucircumflex   : 'Key_Ucircumflex',
        Qt.Key_Udiaeresis    : 'Key_Udiaeresis',
        Qt.Key_Yacute        : 'Key_Yacute',
        Qt.Key_THORN         : 'Key_THORN',
        Qt.Key_ssharp        : 'Key_ssharp',
        # Qt.Key_agrave        :                'Key_agrave'     ,
        # Qt.Key_aacute        :                'Key_aacute'     ,
        # Qt.Key_acircumflex        :                'Key_acircumflex'     ,
        # Qt.Key_atilde        :                'Key_atilde'     ,
        # Qt.Key_adiaeresis        :                'Key_adiaeresis'     ,
        # Qt.Key_aring        :                'Key_aring'     ,
        #    Qt.Key_ae        :                'Key_ae'     ,
        #    Qt.Key_ccedilla        :                'Key_ccedilla'     ,
        #    Qt.Key_egrave        :                'Key_egrave'     ,
        #    Qt.Key_eacute        :                'Key_eacute'     ,
        #    Qt.Key_ecircumflex        :                'Key_ecircumflex'     ,
        #    Qt.Key_ediaeresis        :                'Key_ediaeresis'     ,
        #    Qt.Key_igrave        :                'Key_igrave'     ,
        #    Qt.Key_iacute        :                'Key_iacute'     ,
        #    Qt.Key_icircumflex        :                'Key_icircumflex'     ,
        #    Qt.Key_idiaeresis        :                'Key_idiaeresis'     ,
        #    Qt.Key_eth        :                'Key_eth'     ,
        #    Qt.Key_ntilde        :                'Key_ntilde'     ,
        #    Qt.Key_ograve        :                'Key_ograve'     ,
        #    Qt.Key_oacute        :                'Key_oacute'     ,
        #    Qt.Key_ocircumflex        :                'Key_ocircumflex'     ,
        #    Qt.Key_otilde        :                'Key_otilde'     ,
        #    Qt.Key_odiaeresis        :                'Key_odiaeresis'     ,
        #    Qt.Key_division        :                'Key_division'     ,
        #    Qt.Key_oslash        :                'Key_oslash'     ,
        #    Qt.Key_ugrave        :                'Key_ugrave'     ,
        #    Qt.Key_uacute        :                'Key_uacute'     ,
        #    Qt.Key_ucircumflex        :                'Key_ucircumflex'     ,
        #    Qt.Key_udiaeresis        :                'Key_udiaeresis'     ,
        #    Qt.Key_yacute        :                'Key_yacute'     ,
        #    Qt.Key_thorn        :                'Key_thorn'     ,
        #    Qt.Key_ydiaeresis        :                'Key_ydiaeresis'     ,
        #    Qt.Key_Back        :                'Key_Back'     ,
        #    Qt.Key_Forward        :                'Key_Forward'     ,
        #    Qt.Key_Stop        :                'Key_Stop'     ,
        #    Qt.Key_Refresh        :                'Key_Refresh'     ,
        #    Qt.Key_VolumeDown        :                'Key_VolumeDown'     ,
        #    Qt.Key_VolumeMute        :                'Key_VolumeMute'     ,
        #    Qt.Key_VolumeUp        :                'Key_VolumeUp'     ,
        #    Qt.Key_BassBoost        :                'Key_BassBoost'     ,
        #    Qt.Key_BassUp        :                'Key_BassUp'     ,
        #    Qt.Key_BassDown        :                'Key_BassDown'     ,
        #    Qt.Key_TrebleUp        :                'Key_TrebleUp'     ,
        #    Qt.Key_TrebleDown        :                'Key_TrebleDown'     ,
        #    Qt.Key_MediaPlay        :                'Key_MediaPlay'     ,
        #    Qt.Key_MediaStop        :                'Key_MediaStop'     ,
        #    Qt.Key_MediaPrev        :                'Key_MediaPrev'     ,
        #    Qt.Key_MediaNext        :                'Key_MediaNext'     ,
        #    Qt.Key_MediaRecord        :                'Key_MediaRecord'     ,
        #    Qt.Key_HomePage        :                'Key_HomePage'     ,
        #    Qt.Key_Favorites        :                'Key_Favorites'     ,
        #    Qt.Key_Search        :                'Key_Search'     ,
        #    Qt.Key_Standby        :                'Key_Standby'     ,
        #    Qt.Key_OpenUrl        :                'Key_OpenUrl'     ,
        #    Qt.Key_LaunchMail        :                'Key_LaunchMail'     ,
        #    Qt.Key_LaunchMedia        :                'Key_LaunchMedia'     ,
        #    Qt.Key_Launch0        :                'Key_Launch0'     ,
        #    Qt.Key_Launch1        :                'Key_Launch1'     ,
        #    Qt.Key_Launch2        :                'Key_Launch2'     ,
        #    Qt.Key_Launch3        :                'Key_Launch3'     ,
        #    Qt.Key_Launch4        :                'Key_Launch4'     ,
        #    Qt.Key_Launch5        :                'Key_Launch5'     ,
        #    Qt.Key_Launch6        :                'Key_Launch6'     ,
        #    Qt.Key_Launch7        :                'Key_Launch7'     ,
        #    Qt.Key_Launch8        :                'Key_Launch8'     ,
        #    Qt.Key_Launch9        :                'Key_Launch9'     ,
        #    Qt.Key_LaunchA        :                'Key_LaunchA'     ,
        #    Qt.Key_LaunchB        :                'Key_LaunchB'     ,
        #    Qt.Key_LaunchC        :                'Key_LaunchC'     ,
        #    Qt.Key_LaunchD        :                'Key_LaunchD'     ,
        #    Qt.Key_LaunchE        :                'Key_LaunchE'     ,
        #    Qt.Key_LaunchF        :                'Key_LaunchF'     ,
        #    Qt.Key_MediaLast        :                'Key_MediaLast'     ,
        Qt.Key_unknown       : 'Key_unknown',
        Qt.Key_Direction_L   : 'Key_Direction_L',
        Qt.Key_Direction_R   : 'Key_Direction_R',
        }

PEN_STYLES = {
        'no pen'      : Qt.NoPen,
        'solid'       : Qt.SolidLine,
        'dashed'      : Qt.DashLine,
        'dotted'      : Qt.DotLine,
        'dash dot'    : Qt.DashDotLine,
        'dash dot dot': Qt.DashDotDotLine,
        'custom dash' : Qt.CustomDashLine
        }

PEN_STYLES_R = {}
for i in list(PEN_STYLES.keys()):
  PEN_STYLES_R[PEN_STYLES[i]] = i

BUTTON_NAMES = {
        left  : 'left',
        middle: 'middle',
        right : 'right',
        nobut : 'none'
        }

PRESET_COLOURS = {
        "yellow": Qt.yellow
        }


class ModellerRadioButton(QtWidgets.QRadioButton):
  radio_signal = QtCore.pyqtSignal(str, str, str, bool)

  def __init__(self, token_class, token, strID, label, autoexclusive=True, height=20):
    QtWidgets.QRadioButton.__init__(self, label)
    self.token_class = token_class
    self.token = token
    self.strID = strID
    self.setFixedHeight(height)
    self.setAutoExclusive(autoexclusive)
    self.toggled.connect(self.beenToggled)
    self.initialisation = True

  def beenToggled(self, value):
    self.radio_signal.emit(self.token_class, self.token, self.strID, value)


class StackControl():
  def __init__(self, stack, button_up, button_down, icon_left=None, icon_right=None, index=0, identifier='none'):
    self.stack = stack
    self.up = button_up
    self.down = button_down
    self.index = index
    self.identifier = identifier
    self.count = stack.count()
    self.direction = 0
    if icon_left:
      button_down.setIcon(icon_left)
      button_down.setText("")
    if icon_right:
      button_up.setIcon(icon_right)
      button_up.setText("")
    self.showHide()

  def increment(self, step=1):
    self.stepping(step)
    self.showHide()
    self.direction = step
    return self.index

  def decrement(self, step=-1):
    self.stepping(step)
    self.showHide()
    self.direction = step
    return self.index

  def stepping(self, step):
    self.index += step
    if self.index > self.count:
      self.index = self.count
    if self.index < 0:
      self.index = 0

  def reset(self):
    self.index = 0
    self.showHide()

  def showHide(self):
    if self.index == 0:
      self.down.hide()
      self.up.show()
    elif self.index == self.count - 1:
      self.down.show()
      self.up.hide()
    else:
      self.down.show()
      self.up.show()

    self.stack.setCurrentIndex(self.index)
    # print(">>>stack countrol %s seeting index : %s"%(self.identifier, self.index))

  def currentIndex(self):
    return self.stack.currentIndex()


def clearLayout(layout):
  """ removes the widgets from the layout
   had some problems with memory - seems to resolved with phyt 5
   """
  # print("clean layout", layout, layout.count())
  if layout.count() > 0:
    for i in reversed(range(layout.count())):
      widgetToRemove = layout.itemAt(i).widget()
      # remove it from the layout list
      layout.removeWidget(widgetToRemove)
      # print("remove", widgetToRemove)
      # remove it from the gui
      try:
        widgetToRemove.setParent(None)
      except:
        pass


# def clearLayout(layout):
#   while layout.count():
#     child = layout.takeAt(0)
#     if child.widget() is not None:
#       child.widget().deleteLater()
#     elif child.layout() is not None:
#       clearLayout(child.layout())