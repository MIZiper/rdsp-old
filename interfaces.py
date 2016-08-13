class ModuleBase:
    # TODO: display config window, called by context
    def ConfigWin():
        raise NotImplementedError()

    def ListPackage():
        raise NotImplementedError()

    def Config():
        pass

    def PropertyWin():
        pass

class ListBase():
    def SetName():
        pass

    def MapContext():
        pass

    def AddSubList():
        pass

class ConfigBase():
    def ParseConfig():
        pass

    def GenConfig():
        pass