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
        from default import SignalModule
        from scipy.io import loadmat
        import uuid, gl, numpy
        from os import path

        mat = loadmat(matpath)
        i = 1
        tracks = []

        while ('Track%d' % i) in mat:
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
            i += 1

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

    def delSignal(self, signal):
        # prompt confirm
        # force save project, since file won't exist
        self.signals.remove(signal)
        self.refreshListWidget()

    def initConfig(self, data):
        from default import SignalModule
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
        self.modulesName.append(moduleClass.ModuleName)

    def getModule(self, moduleClassName):
        try:
            return self.modules[moduleClassName]
        except:
            return None
    
    def getModuleIndex(self, moduleClassName):
        try:
            return self.modulesName.index(moduleClassName)+1000
        except:
            return -1

    def getModuleByIndex(self, index):
        moduleName = "default"
        try:
            moduleName = self.modulesName[index-1000]
        finally:
            return self.getModule(moduleName)
    
    def getModulesName(self):
        return [name for name in self.modulesName if name!='Signal' and name!='Track'] #]#