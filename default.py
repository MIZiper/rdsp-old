"""
    default/embeded module for common use
"""

import gl, uuid

class SignalModule():
    ModuleName = 'Signal'
    ContextMenu = [
        {'title':'New Process', 'action':'newProcess'},
        # {'title':'ProcessAll', 'action':'processAll'},
        {'title':'Delete', 'action':'delete'}
    ]

    def __init__(self, guid, name, parent):
        self.guid = guid
        self.name = name
        self.parent = parent
        self.tracks = []
        self.process = []

    def fillProperties(self, propDict):
        pass

    def fillTracks(self, tracks):
        for track in tracks:
            t = TrackModule(track['guid'], track['name'], self)
            self.tracks.append(t)

    def fillProcess(self, process):
        for prc in process:
            moduleClass = gl.moduleManager.getModule(prc['type'])
            p = moduleClass(prc['guid'], prc['name'], self)
            p.parseConfig(prc)
            self.process.append(p)

    def loadTracks(self, trackData):
        pass

    def loadProcess(self, processData):
        pass
    
    def getTracksList(self):
        return [{'name':track.name,'guid':track.guid} for track in self.tracks]

    def getTrack(self, guid):
        for track in self.tracks:
            if track.guid == guid:
                return track
        return None
    
    def refresh(self):
        gl.projectManager.refreshListWidget()
    
# custom part over, interface part start

    def configWindow(self):
        pass
    
    def getConfig(self, forList=True):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self,
            'tracks':[
                track.getConfig(forList) for track in self.tracks
            ],
            'process':[
                process.getConfig(forList) for process in self.process
            ]
        }
        if not forList:
            del cfg['object']
        return cfg

# interface part over, event part start

    def delete(self):
        gl.projectManager.delSignal(self)
        # clean the tracks & process
        # delete process' result file meanwhile

    def newProcess(self):
        modulesName = gl.moduleManager.getModulesName()
        from guidata.qt.QtGui import QInputDialog
        item, ok = QInputDialog.getItem(None,'Select a Module','Module:',modulesName,editable=False)
        if ok and item:
            moduleClass = gl.moduleManager.getModule(item)
            guid = str(uuid.uuid4())
            o = moduleClass(guid, item, self)
            if o.configWindow():
                self.process.append(o)
                gl.projectManager.refreshListWidget()

class TrackModule():
    ModuleName = 'Track'
    ContextMenu = [
        {'title':'Display', 'action':'displayOverride'},
        {'title':'Display in New Window', 'action':'displayNew'},
        {'title':'Add to Display', 'action':'displayOverlap'}
        # ,{'title':'Detailed Display', 'action':'detailedDisplay'}
    ]

    def __init__(self, guid, name, parent):
        self.guid = guid
        self.name = name
        self.parent = parent
        self.data = None

    def fillProperties(self, propDict):
        pass

    def loadData(self):
        pass

# custom part over, interface part start

    def getConfig(self, forList=True):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self
        }
        if not forList:
            del cfg['object']
        return cfg

# interface part over, event part start

    def displayOverride(self):
        pass

    def displayNew(self):
        pass

    def displayOverlap(self):
        pass