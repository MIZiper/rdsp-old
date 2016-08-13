from guidata.dataset.datatypes import DataSet
from guidata.dataset.dataitems import (ChoiceItem, IntItem, ButtonItem,
                FloatItem)


class AirGapParam(DataSet):
    numberDirection = ChoiceItem("Numbering Direction",
        (("cw","Clockwise"),("ccw","Counter-Clockwise")),
        default="ccw")
    rotation = ChoiceItem("Rotation",
        (("cw","Clockwise"),("ccw","Counter-Clockwise")),
        )
    numberOfPoles = IntItem("Number of Poles", default=48)
    keyphasorTrack = ButtonItem("Track for KeyPhasor", None)

class AirGapModule():
    ModuleName = "AirGap"
    ContextMenu = [
        {'title':'Process', 'action':'processNow'},
        {'title':'Config', 'action':'setConfig'},
        {'title':'Show Result', 'action':'showResult'}, # showFigure/showTable/exportData
        {'title':'Delete', 'action':'deleteProcess'}
    ]
    def __init__(self):
        self.ModuleObjectName = "the specified name for treatment"
    
    def configWindow():
        pass

    def listPackage():
        pass

    def propertyWindow():
        pass

    def parseConfig():
        pass

    def genConfig():
        pass

    def processNow(self):
        pass

    def processNow(self):
        pass

    def setConfig(self):
        pass

    def showResult(self):
        pass

    def deleteProcess(self):
        pass