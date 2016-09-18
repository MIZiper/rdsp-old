from PyQt4 import QtGui
from guiqwt.plot import CurveWidget
from PyQt4.QtCore import Qt
from guiqwt.builder import make
import numpy as np

class AirGapResult(QtGui.QWidget):
    def __init__(self, result):
        QtGui.QWidget.__init__(self)

        self.numOfSensor = result.size
        (self.numOfPole,self.numOfSpeed) = result[0]['data'].shape
        
        a = np.array([c['data'] for c in result])
        self.max = a.max()
        self.min = a.min()
        self.range = (self.max-self.min)/8*10

        # sort result by angle
        t = [(x['angle'],i,x) for i,x in enumerate(result)]
        t.sort()
        result = [s[2] for s in t]
        self.result = result

        # append first angle to close the loop
        r = {'angle':result[0]['angle']+360,'data':result[0]['data']}
        result.append(r)

        self.poleIndex = 0
        self.speedIndex = 0
        self.sensorIndex = 0

        self.initUi()
        self.orbitPlot()

    def initUi(self):
        layout = QtGui.QVBoxLayout(self)
        
        curve_plot = CurveWidget()
        curve_plot.register_all_curve_tools()
        curve_rotor = make.curve([],[])
        curve_stator = make.curve([],[])
        curve_eccent = make.circle(0,0,0,0)
        plot = curve_plot.plot
        # plot.setAxisScale(0,-self.range,self.range)
        # plot.setAxisScale(2,-self.range,self.range)
        plot.add_item(curve_rotor)
        plot.add_item(curve_stator)
        plot.add_item(curve_eccent)
        self.curve_rotor = curve_rotor
        self.curve_stator = curve_stator
        self.curve_plot = curve_plot
        self.curve_eccent = curve_eccent
        
        info_layout = QtGui.QVBoxLayout()
        eccent_grp = QtGui.QGroupBox("Eccentricity")
        eccent_layout = QtGui.QVBoxLayout(eccent_grp)
        eccent_x_lbl = QtGui.QLabel("X")
        eccent_x = QtGui.QLabel('0')
        eccent_y_lbl = QtGui.QLabel('Y')
        eccent_y = QtGui.QLabel('0')
        eccent_l_lbl = QtGui.QLabel('(X^2+Y^2)^0.5')
        eccent_l = QtGui.QLabel('0')
        eccent_layout.addWidget(eccent_x_lbl)
        eccent_layout.addWidget(eccent_x)
        eccent_layout.addWidget(eccent_y_lbl)
        eccent_layout.addWidget(eccent_y)
        eccent_layout.addWidget(eccent_l_lbl)
        eccent_layout.addWidget(eccent_l)
        self.eccent_x = eccent_x
        self.eccent_y = eccent_y
        self.eccent_l = eccent_l
        
        statRef_lbl = QtGui.QLabel("Stator Ref.")
        statRef_cmb = QtGui.QComboBox()
        statRef_cmb.addItems([str(i) for i in np.arange(self.numOfPole)+1])
        statRef_cmb.currentIndexChanged.connect(self.pole_changed)
        rotRef_lbl = QtGui.QLabel("Rotor Ref.")
        rotRef_cmb = QtGui.QComboBox()
        rotRef_cmb.addItems([self.result[i]['name'] for i in range(self.numOfSensor)])
        rotRef_cmb.currentIndexChanged.connect(self.sensor_changed)
        info_layout.addWidget(eccent_grp)
        info_layout.addStretch(1)
        info_layout.addWidget(statRef_lbl)
        info_layout.addWidget(statRef_cmb)
        info_layout.addWidget(rotRef_lbl)
        info_layout.addWidget(rotRef_cmb)
        
        speed_slider = QtGui.QSlider(Qt.Horizontal)
        speed_slider.setTickPosition(QtGui.QSlider.TicksAbove)
        speed_slider.setMaximum(self.numOfSpeed-1)
        speed_slider.valueChanged.connect(self.speed_changed)
        speed_label = QtGui.QLabel("Speed")
        self.speed_label = speed_label
        spd_layout = QtGui.QHBoxLayout()
        spd_layout.addWidget(speed_slider)
        spd_layout.addWidget(speed_label)

        up_layout = QtGui.QHBoxLayout()
        up_layout.addWidget(curve_plot,stretch=1)
        up_layout.addLayout(info_layout)
        layout.addLayout(up_layout)
        layout.addLayout(spd_layout)

    def speed_changed(self, index):
        self.speedIndex = index
        self.orbitPlot()

    def pole_changed(self, index):
        self.poleIndex = index
        self.orbitPlot()

    def sensor_changed(self, index):
        self.sensorIndex = index
        self.orbitPlot()

    def orbitPlot(self):
        result = self.result
        poleIdx = self.poleIndex
        sensIdx = self.sensorIndex
        spedIdx = self.speedIndex
        sensNum = self.numOfSensor
        spedNum = self.numOfSpeed
        poleNum = self.numOfPole
        rng = self.range
        mini = self.min
        maxi = self.max

        data = result[sensIdx]['data']
        angle = np.arange(poleNum)/poleNum*360
        radius = (rng*0.1+maxi) - data[:,spedIdx]
        x = np.cos(angle/180*np.pi)*radius
        y = np.sin(angle/180*np.pi)*radius
        self.curve_rotor.set_data(np.append(x,x[0]),np.append(y,y[0]))

        xm = x.mean()
        ym = y.mean()
        self.eccent_x.setText('%.2f' % xm)
        self.eccent_y.setText('%.2f' % ym)
        lm = np.absolute(xm+ym*1j)
        self.eccent_l.setText('%.2f' % lm)
        self.curve_eccent.set_xdiameter(xm,ym,xm,ym)

        angle = np.array([])
        for i in range(1,sensNum+1):
            agl = np.arange(result[i-1]['angle'],result[i]['angle'])
            angle = np.append(angle,agl)
        xp = [r['angle'] for r in result]
        yp = [r['data'][poleIdx,spedIdx] for r in result]
        radius = np.interp(angle,xp,yp) - mini+rng
        x = np.cos(angle/180*np.pi)*radius
        y = np.sin(angle/180*np.pi)*radius
        self.curve_stator.set_data(np.append(x,x[0]),np.append(y,y[0]))

        # self.curve_plot.plot.do_autoscale()
        self.speed_label.setText(
            '%.2f' % result[sensIdx]['speed'][spedIdx]
        )
        
def main():
    from guidata import qapplication
    app = qapplication()
    filename = QtGui.QFileDialog.getOpenFileName()
    result = np.load(filename)
    win = AirGapResult(result)
    win.show()
    app.exec()

if __name__ == '__main__':
    import sys
    sys.exit(int(main() or 0))