#!/usr/bin/env python2

import sys

# PyQt4 is not released for python3, sigh...
# The combination of Python2 and Qt4 has a disadvantage for QString.
# This forces interpretor to handle QString as usual unicode string.
import sip
sip.setapi('QString', 2)
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt4.QtGui import QToolButton, QGroupBox, QLineEdit, QLabel

# Hinawa-1.0 gir
from gi.repository import Hinawa

# create sound unit
def handle_lock_status(snd_unit, status):
    if status:
        print("streaming is locked.");
    else:
        print("streaming is unlocked.");
try:
    snd_unit = Hinawa.SndUnit.new("hw:0")
except Exception as e:
    print(e)
    sys.exit()
print('Sound device info:')
print(' name:\t{0}'.format(snd_unit.get_property("name")))
print(' iface:\t{0}'.format(snd_unit.get_property("iface")))
print(' card:\t{0}'.format(snd_unit.get_property("card")))
print(' device:\t{0}'.format(snd_unit.get_property("device")))
print(' GUID:\t{0:016x}'.format(snd_unit.get_property("guid")))
snd_unit.connect("lock-status", handle_lock_status)

# create FireWire unit
def handle_bus_update(fw_unit):
	print(fw_unit.get_property('generation'))
path = "/dev/%s" % snd_unit.get_property("device")
try:
    fw_unit = Hinawa.FwUnit.new(path)
except Exception as e:
    print(e)
    sys.exit()
snd_unit.connect("lock-status", handle_lock_status)

# start listening
try:
    snd_unit.listen()
    fw_unit.listen()
except Exception as e:
    print(e)
    sys.exit()

# create firewire responder
def handle_request(resp, tcode, frame, private_data):
    print('Requested with tcode {0}:'.format(tcode))
    for i in range(len(frame)):
        print(' [{0:02d}]: 0x{1:02x}'.format(i, frame[i]))
    return True
try:
    resp = Hinawa.FwResp.new(fw_unit)
    resp.register(0xfffff0000d00, 0x100, 0)
    resp.connect('requested', handle_request)
except Exception as e:
    print(e)
    sys.exit()

# create firewire requester
try:
    req = Hinawa.FwReq.new()
except Exception as e:
    print(e)
    sys.exit()

# Fireworks/BeBoB/OXFW supports FCP and some AV/C commands
if snd_unit.get_property('iface') is not 1:
    request = bytearray(8)
    request[0] = 0x01
    request[1] = 0xff
    request[2] = 0x19
    request[3] = 0x00
    request[4] = 0xff
    request[5] = 0xff
    request[6] = 0xff
    request[7] = 0xff
    try:
        fcp = Hinawa.FwFcp.new()
        fcp.listen(fw_unit)
        response = fcp.transact(request)
    except Exception as e:
        print(e)
        sys.exit()
    print('FCP Response:')
    for i in range(len(response)):
        print(' [{0:02d}]: 0x{1:02x}'.format(i, ord(response[i])))
    fcp.unlisten()

# Echo Fireworks Transaction
from array import array
if snd_unit.get_property("iface") is 2:
    # The width with 'L' parameter is depending on environment.
    args = array('L')
    if args.itemsize is not 4:
        args = array('I')
    args.append(5)
    try:
        eft = Hinawa.SndEft.new(snd_unit)
        params = eft.transact(6, 1, args)
    except Exception as e:
        print(e)
        sys.exit()
    print('Echo Fireworks Transaction Response:')
    for i in range(len(params)):
        print(" [{0:02d}]: {1:08x}".format(i, params[i]))

# Dice notification
def handle_notification(self, message):
    print("Dice Notification: {0:08x}".format(message))
if snd_unit.get_property('iface') is 1:
    try:
        dice_notify= Hinawa.SndDiceNotify.new(snd_unit)
    except Exception as e:
        print(e)
        sys.exit()
    dice_notify.connect('notified', handle_notification)

# GUI
class Sample(QWidget):
    def __init__(self, parent=None):
        super(Sample, self).__init__(parent)

        self.setWindowTitle("Hinawa-1.0 gir sample with PyQt4")

        layout = QVBoxLayout()
        self.setLayout(layout)

        top_grp = QGroupBox(self)
        top_layout = QHBoxLayout()
        top_grp.setLayout(top_layout)
        layout.addWidget(top_grp)

        buttom_grp = QGroupBox(self)
        buttom_layout = QHBoxLayout()
        buttom_grp.setLayout(buttom_layout)
        layout.addWidget(buttom_grp)

        button = QToolButton(top_grp)
        button.setText('transact')
        top_layout.addWidget(button)
        button.clicked.connect(self.transact)

        close = QToolButton(top_grp)
        close.setText('close')
        top_layout.addWidget(close)
        close.clicked.connect(app.quit)

        self.addr = QLineEdit(buttom_grp)
        self.addr.setText('0xfffff0000984')
        buttom_layout.addWidget(self.addr)

        self.value = QLabel(buttom_grp)
        self.value.setText('00000000')
        buttom_layout.addWidget(self.value)

    def transact(self, val):
        try:
            addr = int(self.addr.text(), 16)
            val = req.read(fw_unit, addr, 4)
        except Exception as e:
            print(e)
            return
            
        template = "0x{0:02x}{1:02x}{2:02x}{3:02x}"
        self.value.setText(template.format(ord(val[0]), ord(val[1]), ord(val[2]), ord(val[3])))
        print(self.value.text())

app = QApplication(sys.argv)
sample = Sample()

sample.show()
app.exec_()

sys.exit()