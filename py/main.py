from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice, QThread, pyqtSignal, QObject
import numpy as np
import time
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys


class Logger(QObject):
    finish_signal = pyqtSignal()

    def set_data(self, _timeline, _voltage):
        self.timeline = _timeline
        self.voltage = _voltage

    def run(self):
        tmp_voltage = map(str, self.voltage)
        tmp_timeline = map(str, self.timeline)
        with open('../data/data.txt', 'w') as f:
            f.write(';'.join(tmp_voltage) + '\n')
            f.write(';'.join(tmp_timeline) + '\n')
        self.finish_signal.emit()


logger_thread = QThread()
logger = Logger()
logger.moveToThread(logger_thread)

app = QtWidgets.QApplication([])
ui = uic.loadUi("front/design.ui")

serial = QSerialPort()
serial.setBaudRate(115200)
portList = []
ports = QSerialPortInfo().availablePorts()

for port in ports:
    portList.append(port.portName())

ui.port_combo_box.addItems(portList)
opened = False
logging = False
start_time = 0

timeline = []
voltage = []

ui.input_lcd.setSmallDecimalPoint(True)
ui.output_lcd.setSmallDecimalPoint(True)
ui.input_lcd.display('0 U')
ui.output_lcd.display('0 U')

tick = time.time()


def start_log():
    global logging, voltage, timeline, start_time, tick
    logging = True
    start_time = time.time()


def download_data():
    global logging, voltage, timeline, start_time, logger
    logging = False

    logger.set_data(timeline, voltage)
    logger_thread.start()


def on_read():
    global logging, voltage, timeline, start_time, tick
    if not serial.canReadLine():
        return None     # выходим если нечего читать

    rx = serial.readLine()
    rxs = str(rx, 'utf-8').strip()
    data = map(int, rxs.split(','))
    key, param = data

    if key == 0:
        ui.connection_info_label.setText("Подключено")

    if key == 1:
        vol = np.round(param * 3.3 / 4095, 3)
        ui.input_lcd.display(f'{vol} U')
        if logging:
            if time.time() - tick > 0.1:
                tick = time.time()
                voltage.append(vol)
                timeline.append(time.time() - start_time)
                if len(voltage) > 1:
                    ui.graph.plot(timeline[-2:], voltage[-2:])

    if key == 2:
        print(param)
        vol = np.round(param * 3.3 / 4095, 3)
        ui.output_lcd.display(f'{vol} U')

    serial.write('1,0;'.encode('UTF-8'))


def make_connection():
    serial.setPortName(ui.port_combo_box.currentText())
    serial.open(QIODevice.ReadWrite)


def set_voltage():
    val = ui.voltageSpinBox.value()
    val = int(val * 4095 / 3.3)
    ui.voltageSpinBox.setValue(val * 3.3 / 4095)
    param = str(val).rjust(4, '0')
    txs = f"2,{param};"
    print(txs)
    serial.write(txs.encode('UTF-8'))


def close_slot():
    serial.close()


serial.readyRead.connect(on_read)

ui.connect_button.clicked.connect(make_connection)
ui.set_voltage_button.clicked.connect(set_voltage)
ui.start_stop_button.clicked.connect(start_log)
ui.download_button.clicked.connect(download_data)

# поведение для начала и конца логгирования
logger_thread.started.connect(logger.run)
logger.finish_signal.connect(logger_thread.quit)

# чистим
logger.finish_signal.connect(logger.deleteLater)
logger_thread.finished.connect(logger_thread.deleteLater)


ui.show()
app.aboutToQuit.connect(close_slot)
app.exec()
