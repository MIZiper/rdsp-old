from rdsp.default import SignalModule
from rdsp import gl
from scipy.io import loadmat
import uuid, numpy
from os import path
from guiqwt.plot import CurveWidget
from PyQt4.QtGui import QProgressDialog
from PyQt4.QtCore import QCoreApplication
from PyQt4 import QtGui
from PyQt4.QtCore import Qt

"""
    Read/Parse/Save Proj file
"""
class ProjectManager():
    def __init__(self, parent=None):
        self.signals = []
        self.listWidget = []
        self.parent = parent

    def registerListWidget(self, listWidget):
        self.listWidget.append(listWidget)

    def addNewMat(self, matpath):
        mat = loadmat(matpath)
        i = 1
        tracks = []

        while ('Track%d' % i) in mat:
            i += 1
        j = i
        gl.progress.startNewProgress(j-1,'Parsing tracks.')
        for i in range(1,j):
            guid = str(uuid.uuid4())
            numpy.save(path.join(gl.projectPath,gl.SOURCEDIR,guid+gl.TRACKEXT), mat['Track%d' % i])
            tracks.append({
                'guid':guid,
                'name':mat['Track%d_Name' % i][0],
                'config':{
                    'bandwidth':int(mat['Track%d_TrueBandWidth' % i][0,0]),
                    'c1':float(mat['Track%d_Sensitivity' % i][0,0]),
                    'c0':float(mat['Track%d_Offset' % i][0,0]),
                    'x-unit':mat['Track%d_X_Magnitude' % i][0],
                    'y-unit':mat['Track%d_Y_Magnitude' % i][0]
                    # Track%d_Coupling: DC/AC
                    # Track%d_Format: 32 bit floating point
                    # Track%d_Range_Peak
                    # Track%d_Sensor
                }
            })
            gl.progress.setValue(i)
        gl.progress.endProgress()

        guid = str(uuid.uuid4())
        name = path.basename(matpath)
        signal = SignalModule(guid, name, self)
        signal.parseConfig({
            'date':mat['RecordDate'][0],
            'length':float(mat['RecordLength'][0,0])
        })
        signal.fillTracks(tracks)
        self.signals.append(signal)
        
        for lw in self.listWidget:
            lw.addNewSignal(signal)

    # Since we're going to add various data type, count internal type in!
    def addNewSignal(self, intSig):
        # {'name',config:{'#date','#length'},'#guid',
        #  'tracks':[{'name','?guid','data','config':{'bandwidth','???'}}
        n = len(intSig['tracks'])
        gl.progress.startNewProgress(n,'Saving tracks.')
        tracks = []
        i = 0
        for track in intSig['tracks']:
            guid = str(uuid.uuid4())
            track['guid'] = guid
            numpy.save(path.join(gl.projectPath,gl.SOURCEDIR,guid+gl.TRACKEXT), track['data'])
            i += 1
            gl.progress.setValue(i)
        gl.progress.endProgress()

        guid = str(uuid.uuid4())
        signal = SignalModule(guid, intSig['name'], self)
        signal.parseConfig(intSig['config'])
        signal.fillTracks(intSig['tracks'])
        self.signals.append(signal)

        for lw in self.listWidget:
            lw.addNewSignal(signal)

    def delSignal(self, signal):
        # prompt confirm
        # force save project, since file won't exist
        self.signals.remove(signal)
        self.refreshListWidget()

    def initConfig(self, data):
        self.signals.clear()

        for dt in data:
            signal = SignalModule(dt['guid'],dt['name'],self)
            signal.fillTracks(dt['tracks'])
            signal.fillProcess(dt['process'])
            signal.parseConfig(dt['config'])
            self.signals.append(signal)
            
        self.refreshListWidget()

    def refreshListWidget(self):
        for lw in self.listWidget:
            lw.clear()
            for signal in self.signals:
                lw.addNewSignal(signal)

    def getConfig(self):
        return [ signal.getFileConfig() for signal in self.signals]

"""
    Search modules and register
"""
class ModuleManager():
    def __init__(self):
        # search modules in module/
        # the parameter should be a path, so to import 3rd-party modules
        self.modules = {}
        self.modulesName = []

    def registerModule(self, moduleClass):
        self.modules[moduleClass.ModuleName] = moduleClass
        if (moduleClass.ModuleType & gl.ModuleType.process):
            self.modulesName.append(moduleClass.ModuleName)

    def getModule(self, moduleClassName):
        try:
            return self.modules[moduleClassName]
        except:
            return None
    
    def getModulesName(self):
        return self.modulesName

"""
    Handle plot area, including graphs and tables
"""
class PlotManager():
    def __init__(self, plotTab=None):
        self.plotTab = plotTab
        if plotTab!=None:
            self.requestNewCurve('Display')

    def requestNewCurve(self, tabName):
        cw = CurveWidget()
        cw.register_all_curve_tools()
        self.plotTab.addTab(cw, tabName)
        self.plotTab.setCurrentIndex(self.plotTab.count()-1)
        return cw

    def requestCurrentCurve(self):
        c = self.plotTab.currentWidget()
        if type(c)==CurveWidget:
            return c
        return None

    def addNewWidget(self, tabName, widget):
        self.plotTab.addTab(widget, tabName)
        self.plotTab.setCurrentIndex(self.plotTab.count()-1)

    def clean(self, widget):
        if type(widget)==CurveWidget:
            plot = widget.plot
            plot.del_all_items()

class ProgressManager():
    def __init__(self, parent=None):
        if parent:
            self.progress = QProgressDialog()
            self.progress.setWindowTitle("Progress")
            self.progress.setCancelButton(None)

    def startNewProgress(self, count, text):
        self.progress.setMaximum(count)
        self.progress.setLabelText(text)
        self.progress.setValue(0)
        self.progress.show()
        QCoreApplication.processEvents()

    def setValue(self, value):
        self.progress.setValue(value)

    def endProgress(self):
        self.progress.accept()

class DisplayRangePicker(QtGui.QDialog):
    def __init__(self, maxFreq = None, maxTime = None):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle('Range Picker')
        self.maxFreq = maxFreq
        self.maxTime = maxTime
        self.useAll = False
        self.initUI()

    def initUI(self):
        layout = QtGui.QVBoxLayout(self)

        buttonBox = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok |
            QtGui.QDialogButtonBox.Cancel
        )
        btnUseAll = buttonBox.addButton('All',QtGui.QDialogButtonBox.ResetRole)
        btnUseAll.clicked.connect(self.useAllHandler)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        if self.maxTime:
            grpTime = QtGui.QGroupBox('Time')
            upperTime = QtGui.QSlider(Qt.Horizontal)
            upperTime.setMaximum(self.maxTime)
            upperTime.setValue(self.maxTime)
            lblUpperTime = QtGui.QLabel('%d' % self.maxTime)
            lowerTime = QtGui.QSlider(Qt.Horizontal)
            lowerTime.setMaximum(self.maxTime)
            lowerTime.setValue(0)
            lblLowerTime = QtGui.QLabel('%d' % 0)
            upperTime.valueChanged.connect(lambda x: lblUpperTime.setText('%d' % x))
            lowerTime.valueChanged.connect(lambda x: lblLowerTime.setText('%d' % x))
            grpTimeLayout = QtGui.QGridLayout(grpTime)
            grpTimeLayout.addWidget(lowerTime,0,0)
            grpTimeLayout.addWidget(upperTime,1,0)
            grpTimeLayout.addWidget(lblLowerTime,0,1)
            grpTimeLayout.addWidget(lblUpperTime,1,1)
            layout.addWidget(grpTime)

            self.upperTime = upperTime
            self.lowerTime = lowerTime

        if self.maxFreq:
            grpFreq = QtGui.QGroupBox('Frequency')
            upperFreq = QtGui.QSlider(Qt.Horizontal)
            upperFreq.setMaximum(self.maxFreq)
            upperFreq.setValue(self.maxFreq)
            lblUpperFreq = QtGui.QLabel('%d' % self.maxFreq)
            lowerFreq = QtGui.QSlider(Qt.Horizontal)
            lowerFreq.setMaximum(self.maxFreq)
            lowerFreq.setValue(0)
            lblLowerFreq = QtGui.QLabel('%d' % 0)
            upperFreq.valueChanged.connect(lambda x: lblUpperFreq.setText('%d' % x))
            lowerFreq.valueChanged.connect(lambda x: lblLowerFreq.setText('%d' % x))
            grpFreqLayout = QtGui.QGridLayout(grpFreq)
            grpFreqLayout.addWidget(lowerFreq,0,0)
            grpFreqLayout.addWidget(upperFreq,1,0)
            grpFreqLayout.addWidget(lblLowerFreq,0,1)
            grpFreqLayout.addWidget(lblUpperFreq,1,1)
            layout.addWidget(grpFreq)
            
            self.upperFreq = upperFreq
            self.lowerFreq = lowerFreq

        layout.addWidget(buttonBox)

    def useAllHandler(self):
        self.useAll = True
        self.accept()

    def getResult(self):
        result = {}
        if self.maxFreq:
            lowerFreq = self.lowerFreq.value()
            upperFreq = self.upperFreq.value()
            freq = (lowerFreq, upperFreq) if upperFreq>=lowerFreq else (upperFreq, lowerFreq)
            result['freq'] = None if self.useAll else freq
        if self.maxTime:
            lowerTime = self.lowerTime.value()
            upperTime = self.upperTime.value()
            time = (lowerTime, upperTime) if upperTime>=lowerTime else (upperTime, lowerTime) 
            result['time'] = None if self.useAll else time

        return result