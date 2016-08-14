"""
    Read/Parse/Save Proj file
"""
class ProjectManager():
    def __init__(self):
        self.signals = []
        self.listWidget = []

    def registerListWidget(self, listWidget):
        self.listWidget.append(listWidget)

    def addNewMat(self, guid, name, matpath):
        from default import SignalModule
        from scipy.io import loadmat
        import uuid

        mat = loadmat(matpath)
        i = 1
        tracks = []

        while ('Track%d' % i) in mat.keys():
            tracks.append({
                'guid':str(uuid.uuid4()),
                'name':mat['Track%d_Name' % i][0]
            })
            i += 1

        signal = SignalModule(guid, name, self)
        signal.fillProperties({
            'date':mat['RecordDate'][0],
            'length':mat['RecordLength'][0,0]
        })
        signal.fillTracks(tracks)
        
        for lw in self.listWidget:
            lw.addNewSignal(signal)

"""
    Search modules and register
"""
class ModuleManager():
    # TODO: new process type from signal file context menu
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
        return [name for name in self.modulesName]# if name!='SignalFile' and name!='Track']