from guidata.qt import QtGui

class AirGapModule():
    ModuleName = "AirGap"
    ContextMenu = [
        {'title':'Process', 'action':'processNow'},
        {'title':'Config', 'action':'setConfig'},
        {'title':'Show Result', 'action':'showResult'}, # showFigure/showTable/exportData
        {'title':'Delete', 'action':'deleteProcess'}
    ]
    def __init__(self, parent=None):
        self.name = ''
        self.guid = ''
        self.parent = parent
        self.tracks = []
    
    def configWindow(self, config={}):
        config['trackSrc'] = self.parent.getTracksList()
        config['name'] = 'AirGap'
        cfgWin = AirGapConfig(config)
        cfgWin.exec_()
        if cfgWin.result():
            self.parseConfig(cfgWin.getResult())
            return True
        return False

    def listPackage(self):
        pass

    def propertyWindow(self):
        pass

    def parseConfig(self, config):
        self.name = config['name']

    def getConfig(self, WithObject=True):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self,
            'sub':[] # self.parent.getTracks().getConfig()
        }
        if not WithObject:
            del cfg['object']
        return cfg

# interface part over, event part start

    def processNow(self):
        pass

    def setConfig(self):
        pass

    def showResult(self):
        pass

    def deleteProcess(self):
        pass

class AirGapConfig(QtGui.QDialog):
    def __init__(self, config, parent=None):
        '''
        config = {name,trackSrc:[{name,guid}],trackSet}
        '''
        QtGui.QDialog.__init__(self)
        self.config = config
        self.setWindowTitle('AirGap Configuration')
        self.initUi()

    def initUi(self):
        config = self.config
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        lblName = QtGui.QLabel("Name")
        txtName = QtGui.QLineEdit(config['name'])

        grpRotation = QtGui.QGroupBox('Generator Rotation')
        rdoRotCw = QtGui.QRadioButton('Clockwise')
        rdoRotCcw = QtGui.QRadioButton('Counter-Clockwise')
        rdoRotCw.setChecked(True)
        rotLayout = QtGui.QHBoxLayout(grpRotation)
        rotLayout.addWidget(rdoRotCw)
        rotLayout.addWidget(rdoRotCcw)

        grpNumbering = QtGui.QGroupBox('Numbering Direction')
        rdoNumCw = QtGui.QRadioButton('Clockwise')
        rdoNumCcw = QtGui.QRadioButton('Counter-Clockwise')
        rdoNumCcw.setChecked(True)
        numLayout = QtGui.QHBoxLayout(grpNumbering)
        numLayout.addWidget(rdoNumCw)
        numLayout.addWidget(rdoNumCcw)

        lblCount = QtGui.QLabel('Number of Poles')
        txtCount = QtGui.QSpinBox()
        txtCount.setRange(0, 100)
        txtCount.setSingleStep(1)
        txtCount.setValue(48)

        lblKpTrack = QtGui.QLabel('KeyPhasor Track')
        cmbTracks = QtGui.QComboBox()
        tracks = [track['name'] for track in self.config['trackSrc']]
        cmbTracks.addItems(tracks)

        btnTrack = QtGui.QCommandLinkButton('Add Track')
        btnTrack.clicked.connect(self.addTrack)

        sideLayout = QtGui.QVBoxLayout()
        sideLayout.addWidget(lblName)
        sideLayout.addWidget(txtName)
        sideLayout.addWidget(grpRotation)
        sideLayout.addWidget(grpNumbering)
        sideLayout.addWidget(lblCount)
        sideLayout.addWidget(txtCount)
        sideLayout.addWidget(lblKpTrack)
        sideLayout.addWidget(cmbTracks)
        sideLayout.addWidget(btnTrack)
        sideLayout.addStretch(1)

        tracksTable = QtGui.QTableWidget(0,3)
        tracksTable.setHorizontalHeaderLabels(['Track Name','Thickness','Angel'])        
        tracksTable.verticalHeader().sectionDoubleClicked.connect(self.removeTrack)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addLayout(sideLayout)
        mainLayout.addWidget(tracksTable, stretch=1)
        layoutMain = QtGui.QVBoxLayout()
        layoutMain.addLayout(mainLayout)
        layoutMain.addWidget(buttonBox)
        self.setLayout(layoutMain)

        self.tracks_table = tracksTable
        self.name_txt = txtName

    def addTrack(self):
        tt = self.tracks_table
        n = tt.rowCount()
        tt.setRowCount(n+1)

        cmbTracks = QtGui.QComboBox()
        tracks = [track['name'] for track in self.config['trackSrc']]
        cmbTracks.addItems(tracks)

        tt.setCellWidget(n,0,cmbTracks)

    def removeTrack(self, index):
        self.tracks_table.removeRow(index)

    def getResult(self):
        return {'name':self.name_txt.text()}

if __name__ == '__main__':
    import guidata
    app = guidata.qapplication()
    dialog = AirGapConfig({'name':'AirGap','trackSrc':[]})
    dialog.exec_()
    print(dialog.result())