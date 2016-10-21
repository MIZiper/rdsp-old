# from rdsp.util import ModuleManager, ProjectManager, PlotManager, ProgressManager

# moduleManager = ModuleManager()
# projectManager = ProjectManager()
# plotManager = PlotManager()
# progress = ProgressManager()

moduleManager = None
projectManager = None
plotManager = None
progress = None

projectPath = ''
projectConfig = 'project.json'

TRACKEXT = '.npy'
SOURCEDIR = 'source/'
RESULTDIR = 'result/'

from enum import IntEnum
class ModuleType(IntEnum):
    none = 0
    config = 1  # the module has config, shows in listWidget
    process = 2 # the module is for processing, in process for signal
    all = 3