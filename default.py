"""
    default/embeded module for common use
"""

import uuid, numpy, os
from rdsp import gl
from os import path
from PyQt4.QtGui import QInputDialog
from guiqwt.builder import make

class SignalModule():
    ModuleName = 'Signal'
    ModuleType = gl.ModuleType.config
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
        self.config = {}

    def fillTracks(self, tracks):
        for track in tracks:
            t = TrackModule(track['guid'], track['name'], self)
            t.parseConfig(track['config'])
            self.tracks.append(t)

    def fillProcess(self, process):
        for prc in process:
            moduleClass = gl.moduleManager.getModule(prc['type'])
            if 'processed' in prc:
                p = moduleClass(prc['guid'], prc['name'], self, prc['processed'])
            else:
                p = moduleClass(prc['guid'], prc['name'], self)
            p.parseConfig(prc['config'])
            self.process.append(p)

    def loadTracks(self, trackData):
        pass

    def loadProcess(self, processData):
        pass
    
    def getTracksList(self):
        return [{'name':track.name,'guid':track.guid} for track in self.tracks]

    def getTrack(self, guid):
        for track in self.tracks:
            if track.guid == guid:
                return track
        return None
    
    def delProcess(self, process):
        self.process.remove(process)
        self.refresh()
    
    def refresh(self):
        gl.projectManager.refreshListWidget()
    
# custom part over, interface part start

    def parseConfig(self, config):
        self.config = config

    def configWindow(self):
        pass
    
    def getFileConfig(self):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'config':self.config,
            'tracks':[
                track.getFileConfig() for track in self.tracks
            ],
            'process':[
                process.getFileConfig() for process in self.process
            ]
        }
        
        return cfg

    def getProperty(self):
        return {
            "Record Date":self.config['date'],
            "Duration":self.config['length']
        }

    def addTracks(self, tracks):
        ts = []
        for track in tracks:
            track['guid'] = str(uuid.uuid4())
            t = TrackModule(track['guid'],track['name'],self,track['data'])
            t.parseConfig(track['config'])
            ts.append(t)
        self.tracks += ts
        self.parent.addTracks(tracks)
        return ts
        
    def removeTracks(self, tracks):
        for track in tracks:
            self.tracks.remove(track)
        self.parent.removeTracks(tracks)

# interface part over, event part start

    def delete(self):
        gl.projectManager.delSignal(self)
        # clean the tracks & process
        for prc in self.process:
            prc.delete()
        for track in self.tracks:
            track.delete()

    def newProcess(self):
        modulesName = gl.moduleManager.getModulesName()
        item, ok = QInputDialog.getItem(None,'Select a Module','Module:',modulesName,editable=False)
        if ok and item:
            moduleClass = gl.moduleManager.getModule(item)
            guid = str(uuid.uuid4())
            o = moduleClass(guid, item, self)
            # assert o.ModuleType & gl.ModuleType.process  ~= True
            if o.configWindow() and (o.ModuleType & gl.ModuleType.config):
                self.process.append(o)
                gl.projectManager.refreshListWidget()

class TrackModule():
    ModuleName = 'Track'
    ModuleType = gl.ModuleType.config
    ContextMenu = [
        {'title':'Display', 'action':'displayOverride'},
        {'title':'Display in New Window', 'action':'displayNew'},
        {'title':'Add to Display', 'action':'displayOverlap'}
        # ,{'title':'Detailed Display', 'action':'detailedDisplay'}
    ]

    def __init__(self, guid, name, parent, data=None):
        self.guid = guid
        self.name = name
        self.parent = parent
        self.data = data
        self.config = {}
        self.dataLoaded = data is not None

    def getData(self):
        if not self.dataLoaded:
            self.data = numpy.load(path.join(gl.projectPath,gl.SOURCEDIR,self.guid+gl.TRACKEXT))
            self.dataLoaded = True
        return self.data

    def getPlotData(self):
        data = self.getData()
        l = data.size / (self.config['bandwidth']*2.56)
        d = 1 / (self.config['bandwidth']*2.56)
        xs = numpy.arange(0,l,d)
        return (xs,data[0,:])

# custom part over, interface part start

    def parseConfig(self, config):
        self.config = config

    def getListConfig(self):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self
        }
        return cfg

    def getProperty(self):
        return {
            "BandWidth":self.config['bandwidth']
        }

    def getFileConfig(self):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'config':self.config
        }
        return cfg

    def delete(self):
        os.remove(path.join(gl.projectPath,gl.SOURCEDIR,self.guid+gl.TRACKEXT))

# interface part over, event part start

    def displayOverride(self):
        cw = gl.plotManager.requestCurrentCurve()
        if cw:
            plot = cw.plot
            (xs,ys) = self.getPlotData()
            curve = make.curve(xs, ys)
            if hasattr(cw,'RDSP_Curves'):
                cs = getattr(cw, 'RDSP_Curves')
                cs.clear()
                plot.del_all_items()
                plot.add_item(curve)
            else:
                plot.add_item(curve)
                cs = [curve]
                setattr(cw,'RDSP_Curves',cs)

    def displayNew(self):
        cw = gl.plotManager.requestNewCurve(self.name)
        plot = cw.plot
        (xs,ys) = self.getPlotData()
        curve = make.curve(xs,ys)
        plot.add_item(curve)

    def displayOverlap(self):
        cw = gl.plotManager.requestCurrentCurve()
        if cw:
            plot = cw.plot
            (xs,ys) = self.getPlotData()
            curve = make.mcurve(xs, ys)
            if hasattr(cw,'RDSP_Curves'):
                cs = getattr(cw, 'RDSP_Curves')
                cs.append(curve)
                plot.add_item(curve)
            else:
                plot.add_item(curve)
                cs = [curve]
                setattr(cw,'RDSP_Curves',cs)

class FakeSignal(SignalModule):
    # ModuleName
    ModuleType = gl.ModuleType.all
    # ContextMenu

    # __init__
    # fillTracks
    # fillProcess
    # getTracksList

    def getTrack(self, guid):
        return self.parent.getTrack(guid)
    # delProcess
    # refresh

    def parseConfig(self, config):
        self.tracks = [
            self.parent.getTrack(guid) for guid in config['tracks']
        ]
        self.fillProcess(config['process'])
    # configWindow
    def getFileConfig(self):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'config':{
                'tracks':[
                    track.guid for track in self.tracks
                ],
                'process':[
                    process.getFileConfig() for process in self.process
                ]
            }
        }
        return cfg
    
    def getProperty(self):
        return {}

    def delete(self):
        for prc in self.process:
            prc.delete()
        for track in self.tracks:
            track.delete()
        self.parent.delProcess(self)
        self.parent.removeTracks(self.tracks)
        # the track deletion should be performed by parent, finally by projMng

    def addTracks(self, tracksParam):
        tracks = self.parent.addTracks(tracksParam)
        self.tracks += tracks
        return tracks

    # newProcess
    def getListConfig(self):
        cfg = {
            'type':self.ModuleName,
            'guid':self.guid,
            'name':self.name,
            'object':self,
            'sub':[
                track.getListConfig() for track in self.tracks
            ] + [
                prc.getListConfig() for prc in self.process
            ]
        }
        return cfg