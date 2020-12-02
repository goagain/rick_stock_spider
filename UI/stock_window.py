import sys
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QApplication,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QHBoxLayout,
    QVBoxLayout,
    QListView,
    QListWidgetItem,
    QWidgetItem,
    QCheckBox,
    QListWidget,
    QSizePolicy,
    QGraphicsScene,
    QDialog
)
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
import matplotlib
import matplotlib.pyplot as plot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import random
import yfinance as yf
import mplfinance as mpf
from matplotlib.figure import Figure

from core.spider import Spider
matplotlib.use('qt5agg')


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi('./res/main.ui', self)
        self.url_list = set()

        self.spider = Spider()
        self.news_list = self.findChild(QListWidget, "listWidget")
        self.news_list.itemClicked.connect(self.on_click_news)
        self.next_update.clicked.connect(self.on_click_refresh)
        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update_feeds)
        self.on_start()

        self.ticker = QTimer(self)
        self.ticker.timeout.connect(self.on_tick)
        self.ticker.start(1000)

        self.actionAbout.triggered.connect(self.on_click_about)
        self.clicked = None
        self.stock_index = 0

        self.nextButton.clicked.connect(self.on_click_next)
        self.previousButton.clicked.connect(self.on_click_previous)
    def on_click_about(self):
        widget = QDialog(self)
        loadUi('./res/about.ui', widget)
        widget.show()

    def on_start(self):
        self.update_feeds()

    def on_click_refresh(self):
        self.update_feeds()

    def update_feeds(self):
        try:
            model = self.spider.get_model()
            self.refresh(model)
            self.timer.start(30000)
        except Exception as ex:
            print(ex)

    def on_tick(self):
        try:
            self.next_update.setText(
                f'Next Update({self.timer.remainingTime()//1000}s)')
        except Exception as ex:
            print(ex)

    def refresh(self, model):
        try:
            for data in model[::-1]:
                if data['url'] in self.url_list:
                    continue
                self.url_list.add(data['url'])
                item = NewsWidgetItem()

                self.news_list.insertItem(0, item)
                self.news_list.setItemWidget(item, item.widget)
                item.set_data(data)
        except Exception as ex:
            print(ex)

    def on_click_news(self, clicked):
        try:
            self.clicked = clicked
            self.bodyBrowser.setText(clicked.data['body'])
            if len(self.clicked.data['symbols']):
                self.show_stock(0)
            else:
                self.priceGraphicView.hide()
                self.previousButton.setText(f'No Previous Stock')
                self.previousButton.setEnabled(False)
                self.nextButton.setText(f'No Next Stock')
                self.nextButton.setEnabled(False)
        except Exception as ex:
            print(ex)

    def show_stock(self, index):
        try:
            symbols = self.clicked.data['symbols']
            if symbols:
                symbol = symbols[index]
                # get historical market data
                # Initialize a FigureCanvas
                graphicscene = QGraphicsScene()
                self.priceGraphicView.setScene(graphicscene)

                canvas = Figure_Canvas()
                graphicscene.addWidget(canvas)

                canvas.plot_candle(symbol)
                self.priceGraphicView.show()

                self.stock_index = index

                if len(symbols) > index + 1:
                    self.nextButton.setText(f'Next Stock({symbols[index + 1]})')
                    self.nextButton.setEnabled(True)
                else:
                    self.nextButton.setText(f'No Next Stock')
                    self.nextButton.setEnabled(False)
                if index > 0:
                    self.previousButton.setText(f'Previous Stock({symbols[index - 1]})')
                    self.previousButton.setEnabled(True)
                else:
                    self.previousButton.setText(f'No Previous Stock')
                    self.previousButton.setEnabled(False)

            else:
                self.priceGraphicView.hide()
        except Exception as ex:
            self.priceGraphicView.hide()
            self.previousButton.setText(f'No Previous Stock')
            self.previousButton.setEnabled(False)
            self.nextButton.setText(f'No Next Stock')
            self.nextButton.setEnabled(False)

            print(ex)

    def on_click_next(self):
        self.show_stock(self.stock_index + 1)

    def on_click_previous(self):
        self.show_stock(self.stock_index - 1)


class Figure_Canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=7, height=8, dpi=100):
        self.fig = mpf.figure(figsize=(width, height), dpi=dpi)

        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(211)
        self.axes2 = self.fig.add_subplot(212)

    def plot_candle(self, symbol):
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='3mo', interval='1d')
        mpf.plot(hist, ax=self.axes, type='candlestick',
                 volume=self.axes2, axtitle=symbol, mav=5)


class NewsWidgetItem(QListWidgetItem):
    def __init__(self, parent=None):
        super(NewsWidgetItem, self).__init__(parent)
        self.widget = QWidget()
        loadUi('./res/news.ui', self.widget)
        self.setSizeHint(self.widget.sizeHint())

        self.data = None

    def set_data(self, data):
        self.data = data
        self.title = data['title']
        self.body = data['body']
        self.time = data['time']
        if data['symbols']:
            self.symbols = f"Related Stock: {' '.join(data['symbols'])}"
        else:
            self.symbols = "No Related Stock"

    @property
    def title(self):
        return self.widget.lableTitle.text()

    @title.setter
    def title(self, text):
        self.widget.lableTitle.setText(text)

    @property
    def body(self):
        return self.widget.labelBody.text()

    @body.setter
    def body(self, text):
        self.widget.labelBody.setText(text)

    @property
    def time(self):
        return self.widget.labelTime.text()

    @time.setter
    def time(self, text):
        self.widget.labelTime.setText(text)

    @property
    def symbols(self):
        return self.widget.lableStock.text()

    @symbols.setter
    def symbols(self, text):
        self.widget.lableStock.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    app.exit(app.exec_())
