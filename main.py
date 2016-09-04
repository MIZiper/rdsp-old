from guidata.qt.QtGui import (QMainWindow, QHBoxLayout, QTabWidget, QTreeWidget,
    QVBoxLayout, QListWidget, QSplitter, QVBoxLayout, QWidget,
    QFileDialog ,QMessageBox, QTreeWidgetItem, QMenu,
    QGridLayout, QApplication)
from guidata.qt.QtCore import QFile, QSettings
from guidata.qthelpers import (create_action, add_actions)
from guidata.qthelpers import Qt

from os import path, mkdir
import uuid, json

from util import ModuleManager, ProjectManager, PlotManager, ProgressManager

APPNAME = "RDSP"

import gl

class ListWidgetBase(QTreeWidget):
    def __init__(self, parent):
        QTreeWidget.__init__(self, parent)
        self.setHeaderLabels(("Type", "Name"))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def appendNode(self, parent, node):
        item = QTreeWidgetItem(parent)
        item.setText(0, node['type'])
        item.setText(1, node['name'])
        item.setData(0, 33, node['object']) # 33 user-role for module object
        if 'sub' in node:
            for subNode in node['sub']:
                self.appendNode(item, subNode)
    
    def registerPropertyWindow(self, prop_list):
        self.propertyWindow = prop_list
        self.currentItemChanged.connect(self.showProperty)

    def showProperty(self, item):
        if item == None:
            return
        boundObject = item.data(0, 33)
        prop = boundObject.getProperty()
        self.propertyWindow.clear()
        for (k,v) in prop.items():
            self.propertyWindow.addItem(k)
            self.propertyWindow.addItem('  '+str(v))

    def contextMenu(self, position):
        items = self.selectedItems()
        if len(items) > 0:
            boundObject = items[0].data(0, 33)
            moduleClassName = boundObject.ModuleName
            moduleClass = gl.moduleManager.getModule(moduleClassName)
            if moduleClass:
                menu = QMenu()
                import functools
                actions = (
                    create_action(
                        menu, action['title'],
                        triggered=functools.partial(
                            getattr(moduleClass,action['action']),
                            boundObject
                        )
                    ) for action in moduleClass.ContextMenu
                )
                add_actions(menu, actions)
                menu.exec_(self.viewport().mapToGlobal(position))

    def addNewSignal(self, signal):
        raise NotImplementedError

class ListProjectWidget(ListWidgetBase):
    def __init__(self, parent):
        ListWidgetBase.__init__(self, parent)

    def addNewSignal(self, signal):
        node = {
            'type':signal.ModuleName,
            'name':signal.name,
            'object':signal,
            'sub':[
                process.getListConfig() for process in signal.process
            ]
        }
        self.appendNode(self, node)

class ListTrackWidget(ListWidgetBase):
    def __init__(self, parent):
        ListWidgetBase.__init__(self, parent)

    def addNewSignal(self, signal):
        node = {
            'type':signal.ModuleName,
            'name':signal.name,
            'object':signal,
            'sub':[
                track.getListConfig() for track in signal.tracks
            ]
        }
        # change the type so as to drop "new process", but a new module class required
        self.appendNode(self, node)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        gl.moduleManager = ModuleManager()
        gl.projectManager = ProjectManager(self)
        gl.progress = ProgressManager(self)

        self.recentSetting = QSettings("AHC","rdsp")
        self.initUi()
        # self.loadModule()
        gl.plotManager = PlotManager(self.disp_widget)

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
        self.proj_list = ListProjectWidget(tab_list_widget)
        self.track_list = ListTrackWidget(tab_list_widget)
        tab_list_widget.addTab(self.proj_list, 'Project')
        tab_list_widget.addTab(self.track_list, 'Track')
        side_layout.addWidget(tab_list_widget, 0, 0)
        prop_widget = QListWidget(side_widget)
        self.proj_list.registerPropertyWindow(prop_widget)
        self.track_list.registerPropertyWindow(prop_widget)
        side_layout.addWidget(prop_widget, 1, 0)
        side_layout.setRowStretch(0, 2)
        side_layout.setRowStretch(1, 1)
        #
        disp_widget.setTabPosition(QTabWidget.South)
        disp_widget.setTabsClosable(True)
        disp_widget.tabCloseRequested.connect(self.plotTab_close)
        self.disp_widget = disp_widget
        #
        main_layout.addWidget(side_widget, 0, 0)
        main_layout.addWidget(disp_widget, 0, 1)
        main_layout.setColumnStretch(1, 30)
        main_layout.setColumnStretch(0, 10)
        self.setCentralWidget(main_widget)

    def loadModule(self):
        from default import SignalModule, TrackModule
        gl.moduleManager.registerModule(SignalModule)
        gl.moduleManager.registerModule(TrackModule)

        gl.projectManager.registerListWidget(self.proj_list)
        gl.projectManager.registerListWidget(self.track_list)

        self.statusBar().showMessage("Loading modules ...")
        import os, importlib
        dirs = os.listdir('module')
        # judge if it is dir
        for dir in dirs:
            modulePath = 'module.%s.implementation' % dir
            module = getattr(importlib.import_module(modulePath),'%sModule' % dir)
            gl.moduleManager.registerModule(module)
            # # the way should be like:
            # mod = __import__(dir, 'module')
            # gl.moduleManager.registerModule(mod)
            # # an __init__.py in dir should handle and export the moduleClass
            # # but don't know how to
        self.statusBar().showMessage("Done!", 3000)

    def plotTab_close(self, index):
        # import gc
        widget = self.disp_widget.widget(index)
        self.disp_widget.removeTab(index)
        gl.plotManager.clean(widget)
        widget.deleteLater()
        # gc.collect()

    def import_mat(self):
        if not gl.projectPath:
            QMessageBox.warning(self, APPNAME, 'Open a project first or create a new one.')
            return

        filename = QFileDialog.getOpenFileName(self, "Import Mat File", filter='Matlab File (*.mat)', directory=self.recentSetting.value('recentMat',''))
        if not filename:
            return

        self.statusBar().showMessage("Parsing Matlab file ...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.recentSetting.setValue('recentMat',path.dirname(filename))
        gl.projectManager.addNewMat(filename)
        self.statusBar().showMessage("Done!", 3000)
        QApplication.restoreOverrideCursor()

    def open_project(self):
        filename = QFileDialog.getOpenFileName(self, "Open Project File", filter='JSON File (*.json);;All (*.*)', directory=self.recentSetting.value('recentProj',''))
        if not filename:
            return

        filehandle = QFile(filename)
        if not filehandle.open(QFile.ReadWrite | QFile.Text):
            QMessageBox.warning(self, APPNAME,
                "Cannot open file %s:\n%s." % (filename, filehandle.errorString()))
            return
        
        gl.projectPath = path.dirname(filename)
        self.recentSetting.setValue('recentProj',gl.projectPath)
        gl.projectConfig = path.basename(filename)
        with open(filename) as fp:
            data = json.load(fp)

        gl.projectManager.initConfig(data)

    def save_project(self):
        if gl.projectPath:
            filename = path.join(gl.projectPath,gl.projectConfig)
            with open(filename, mode='w') as fp:
                json.dump(gl.projectManager.getConfig(),fp, indent=2)

    def new_project(self):
        if gl.projectPath:
            # prompt to save project
            pass

        prjfolder = QFileDialog.getExistingDirectory(self, 'Select a Folder', directory=self.recentSetting.value('recentProj',''))
        if not prjfolder:
            return

        gl.projectPath = prjfolder
        self.recentSetting.setValue('recentProj',gl.projectPath)
        try:
            mkdir(path.join(gl.projectPath,gl.SOURCEDIR))
            mkdir(path.join(gl.projectPath,gl.RESULTDIR))
        except:
            pass

        gl.projectManager.initConfig([])

    def quit(self):
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
    win.loadModule()
    app.exec_()