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

    def configWin(self):
        from guidata.qt.QtGui import QInputDialog
        a, ok = QInputDialog.getInteger(None,"G","H")
        return ok
    
    def getConfig(self):
        return {
            'type':'Signal',
            'name':self.name,
            'object':self,
            'tracks':[],
            'process':[]
        }

# interface part over, event part start

    def delete(self):
        pass

    def newProcess(self):
        modulesName = gl.moduleManager.getModulesName()
        from guidata.qt.QtGui import QInputDialog
        item, ok = QInputDialog.getItem(None,'Select a Module','Module:',modulesName,editable=False)
        if ok and item:
            moduleClass = gl.moduleManager.getModule(item)
            o = moduleClass()
            if o.configWin():
                pass # store this object to list

        # a dialog list
        # if yes

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

    def getConfig(self):
        return {
            'type':'Track',
            'name':self.name,
            'object':self
        }

# interface part over, event part start

    def displayOverride(self):
        pass

    def displayNew(self):
        pass

    def displayOverlap(self):
        pass