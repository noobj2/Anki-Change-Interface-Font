#// auth_ Mohamad Janati
#// Copyright (c) 2020-2021 Mohamad Janati (freaking stupid, right? :|)

from os.path import dirname
from aqt.webview import AnkiWebView
from aqt.webview import WebContent
from typing import Optional, List, Any
from aqt import mw
from aqt import gui_hooks
from aqt.qt import *
from aqt.theme import theme_manager
from aqt.utils import showInfo
from anki import version
import anki
from anki.lang import is_rtl
from anki.utils import isLin, isMac, isWin
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
        self.setWindowTitle("Anki [Change Font]")
        self.setWindowIcon(QIcon(addon_path + "/icon.png"))

    def choose_font(self):
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
        self.layout = QVBoxLayout()
        self.layout.addLayout(font_line)
        self.layout.addLayout(size_line)
        self.layout.addLayout(button_line)

    def onApply(self):
        conf = {
        "Interface Font": self.interface_font.currentFont().family(),
        "Font Size": self.font_size.value()
        }
        mw.addonManager.writeConfig(__name__, conf)
        showInfo("Changes will take effect after you restart anki.", title="Anki [Change Font]")

    def restore_defaults(self):
        if isWin:
            font = "Segoe UI"
            font_size = 12
        elif isMac:
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
        showInfo("Changes will take effect after you restart anki.", title="Anki [Change Font]")

def stdHtml_new(
    self,
    body: str,
    css: Optional[List[str]] = None,
    js: Optional[List[str]] = None,
    head: str = "",
    context: Optional[Any] = None,
    ):

    web_content = WebContent(
        body=body,
        head=head,
        js=["webview.js"] + (["jquery.js"] if js is None else js),
        css=["webview.css"] + ([] if css is None else css),
    )

    gui_hooks.webview_will_set_content(web_content, context)

    palette = self.style().standardPalette()
    color_hl = palette.color(QPalette.Highlight).name()

    family = config["Interface Font"]
    font_size = config["Font Size"]

    if isWin:
        # T: include a font for your language on Windows, eg: "Segoe UI", "MS Mincho"
        # family = _('"Courier"')
        widgetspec = "button { font-family:%s; }" % family
        widgetspec += "\n:focus { outline: 1px solid %s; }" % color_hl
        fontspec = "font-size:{}px; font-family:{};".format(font_size, family)
    elif isMac:
        # family = "Helvetica"
        fontspec = 'font-size:{}px; font-family:"{}";'.format(font_size, family)
        widgetspec = """
        button { -webkit-appearance: none; background: #fff; border: 1px solid #ccc;
        border-radius:5px; font-family: %s }""" % family
    else:
        # family = self.font().family()
        color_hl_txt = palette.color(QPalette.HighlightedText).name()
        color_btn = palette.color(QPalette.Button).name()
        fontspec = 'font-size:{}px;font-family:"{}";'.format(font_size, family)
        widgetspec = """
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

    csstxt = "\n".join(self.bundledCSS(fname) for fname in web_content.css)
    jstxt = "\n".join(self.bundledScript(fname) for fname in web_content.js)

    from aqt import mw

    head = mw.baseHTML() + csstxt + jstxt + web_content.head

    body_class = theme_manager.body_class()

    html = """
    <!doctype html>
    <html><head>
    <title>{}</title>

    <style>
    body {{ zoom: {}; background: {}; {} }}
    {}
    </style>

    {}
    </head>

    <body class="{}">{}</body>
    </html>""".format(
            self.title,
            self.zoomFactor(),
            self._getWindowColor().name(),
            fontspec,
            widgetspec,
            head,
            body_class,
            web_content.body,
            )
    # print(html)
    self.setHtml(html)

def stdHtml_old(self, body, css=None, js=None, head=""):
    if css is None:
        css = []
    if js is None:
        js = ["jquery.js"]

    palette = self.style().standardPalette()
    color_hl = palette.color(QPalette.Highlight).name()

    family = config["Interface Font"]
    font_size = config["Font Size"]

    if isWin:
        #T: include a font for your language on Windows, eg: "Segoe UI", "MS Mincho"
        # family = _('"Segoe UI"')
        widgetspec = "button { font-size: 12px; font-family:%s; }" % family
        widgetspec += "\n:focus { outline: 1px solid %s; }" % color_hl
        fontspec = 'font-size:{}px; font-family:"{}";'.format(font_size, family)
    elif isMac:
        # family="Helvetica"
        fontspec = 'font-size:{}px; font-family:"{}";'.format(font_size, family)
        widgetspec = """
    button { font-size: 13px; -webkit-appearance: none; background: #fff; border: 1px solid #ccc;
    border-radius:5px; font-family: %s }""" % family
    else:
        # family = self.font().family()
        color_hl_txt = palette.color(QPalette.HighlightedText).name()
        color_btn = palette.color(QPalette.Button).name()
        fontspec = 'font-size:{}px; font-family:"{}";'.format(font_size, family)
        widgetspec = """
    /* Buttons */
    button{ font-size:14px; -webkit-appearance:none; outline:0;
        background-color: %(color_btn)s; border:1px solid rgba(0,0,0,.2);
        border-radius:2px; height:24px; font-family:"%(family)s"; }
    button:focus{ border-color: %(color_hl)s }
    button:hover{ background-color:#fff }
    button:active, button:active:hover { background-color: %(color_hl)s; color: %(color_hl_txt)s;}
    /* Input field focus outline */
    textarea:focus, input:focus, input[type]:focus, .uneditable-input:focus,
    div[contenteditable="true"]:focus {
    outline: 0 none;
    border-color: %(color_hl)s;
    }""" % {"family": family, "color_btn": color_btn,
        "color_hl": color_hl, "color_hl_txt": color_hl_txt}

    csstxt = "\n".join([self.bundledCSS("webview.css")]+
                       [self.bundledCSS(fname) for fname in css])
    jstxt = "\n".join([self.bundledScript("webview.js")]+
                      [self.bundledScript(fname) for fname in js])
    from aqt import mw
    head =  mw.baseHTML() + head + csstxt + jstxt

    html = """
    <!doctype html>
    <html><head>
    <title>{}</title>

    <style>
    body {{ zoom: {}; background: {}; {} }}
    {}
    </style>

    {}
    </head>

    <body>{}</body>
    </html>""".format(self.title, self.zoomFactor(), self._getWindowColor().name(),
                  fontspec, widgetspec, head, body)
    #print(html)
    self.setHtml(html)


def standard_css_old(self) -> str:
    palette = self.style().standardPalette()
    color_hl = palette.color(QPalette.Highlight).name()

    family = config["Interface Font"]
    font_size = config["Font Size"]

    if isWin:
        # T: include a font for your language on Windows, eg: "Segoe UI", "MS Mincho"
        button_style = "button { font-size: 12px; font-family:%s; }" % family
        button_style += "\n:focus { outline: 1px solid %s; }" % color_hl
        font = "font-size:{}px;font-family:{};".format(font_size, family)
    elif isMac:
        font = 'font-size:{}px;font-family:"{}";'.format(font_size, family)
        button_style = """
button { -webkit-appearance: none; background: #fff; border: 1px solid #ccc;
border-radius:5px; font-family: %s }""" % family
    else:
        color_hl_txt = palette.color(QPalette.HighlightedText).name()
        color_btn = palette.color(QPalette.Button).name()
        font = 'font-size:{}px;font-family:"{}";'.format(font_size, family)
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
    background = self._getWindowColor().name()

    if is_rtl(anki.lang.currentLang):
        lang_dir = "rtl"
    else:
        lang_dir = "ltr"

    return f"""
body {{ zoom: {zoom}; background: {background}; direction: {lang_dir}; {font} }}
{button_style}
:root {{ --window-bg: {background} }}
:root[class*=night-mode] {{ --window-bg: {background} }}
"""

def standard_css_new(self) -> str:
    palette = theme_manager.default_palette
    color_hl = palette.color(QPalette.Highlight).name()

    family = config["Interface Font"]
    font_size = config["Font Size"]

    if isWin:
        # T: include a font for your language on Windows, eg: "Segoe UI", "MS Mincho"
        button_style = "button { font-size: 12px; font-family:%s; }" % family
        button_style += "\n:focus { outline: 1px solid %s; }" % color_hl
        font = f"font-size:{font_size}px;font-family:{family};"
    elif isMac:
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
if anki_version < 2122:
    AnkiWebView.stdHtml = stdHtml_old
elif 2121 < anki_version < 2136:
    AnkiWebView.stdHtml = stdHtml_new
elif 2135 < anki_version < 2145:
    AnkiWebView.standard_css = standard_css_old
else:
    AnkiWebView.standard_css = standard_css_new
