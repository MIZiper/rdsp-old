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