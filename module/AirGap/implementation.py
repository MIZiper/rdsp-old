from PyQt4 import QtGui
import numpy as np
from os import path
import os, xlsxwriter

from rdsp.module.AirGap.algorithm import findContinuous, getAprxValue, findSEIndex
from rdsp.module.AirGap.resultWidget import AirGapResult
from rdsp import gl

class AirGapModule():
    ModuleName = "AirGap"
    ModuleType = gl.ModuleType.all
    ContextMenu = [
        {'title':'Process', 'action':'processNow'},
        {'title':'Config', 'action':'setConfig'},
        {'title':'Show Result', 'action':'showResult'}, # showFigure/showTable/exportData
        {'title':'Export', 'action':'export2xlsx'},
        {'title':'Delete', 'action':'delete'}
    ]
    def __init__(self, guid, name, parent, processed=False):
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
        self.result = None
        self.resultLoaded = False
        self.processed = processed

    def getResult(self):
        if not self.resultLoaded:
            self.result = np.load(path.join(gl.projectPath,gl.RESULTDIR,self.guid+gl.TRACKEXT))
            self.resultLoaded = True

        return self.result
    
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

    def getProperty(self):
        return {
            "Number of Poles":self.config['numOfPoles']
        }

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
                'angle':track['angle'],
                'pole':track['pole']
            } for track in config['trackSet']
        ]

    def getFileConfig(self):
        config = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'config':{},
            'processed':self.processed
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
                'angle':track['angle'],
                'pole':track['pole']
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
        kp_data = self.keyPhasor.getData()[0,:]
        kp_data_bool = kp_data<((kp_data.max()+kp_data.min())/2)
        kp_se_pairs = findContinuous(kp_data_bool,0)
        tolerance = 0.01
        poles = self.config['numOfPoles']
        rotCw = self.config['rot-cw']
        numCw = self.config['num-cw']

        result = []
        c = len(self.tracks)
        k = 0
        gl.progress.startNewProgress(c,'Processing.')
        for trackSet in self.tracks:
            track_data = trackSet['object'].getData()[0,:]
            track_data_bool = track_data<((track_data.max()+track_data.min())/2)
            track_se_pairs = findContinuous(track_data_bool,0)
            se_idx = findSEIndex(kp_se_pairs, track_se_pairs)
            t_pole = trackSet['pole']
            t_thick = trackSet['thickness']
            t_freq = trackSet['object'].config['bandwidth']*2.56
            l = se_idx.size
            r = {
                'speed':np.zeros(l-1),
                'name':trackSet['object'].name,
                'angle':trackSet['angle'],
                'data':np.zeros((poles,l-1))
            }
            dat = r['data']
            spd = r['speed']
            for i in range(1,l):
                track_se_segment = track_se_pairs[se_idx[i-1]:se_idx[i],:]
                (ll,ww) = track_se_segment.shape
                # assert ll==numOfPoles
                for j in range(ll):
                    (v,c) = getAprxValue(track_data,track_se_segment[j,:],tolerance)
                    n = t_pole+j*(-1+numCw*2)*(1-2*rotCw)
                    if n<=0:
                        n += poles
                    else:
                        if n>poles:
                            n -= poles
                    dat[j,i-1] = v+t_thick
                spd[i-1] = 60*t_freq/(
                    track_se_pairs[se_idx[i],0] - track_se_pairs[se_idx[i-1],0]
                )
            result.append(r)
            k += 1
            gl.progress.setValue(k)
        np.save(path.join(gl.projectPath,gl.RESULTDIR,self.guid+gl.TRACKEXT),result)
        gl.progress.endProgress()
        self.result = np.array(result)

        self.processed = True
        self.resultLoaded = True

    def setConfig(self):
        config = self.getFileConfig()
        cfg = config['config']
        cfg['name'] = self.name
        cfg['trackSrc'] = self.parent.getTracksList()
        if self.configWindow(cfg):
            self.parent.refresh()

    def showResult(self):
        if self.processed:
            result = self.getResult()
            widget = AirGapResult(result)
            gl.plotManager.addNewWidget(self.name,widget)

    def export2xlsx(self):
        if self.processed:
            filename = QtGui.QFileDialog.getSaveFileName(caption='Export to Excel', filter='Excel File (*.xlsx)')
            if not filename:
                return

            result = self.getResult()
            wb = xlsxwriter.Workbook(filename)
            num_format = wb.add_format({'num_format':'0.000'})
            for dt in result:
                ws = wb.add_worksheet(dt['name'])
                ws.write_row(0,1,dt['speed'],num_format)
                ws.write_string(0,0,'Speed (rpm)')
                row = 2
                for d in dt['data']:
                    ws.write(row,0,row-1)
                    ws.write_row(row,1,d,num_format)
                    row += 1

            wb.close()

    def delete(self):
        self.parent.delProcess(self)
        if self.processed:
            os.remove(path.join(gl.projectPath,gl.RESULTDIR,self.guid+gl.TRACKEXT))

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

        tracksTable = QtGui.QTableWidget(0,4)
        tracksTable.setHorizontalHeaderLabels(['Track Name','Thickness','Angle','Pole'])        
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
            itm = QtGui.QTableWidgetItem(str(trackCfg['angle']))
            tt.setItem(n,2,itm)
            itm = QtGui.QTableWidgetItem(str(trackCfg['pole']))
            tt.setItem(n,3,itm)

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
                'angle':float(tt.item(r,2).text()),
                'pole':int(tt.item(r,3).text())
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