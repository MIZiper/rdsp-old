"""
    default/embeded module for common use
"""

class SignalModule():
    ModuleName = 'Signal'
    ContextMenu = [
        {'title':'New Process', 'action':'newProcess'},
        # {'title':'ProcessAll', 'action':'processAll'},
        {'title':'Delete', 'action':'delete'}
    ]

    def __init__(self):
        self.guid = guid
        self.name = name
        self.tracks = []
        self.process = []

    def fillTracks(self):
        pass

    def loadTracks(self, trackData):
        pass

    def loadProcess(self, processData):
        pass
    
    def configWin(self):
        from guidata.qt.QtGui import QInputDialog
        a, ok = QInputDialog.getInteger(None,"G","H")
        return ok
    
    def delete(self, l):
        pass

    def newProcess(self, l):
        modulesName = l.moduleManager.getModulesName()
        from guidata.qt.QtGui import QInputDialog
        item, ok = QInputDialog.getItem(l,'Select a Module','Module:',modulesName,editable=False)
        if ok and item:
            moduleClass = l.moduleManager.getModule(item)
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

    def __init__(self):
        pass

    def displayOverride(self):
        pass

    def displayNew(self):
        pass

    def displayOverlap(self):
        pass