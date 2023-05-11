#// auth_ Noobj2
#// Copyright (c) 2020-2023 Noobj2

from os.path import dirname
import webbrowser
from aqt.webview import AnkiWebView
from aqt import mw, colors
from aqt.qt import *
from aqt.theme import theme_manager
from aqt.utils import showInfo
from anki import version
import anki
from anki.lang import is_rtl
from anki.utils import is_mac, is_win
anki_version = int(version.replace('.', ''))

config = mw.addonManager.getConfig(__name__)

def refreshConfig():
    global C_font, C_fontSize
    C_font = config["Interface Font"]
    C_fontSize = config["Font Size"]

class FontDialog(QDialog):
    def __init__(self, parent=None):
        super(FontDialog, self).__init__(parent)
        self.mainWindow()
    def mainWindow(self):
        addon_path = dirname(__file__)
        self.choose_font()
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.setLayout(self.layout)
        self.setWindowTitle("Anki - Change Font")
        self.setWindowIcon(QIcon(addon_path + "/icon.png"))

    def choose_font(self):
        addon_path = dirname(__file__)
        refreshConfig()
        font_label = QLabel("Font: ")
        font_label.setFixedWidth(100)
        self.interface_font = QFontComboBox()
        self.interface_font.setFixedWidth(200)
        self.interface_font.setCurrentFont(QFont(C_font))
        size_label = QLabel("Font Size: ")
        size_label.setFixedWidth(100)
        self.font_size = QSpinBox()
        self.font_size.setFixedWidth(200)
        self.font_size.setValue(C_fontSize)
        self.font_size.setSuffix("px")
        apply_button = QPushButton("&Apply")
        apply_button.clicked.connect(lambda: self.onApply())
        apply_button.clicked.connect(lambda: self.hide())
        restore_button = QPushButton("&Default")
        restore_button.clicked.connect(lambda: self.restore_defaults())
        restore_button.clicked.connect(lambda: self.hide())
        cancel_button = QPushButton("&Cancel")
        cancel_button.clicked.connect(lambda: self.hide())
        buyMeACoffee_button = QPushButton()
        buyMeACoffee_button.setIcon(QIcon(addon_path + "/bmac.png"))
        buyMeACoffee_button.setIconSize(QSize(130,40))
        buyMeACoffee_button.setGeometry(QRect(1030, 500, 161, 61))
        buyMeACoffee_button.clicked.connect(lambda: webbrowser.open('https://www.buymeacoffee.com/noobj2'))
        font_line = QHBoxLayout()
        font_line.addWidget(font_label)
        font_line.addStretch()
        font_line.addWidget(self.interface_font)
        size_line = QHBoxLayout()
        size_line.addWidget(size_label)
        size_line.addStretch()
        size_line.addWidget(self.font_size)
        button_line = QHBoxLayout()
        button_line.addWidget(apply_button)
        button_line.addWidget(restore_button)
        button_line.addWidget(cancel_button)
        buyMeACoffee_line = QHBoxLayout()
        buyMeACoffee_line.addWidget(buyMeACoffee_button)
        self.layout = QVBoxLayout()
        self.layout.addLayout(font_line)
        self.layout.addLayout(size_line)
        self.layout.addLayout(button_line)
        self.layout.addLayout(buyMeACoffee_line)

    def onApply(self):
        conf = {
        "Interface Font": self.interface_font.currentFont().family(),
        "Font Size": self.font_size.value()
        }
        mw.addonManager.writeConfig(__name__, conf)
        showInfo("Changes will take effect after you restart anki.", title="Anki - Change Font")

    def restore_defaults(self):
        if is_win:
            font = "Segoe UI"
            font_size = 12
        elif is_mac:
            font = "Helvetica"
            font_size = 15
        else:
            font = "Segoe UI"
            font_size = 14
        conf = {
        "Interface Font": font,
        "Font Size": font_size
        }
        mw.addonManager.writeConfig(__name__, conf)
        showInfo("Changes will take effect after you restart anki.", title="Anki - Change Font")

def standard_css_new(self) -> str:
    color_hl = theme_manager.var(colors.BORDER_FOCUS)

    family = config["Interface Font"]
    font_size = config["Font Size"]

    if is_win:
        # T: include a font for your language on Windows, eg: "Segoe UI", "MS Mincho"
        button_style = "button { font-size: 12px; font-family:%s; }" % family
        button_style += "\n:focus { outline: 1px solid %s; }" % color_hl
        font = f"font-size:{font_size}px;font-family:{family};"
    elif is_mac:
        font = f'font-size:{font_size}px;font-family:"{family}";'
        button_style = """
button { -webkit-appearance: none; background: #fff; border: 1px solid #ccc;
border-radius:5px; font-family: %s }""" % family
    else:
        color_hl_txt = palette.color(QPalette.HighlightedText).name()
        color_btn = palette.color(QPalette.Button).name()
        font = f'font-size:{font_size}px;font-family:"{family}";'
        button_style = """
/* Buttons */
button{
    background-color: %(color_btn)s;
    font-family:"%(family)s"; }
button:focus{ border-color: %(color_hl)s }
button:active, button:active:hover { background-color: %(color_hl)s; color: %(color_hl_txt)s;}
/* Input field focus outline */
textarea:focus, input:focus, input[type]:focus, .uneditable-input:focus,
div[contenteditable="true"]:focus {
outline: 0 none;
border-color: %(color_hl)s;
}""" % {
            "family": family,
            "color_btn": color_btn,
            "color_hl": color_hl,
            "color_hl_txt": color_hl_txt,
        }

    zoom = self.zoomFactor()

    window_bg_day = self.get_window_bg_color(False).name()
    window_bg_night = self.get_window_bg_color(True).name()
    body_bg = window_bg_night if theme_manager.night_mode else window_bg_day

    if is_rtl(anki.lang.currentLang):
        lang_dir = "rtl"
    else:
        lang_dir = "ltr"

    return f"""
body {{ zoom: {zoom}; background-color: {body_bg}; direction: {lang_dir}; }}
html {{ {font} }}
{button_style}
:root {{ --window-bg: {window_bg_day} }}
:root[class*=night-mode] {{ --window-bg: {window_bg_night} }}
"""

def open_window():
    font_dialog = FontDialog()
    font_dialog.exec()

action = QAction("Change Interface &Font", mw)
action.triggered.connect(open_window)
mw.form.menuTools.addAction(action)
mw.addonManager.setConfigAction(__name__, open_window)
AnkiWebView.standard_css = standard_css_new