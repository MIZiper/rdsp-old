"""
    default/embeded module for common use
"""

import gl

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

    def loadTracks(self, trackData):
        pass

    def loadProcess(self, processData):
        pass
    
# custom part over, interface part start

    def configWindow(self):
        from guidata.qt.QtGui import QInputDialog
        a, ok = QInputDialog.getInteger(None,"G","H")
        return ok
    
    def getConfig(self, WithObject=True):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self,
            'tracks':[
                track.getConfig(WithObject) for track in self.tracks
            ],
            'process':[
                process.getConfig(WithObject) for process in self.process
            ]
        }
        if not WithObject:
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
            o = moduleClass()
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

# custom part over, interface part start

    def getConfig(self, WithObject=True):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self
        }
        if not WithObject:
            del cfg['object']
        return cfg

# interface part over, event part start

    def displayOverride(self):
        pass

    def displayNew(self):
        pass

    def displayOverlap(self):
        pass