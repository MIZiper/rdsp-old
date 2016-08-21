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
        self.config = {}

    def fillTracks(self, tracks):
        for track in tracks:
            t = TrackModule(track['guid'], track['name'], self)
            t.parseConfig(track['config'])
            self.tracks.append(t)

    def fillProcess(self, process):
        for prc in process:
            moduleClass = gl.moduleManager.getModule(prc['type'])
            p = moduleClass(prc['guid'], prc['name'], self)
            p.parseConfig(prc['config'])
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

    def parseConfig(self, config):
        self.config = config

    def configWindow(self):
        pass
    
    def getFileConfig(self):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'config':self.config,
            'tracks':[
                track.getFileConfig() for track in self.tracks
            ],
            'process':[
                process.getFileConfig() for process in self.process
            ]
        }
        
        return cfg

# interface part over, event part start

    def delete(self):
        gl.projectManager.delSignal(self)
        # clean the tracks & process
        for prc in self.process:
            prc.delete()
        for track in self.tracks:
            track.delete()

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
        self.config = {}

    def loadData(self):
        pass

# custom part over, interface part start

    def parseConfig(self, config):
        self.config = config

    def getListConfig(self):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self
        }
        return cfg

    def getFileConfig(self):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'config':self.config
        }
        return cfg

    def delete(self):
        import os
        os.remove(os.path.join(gl.projectPath,gl.SOURCEDIR,self.guid+gl.TRACKEXT))

# interface part over, event part start

    def displayOverride(self):
        pass

    def displayNew(self):
        pass

    def displayOverlap(self):
        pass