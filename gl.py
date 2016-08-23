from util import ModuleManager, ProjectManager, PlotManager, ProgressManager

moduleManager = ModuleManager()
projectManager = ProjectManager()
plotManager = PlotManager()
progress = ProgressManager()

projectPath = ''
projectConfig = 'project.json'

TRACKEXT = '.npy'
SOURCEDIR = 'source/'
RESULTDIR = 'result/'