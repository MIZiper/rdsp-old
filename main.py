from guidata.qt.QtGui import (QMainWindow, QHBoxLayout, QTabWidget, QTreeWidget,
    QVBoxLayout, QListWidget, QSplitter, QVBoxLayout, QWidget,
    QFileDialog ,QMessageBox, QTreeWidgetItem, QMenu,
    QGridLayout)
from guidata.qt.QtCore import QFile
from guidata.qthelpers import (create_action, add_actions)
from guidata.qthelpers import Qt

from os import path 
import uuid

from util import ModuleManager, ProjectManager

APPNAME = "RDSP"
PROJPATH = ''
SOURCEDIR = 'source/'
SETTING = 'project.json'

class ListWidgetBase(QTreeWidget):
    def __init__(self, parent, moduleManager):
        QTreeWidget.__init__(self, parent)
        self.moduleManager = moduleManager
        self.setHeaderLabels(("Type", "Name"))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

        self.data = {}

    def setData(self, data):
        self.clear()
        for i in data:
            if i['type'] == 'SignalFile':
                self.parseNode(self, i)

    def parseNode(self, parent, node):
        item = QTreeWidgetItem(parent)
        item.setText(0, node['type'])
        item.setText(1, node['name'])
        item.setData(0, 33, node['type']) # 33 user-role for module type
        item.setData(0, 34, node['object']) # 34 user-role for object
        if 'sub' in node.keys():
            for subNode in node['sub']:
                self.parseNode(item, subNode)
    
    def contextMenu(self, position):
        items = self.selectedItems()
        if len(items) > 0:
            moduleClassName = items[0].data(0, 33)
            boundObject = items[0].data(0, 34)
            moduleClass = self.moduleManager.getModule(moduleClassName)
            if moduleClass:
                menu = QMenu()
                import functools
                actions = (create_action(menu, action['title'], triggered=functools.partial(getattr(moduleClass,action['action']),boundObject,self)) for action in moduleClass.ContextMenu)
                add_actions(menu, actions)
                menu.exec_(self.viewport().mapToGlobal(position))

    def addNewSignal(self, signal):
        raise NotImplementedError

class ListProjectWidget(ListWidgetBase):
    def __init__(self, parent, moduleManager):
        ListWidgetBase.__init__(self, parent, moduleManager)

    def addNewSignal(self, signal):
        newData = {"type":"SignalFile", "name":fname, "object":None, "sub":[]}
        self.parseNode(self, newData)

class ListTrackWidget(ListWidgetBase):
    def __init__(self, parent, moduleManager):
        ListWidgetBase.__init__(self, parent, moduleManager)

    def addNewSignal(self, signal):
        # change the type so as to drop "new process", but a new module class required
        from util import extractMatFile
        signalTracks = extractMatFile(path.join(PROJPATH,SOURCEDIR,fname))
        newData = {"type":"SignalFile", "name":fname, "object":None, "sub":[
            {"type":"Track", "name":track['name'], "object":None} for track in signalTracks['tracks']
        ]}
        self.data[fname] = newData
        
        self.parseNode(self, newData)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.moduleManager = ModuleManager()
        self.projectManager = ProjectManager()

        self.initUi()
        self.loadModule()

    def initUi(self):
        self.setWindowTitle(APPNAME)
        self.statusBar().showMessage("Welcome!", 3000)

        file_menu = self.menuBar().addMenu("File")
        new_proj_action = create_action(self, "New Project", triggered=self.new_project)
        open_proj_action = create_action(self, "Open Project", triggered=self.open_project)
        save_proj_action = create_action(self, "Save Project", triggered=self.save_project)
        import_mat_action = create_action(self, "Import Mat", triggered=self.import_mat)
        quit_action = create_action(self, "Quit", triggered=self.quit)
        add_actions(file_menu, (new_proj_action, open_proj_action, save_proj_action,
                                None, import_mat_action, None, quit_action))
        
        help_menu = self.menuBar().addMenu("Help")
        about_action = create_action(self, "About", triggered=self.about)
        tetris_action = create_action(self, "Tetris", triggered=self.game_tetris)
        same_action = create_action(self, "Same", triggered=self.game_same)
        mine_action = create_action(self, "Mine", triggered=self.game_mine)
        add_actions(help_menu, (about_action, None, tetris_action, same_action, mine_action))

        main_widget = QWidget(self)
        main_layout = QGridLayout(main_widget)
        disp_widget = QTabWidget(main_widget)
        side_widget = QWidget(main_widget)
        #
        side_layout = QGridLayout(side_widget)
        tab_list_widget = QTabWidget(side_widget)
        self.proj_list = ListProjectWidget(tab_list_widget, self.moduleManager)
        self.track_list = ListTrackWidget(tab_list_widget, self.moduleManager)
        tab_list_widget.addTab(self.proj_list, 'Project')
        tab_list_widget.addTab(self.track_list, 'Track')
        side_layout.addWidget(tab_list_widget, 0, 0)
        prop_widget = QListWidget(side_widget)
        side_layout.addWidget(prop_widget, 1, 0)
        side_layout.setRowStretch(0, 2)
        side_layout.setRowStretch(1, 1)
        #
        disp_widget.setTabPosition(QTabWidget.South)
        plot = QListWidget(disp_widget)
        disp_widget.addTab(plot, 'plot')
        #
        main_layout.addWidget(side_widget, 0, 0)
        main_layout.addWidget(disp_widget, 0, 1)
        main_layout.setColumnStretch(1, 30)
        main_layout.setColumnStretch(0, 10)
        self.setCentralWidget(main_widget)

    def loadModule(self):
        from default import SignalFileModule, TrackModule
        self.moduleManager.registerModule(SignalFileModule)
        self.moduleManager.registerModule(TrackModule)
        

    def test(self):
        # from module.AirGap.implementation import AirGapParam
        # o = AirGapParam(title="NNNN")
        # o.edit(self)
        data = [
            {
                "type":"SignalFile", "name":"measurement-1.mat", "object":"nnn",
                "sub":[
                    {
                        "type":"AirGap", "name":"nde", "object":None,
                        "sub":[]
                    },{
                        "type":"FFT", "name":"vib",  "object":None,
                        "sub":[
                            {
                                "type":"Track", "name":"velocity", "object":None
                            }
                        ]
                    }
                ]
            },{
                "type":"SignalFile", "name":"measurement-2.mat", "object":None,
                "sub":[]
            }
        ]
        self.proj_list.setData(data)

    def import_mat(self):
        if not PROJPATH:
            QMessageBox.warning(self, APPNAME, 'Open a project first or create a new one.')
            return

        filename = QFileDialog.getOpenFileName(self, "Import Mat File", filter='Matlab File (*.mat)')
        if not filename:
            return

        self.statusBar().showMessage("Copying Matlab file ...")
        # fname = path.basename(filename)
        fname = str(uuid.uuid4()) + '.mat'
        # make a guid and ..
        QFile.copy(filename, path.join(PROJPATH,SOURCEDIR,fname))
        self.statusBar().showMessage("Copy done, parsing ...")
        # self.proj_list.addNewMat(fname)
        # self.track_list.addNewMat(fname)
        self.projectManager.addNewMat(fname)
        self.statusBar().showMessage("Done!", 3000)

    def open_project(self):
        filename = QFileDialog.getOpenFileName(self, "Open Project File", filter='JSON File (*.json) \n All (*.*)')
        if not filename:
            return

        filehandle = QFile(filename)
        if not filehandle.open(QFile.ReadWrite | QFile.Text):
            QMessageBox.warning(self, APPNAME,
                "Cannot open file %s:\n%s." % (filename, filehandle.errorString()))
            return
        
        # if self.project.read(filehandle):
        #     # clear/init qtree
        #     # self.projlist = self.project.widget
        #     pass

    def save_project(self):
        pass

    def new_project(self):
        if PROJPATH:
            # prompt to save project
            pass

        prjfolder = QFileDialog.getExistingDirectory(self, 'Select a Folder')
        if not prjfolder:
            return

    def quit(self):
        # make sure the project is saved
        self.close()

    def about(self):
        pass

    def game_same(self):
        pass

    def game_mine(self):
        pass

    def game_tetris(self):
        pass

if __name__ == "__main__":
    from guidata import qapplication
    app = qapplication()
    win = MainWindow()
    win.show()
    app.exec_()