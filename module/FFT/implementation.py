import numpy as np
from os import path
import os
from rdsp import gl
from PyQt4 import QtGui

class FFTModule(object):
    ModuleName = 'FFT'
    ContextMenu = [
        {'title':'Process', 'action':'processNow'},
        {'title':'Config', 'action':'setConfig'},
        {'title':'Delete', 'action':'delete'}
    ]
    def __init__(self, guid, name, parent, processed=False):
        self.name = name
        self.guid = guid
        self.parent = parent
        self.tracks = []
        self.freqs = []
        self.config = {
            'lines':1000,
            'overlap':0.7
        }
        self.result = None
        self.resultLoaded = False
        self.processed = processed

    def getResult(self):
        if not self.resultLoaded:
            self.result = np.load(path.join(gl.projectPath,gl.RESULTDIR,self.guid+gl.TRACKEXT))[0]
            self.resultLoaded = True

        return self.result

    def getFreqData(self, guid):
        if self.processed:
            result = self.getResult()
            return result[guid]
        return {}

    def configWindow(self, config=None):
        if not config:
            config = {
                'name': self.name,
                'lines':1000,
                'overlap':0.7,
                'trackSrc':self.parent.getTracksList(),
                'tracks':[]
            }

        cfgWin = FFTConfig(config)
        cfgWin.exec()
        if cfgWin.result():
            self.parseConfig(cfgWin.getResult())
            return True
        return False

    def getProperty(self):
        return {
            'Lines':self.config['lines'],
            'Overlap':self.config['overlap']
        }

    def parseConfig(self, config):
        if 'name' in config:
            self.name = config['name']
        self.config = {
            'lines':config['lines'],
            'overlap':config['overlap']
        }
        self.tracks = [
            self.parent.getTrack(guid) for guid in config['tracks']
        ]
        if 'freqs' in config:
            self.freqs = [
                FFTFreqModule(guid, self.parent.getTrack(guid).name, self) for guid in config['freqs']
            ]

    def getListConfig(self):
        config = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self,
            'sub':[freq.getListConfig() for freq in self.freqs]
            # freqs not saved and the info are stored in npy, so need to save to file?
        }
        return config

    def getFileConfig(self):
        config = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'processed':self.processed,
            'config':{
                'tracks':[track.guid for track in self.tracks],
                'lines':self.config['lines'],
                'overlap':self.config['overlap'],
                'freqs':[freq.guid for freq in self.freqs]
            }
        }
        return config

    def setConfig(self):
        # cfg = self.config
        cfg = self.getFileConfig()['config']
        cfg['name'] = self.name
        cfg['trackSrc'] = self.parent.getTracksList()
        if self.configWindow(cfg):
            # self.parent.refresh()
            pass

    def delete(self):
        self.parent.delProcess(self)
        if self.processed:
            os.remove(path.join(gl.projectPath,gl.RESULTDIR,self.guid+gl.TRACKEXT))

    def processNow(self):
        cfg = self.config

        Nw = cfg['lines'] * 2.56
        win = np.hanning(Nw)
        ols = np.int(Nw*(1-cfg['overlap'])) # OverLapStep

        result = {}
        self.freqs.clear()
        for track in self.tracks:
            track_data = track.getData()[0]
            r = {
                'bandwidth':track.config['bandwidth'],
                'data':None
                # 'Nw'
            }
            N = track_data.size
            olt = np.floor((N-Nw)/ols)+1 # OverLapTimes
            stride = track_data.strides[0]
            
            mat = np.lib.stride_tricks.as_strided(track_data, shape=(olt,Nw), strides=(stride*ols,stride))
            mat_mean = mat.mean(axis=1).reshape(olt,1)
            mat_dcLess = mat - mat_mean
            mat_dcLess *= win
            
            mat_result = np.fft.fft(mat_dcLess)
            mat_result_half = mat_result[:,:Nw/2]

            # mat_amp = 2*2*np.abs(mat_result_half)/Nw # restore from window and fft
            # mat_agl = np.angle(mat_result_half, deg=True)
            r['data'] = 2*mat_result_half/Nw*2 # since the complex contain amp/agl info
            result[track.guid] = r
            
            f = FFTFreqModule(track.guid, track.name, self)
            self.freqs.append(f)

        np.save(path.join(gl.projectPath,gl.RESULTDIR,self.guid+gl.TRACKEXT),[result])
        self.result = result

        self.processed = True
        self.resultLoaded = True
        self.parent.refresh()

class FFTConfig(QtGui.QDialog):
    def __init__(self, config):
        QtGui.QDialog.__init__(self)
        self.config = config
        self.setWindowTitle('FFT Configuration')
        self.initUi()

    def initUi(self):
        config = self.config
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # number of lines

        # window

        # overlap

        layoutMain = QtGui.QVBoxLayout()
        layoutMain.addWidget(buttonBox)
        self.setLayout(layoutMain)

    def getResult(self):
        return {
            'name':'FFT',
            'lines':50000,
            'overlap':0.7,
            'tracks':[self.config['trackSrc'][0]['guid']]
        }

class FFTFreqModule(object):
    ModuleName = 'FFTFreq'
    ContextMenu = [
        {'title':'Show Result', 'action':'showResult'}, #FirstPhase,Average
        {'title':'Export', 'action':'export2xlsx'}, #TBDetermined
        {'title':'Show STFT', 'action':'showStft'}
    ]
    def __init__(self, guid, name, parent):
        self.name = name
        self.guid = guid
        self.parent = parent
        self.data = None
        self.config = {}
        self.dataLoaded = False

    def getData(self):
        if not self.dataLoaded:
            self.data = self.parent.getFreqData(self.guid)
            self.dataLoaded = True
        return self.data

    def getListConfig(self):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self,
            'sub':[
                self.parent.parent.getTrack(self.guid).getListConfig()
            ]
        }
        return cfg

    def getFileConfig(self):
        pass

    def parseConfig(self, config):
        pass

    def getProperty(self):
        return {}

    def export2xlsx(self):
        pass

    def showResult(self):
        data = self.getData()
        widget = FFTFreqWidget(data)
        gl.plotManager.addNewWidget(self.name,widget)

    def showStft(self):
        data = self.getData()
        widget = FFTStftWidget(data)
        gl.plotManager.addNewWidget(self.name,widget)

class FFTFreqWidget(QtGui.QWidget):
    def __init__(self, result):
        QtGui.QWidget.__init__(self)

class FFTStftWidget(QtGui.QWidget):
    def __init__(self, result):
        QtGui.QWidget.__init__(self)

# to make test easy (show context menu of FFTFreqModule), add the following code, but needs to be removed
# modify ModuleManager not to show every module registered
# or simply use object's property instead of class's
gl.moduleManager.registerModule(FFTFreqModule)

if __name__ == '__main__':
    from guidata import qapplication
    app = qapplication()
    dialog = FFTConfig({})
    dialog.exec()
    print(dialog.result())