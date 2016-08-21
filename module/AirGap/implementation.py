from guidata.qt import QtGui

class AirGapModule():
    ModuleName = "AirGap"
    ContextMenu = [
        {'title':'Process', 'action':'processNow'},
        {'title':'Config', 'action':'setConfig'},
        {'title':'Show Result', 'action':'showResult'}, # showFigure/showTable/exportData
        {'title':'Delete', 'action':'delete'}
    ]
    def __init__(self, guid, name, parent):
        self.name = name
        self.guid = guid
        self.parent = parent
        self.tracks = []
        self.keyPhasor = None
        self.config = {
            'rot-cw':True,
            'num-cw':False,
            'numOfPoles':48,
        }
    
    def configWindow(self, config=None):
        if not config:
            config = {
                'name':self.name,
                'rot-cw':True,
                'num-cw':False,
                'numOfPoles':48,
                'trackSrc':self.parent.getTracksList(),
                'keyPhasor':None,
                'trackSet':None
            }
            
        cfgWin = AirGapConfig(config)
        cfgWin.exec_()
        if cfgWin.result():
            self.parseConfig(cfgWin.getResult())
            return True
        return False

    def propertyWindow(self):
        pass

    def parseConfig(self, config):
        if 'name' in config:
            self.name = config['name']

        self.config = {
            'rot-cw':config['rot-cw'],
            'num-cw':config['num-cw'],
            'numOfPoles':config['numOfPoles']
        }
        self.keyPhasor = self.parent.getTrack(config['keyPhasor'])
        self.tracks = [
            {
                'object':self.parent.getTrack(track['guid']),
                'thickness':track['thickness'],
                'angel':track['angel']
            } for track in config['trackSet']
        ]

    def getFileConfig(self):
        config = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'config':{}
        }
        cfg = config['config']
        cfg['rot-cw'] = self.config['rot-cw']
        cfg['num-cw'] = self.config['num-cw']
        cfg['numOfPoles'] = self.config['numOfPoles']
        cfg['keyPhasor'] = self.keyPhasor.guid
        cfg['trackSet'] = [
            {
                'guid':track['object'].guid,
                'thickness':track['thickness'],
                'angel':track['angel']
            } for track in self.tracks
        ]

        return config

    def getListConfig(self):
        config = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self,
            'sub':[]
        }
        config['sub'] = [
            trackSet['object'].getListConfig() for trackSet in self.tracks
        ]
        kpCfg = self.keyPhasor.getListConfig()
        kpCfg['type'] = 'KeyPhasor'
        config['sub'].insert(0, kpCfg)

        return config

# interface part over, event part start

    def processNow(self):
        pass

    def setConfig(self):
        config = self.getFileConfig()
        cfg = config['config']
        cfg['name'] = self.name
        cfg['trackSrc'] = self.parent.getTracksList()
        if self.configWindow(cfg):
            self.parent.refresh()

    def showResult(self):
        pass

    def delete(self):
        pass

class AirGapConfig(QtGui.QDialog):
    def __init__(self, config):
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
        if config['rot-cw']:
            rdoRotCw.setChecked(True)
        else:
            rdoRotCcw.setChecked(True)
        rotLayout = QtGui.QHBoxLayout(grpRotation)
        rotLayout.addWidget(rdoRotCw)
        rotLayout.addWidget(rdoRotCcw)

        grpNumbering = QtGui.QGroupBox('Numbering Direction')
        rdoNumCw = QtGui.QRadioButton('Clockwise')
        rdoNumCcw = QtGui.QRadioButton('Counter-Clockwise')
        if config['num-cw']:
            rdoNumCw.setChecked(True)
        else:
            rdoNumCcw.setChecked(True)
        numLayout = QtGui.QHBoxLayout(grpNumbering)
        numLayout.addWidget(rdoNumCw)
        numLayout.addWidget(rdoNumCcw)

        lblCount = QtGui.QLabel('Number of Poles')
        txtCount = QtGui.QSpinBox()
        txtCount.setRange(0, 100)
        txtCount.setSingleStep(1)
        txtCount.setValue(config['numOfPoles'])

        lblKpTrack = QtGui.QLabel('KeyPhasor Track')
        cmbTracks = QtGui.QComboBox()
        tracks = [track['name'] for track in self.config['trackSrc']]
        cmbTracks.addItems(tracks)
        if config['keyPhasor']:
            for i in range(len(tracks)):
                if self.config['trackSrc'][i]['guid']==config['keyPhasor']:
                    cmbTracks.setCurrentIndex(i)
                    break

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
        self.tracks_table = tracksTable
        if config['trackSet']:
            for i in range(len(config['trackSet'])):
                self.addTrack(config['trackSet'][i])

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addLayout(sideLayout)
        mainLayout.addWidget(tracksTable, stretch=1)
        layoutMain = QtGui.QVBoxLayout()
        layoutMain.addLayout(mainLayout)
        layoutMain.addWidget(buttonBox)
        self.setLayout(layoutMain)

        self.name_txt = txtName
        self.rotCw_rdo = rdoRotCw
        self.numCw_rdo = rdoNumCw
        self.numOfPoles_txt = txtCount
        self.keyPhasor_cmb = cmbTracks

    def addTrack(self, trackCfg=None):
        tt = self.tracks_table
        n = tt.rowCount()
        tt.setRowCount(n+1)

        cmbTracks = QtGui.QComboBox()
        tracks = [track['name'] for track in self.config['trackSrc']]
        cmbTracks.addItems(tracks)

        tt.setCellWidget(n,0,cmbTracks)

        if trackCfg:
            for i in range(len(tracks)):
                if trackCfg['guid']==self.config['trackSrc'][i]['guid']:
                    cmbTracks.setCurrentIndex(i)
                    break
            itm = QtGui.QTableWidgetItem(str(trackCfg['thickness']))
            tt.setItem(n,1,itm)
            itm = QtGui.QTableWidgetItem(str(trackCfg['angel']))
            tt.setItem(n,2,itm)

    def removeTrack(self, index):
        self.tracks_table.removeRow(index)

    def getResult(self):
        tt = self.tracks_table
        trackSrc = self.config['trackSrc']
        trackSet = []
        for r in range(tt.rowCount()):
            trackSet.append({
                'guid':trackSrc[tt.cellWidget(r,0).currentIndex()]['guid'],
                'thickness':float(tt.item(r,1).text()),
                'angel':float(tt.item(r,2).text())
                # try catch parseFloat error required
            })

        return {
            'name':self.name_txt.text(),
            'rot-cw':self.rotCw_rdo.isChecked(),
            'num-cw':self.numCw_rdo.isChecked(),
            'numOfPoles':self.numOfPoles_txt.value(),
            'keyPhasor':trackSrc[self.keyPhasor_cmb.currentIndex()]['guid'],
            'trackSet':trackSet
        }

if __name__ == '__main__':
    import guidata
    app = guidata.qapplication()
    dialog = AirGapConfig({'name':'AirGap','trackSrc':[]})
    dialog.exec_()
    print(dialog.result())