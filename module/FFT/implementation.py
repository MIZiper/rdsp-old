from PyQt4 import QtGui

class FFTModule(object):
    ModuleName = 'FFT'

class FFTConfig(QtGui.QDialog):
    def __init__(self, config):
        QtGui.QDialog.__init__(self)
        self.config = config
        self.setWindowTitle('FFT Configuration')
        self.initUi()

    def initUi(self):
        config = self.config
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # number of lines

        # window

        # overlap

    def getResult(self):
        pass

if __name__ == '__main__':
    from guidata import qapplication
    app = qapplication()
    dialog = FFTConfig({})
    dialog.exec()
    print(dialog.result())