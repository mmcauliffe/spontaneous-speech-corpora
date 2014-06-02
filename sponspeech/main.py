
import os
import numpy
import csv

import PySide

from PySide.QtCore import (qAbs, QLineF, QPointF, qrand, QRectF, QSizeF, qsrand,
        Qt, QTime,QSettings,QSize,QPoint)
from PySide.QtGui import (QBrush, QKeySequence, QColor, QLinearGradient, QPainter,
        QPainterPath, QPen, QPolygonF, QRadialGradient, QApplication, QGraphicsItem, QGraphicsScene,
        QGraphicsView, QStyle,QMainWindow, QAction, QDialog, QDockWidget, QHBoxLayout, QWidget,
        QFileDialog, QListWidget, QMessageBox,QTableWidget,QTableWidgetItem,QDialog,QItemSelectionModel,
        QPushButton,QLabel,QTabWidget,QGroupBox, QRadioButton,QVBoxLayout,QLineEdit,QFormLayout,
        QCheckBox)
        
from scipy.io import wavfile
        
import sqlalchemy, sqlalchemy.orm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

 
from db_models import Base,Speaker,SegmentType,Category,Dialog,WordToken,WordType
from qt_models import SpeakerTable,DialogTable,WordTokenTable

        
from views import TableWidget
        
def parse_file(path):
    output = []
    with open(path,'r') as f:
        reader = csv.DictReader(f,delimiter='\t')
        for row in reader:
            output.append(row)
    return output
        
        
GOOD_WORDS = ['back', 'bad', 'badge', 'bag', 'ball', 'bar', 'bare', 'base', 'bash', 'bass', 'bat', 'bath', 'beach', 'bean', 'bear', 'beat',
                 'bed', 'beer', 'bell', 'berth', 'big', 'bike', 'bill', 'birth', 'bitch', 'bite', 'boat', 'bob', 'boil', 'bomb', 'book', 'boom', 'boon',
                 'boss', 'bought', 'bout', 'bowl', 'buck', 'bum', 'burn', 'bus', 'bush', 'cab', 'cad', 'cake', 'calf', 'call', 'came', 'cap',
                 'car', 'care', 'case', 'cash', 'cat', 'catch', 'caught', 'cave', 'cell', 'chain', 'chair', 'chat', 'cheap', 'cheat', 'check',
                 'cheer', 'cheese', 'chess', 'chick', 'chief', 'chill', 'choice', 'choose', 'chose', 'church', 'coach', 'code', 'coke',
                 'comb', 'come', 'cone', 'cook', 'cool', 'cop', 'cope', 'corps', 'couch', 'cough', 'cub', 'cuff', 'cup', 'curl', 'curve', 'cut',
                 'dab', 'dad', 'dare', 'date', 'dawn', 'dead', 'deal', 'dear', 'death', 'debt', 'deck', 'deed', 'deep', 'deer', 'dime', 'dirt',
                 'doc', 'dodge', 'dog', 'dole', 'doll', 'doom', 'door', 'dot', 'doubt', 'duck', 'dug', 'dumb', 'face', 'fad', 'fade', 'fail',
                 'fair', 'faith', 'fake', 'fall', 'fame', 'fan', 'far', 'fat', 'faze', 'fear', 'fed', 'feed', 'feet', 'fell', 'fight', 'file', 'fill', 'fine',
                 'firm', 'fish', 'fit', 'fog', 'folk', 'food', 'fool', 'foot', 'fore', 'fought', 'fun', 'fuss', 'gain', 'game', 'gap', 'gas',
                 'gate', 'gave', 'gear', 'geese', 'gig', 'girl', 'give', 'goal', 'gone', 'good', 'goose', 'gum', 'gun', 'gut', 'gym', 'hail', 'hair',
                 'hall', 'ham', 'hang', 'hash', 'hat', 'hate', 'head', 'hear', 'heard', 'heat', 'height', 'hick', 'hid', 'hide', 'hill', 'hip', 'hit',
                 'hole', 'home', 'hood', 'hook', 'hop', 'hope', 'hot', 'house', 'hug', 'hum', 'hung', 'hurt', 'jab', 'jail', 'jam', 'jazz', 'jerk',
                 'jet', 'job', 'jog', 'join', 'joke', 'judge', 'june', 'keep', 'kick', 'kid', 'kill', 'king', 'kiss', 'knife', 'knit', 'knob', 'knock',
                 'known', 'lack', 'lag', 'laid', 'lake', 'lame', 'lane', 'lash', 'latch', 'late', 'laugh', 'lawn', 'league', 'leak', 'lean', 'learn',
                 'lease', 'leash', 'leave', 'led', 'leg', 'let', 'lid', 'life', 'light', 'line', 'load', 'loan', 'lock', 'lodge', 'lone', 'long', 'look',
                 'loose', 'lose', 'loss', 'loud', 'love', 'luck', 'mad', 'made', 'maid', 'mail', 'main', 'make', 'male', 'mall',
                 'map', 'mass', 'mat', 'match', 'math', 'meal', 'meat', 'meet', 'men', 'mess', 'met', 'mid', 'mike', 'mile', 'mill',
                 'miss', 'mock', 'moon', 'mouth', 'move', 'mud', 'nail', 'name', 'nap', 'neat', 'neck', 'need', 'nerve', 'net', 'news',
                 'nice', 'niche', 'niece', 'night', 'noise', 'noon', 'nose', 'notch', 'note', 'noun', 'nurse', 'nut', 'pace', 'pack', 'page',
                 'paid', 'pain', 'pair', 'pal', 'pass', 'pat', 'path', 'pawn', 'peace', 'peak', 'pearl', 'peek', 'peer', 'pen', 'pet', 'phase',
                 'phone', 'pick', 'piece', 'pile', 'pill', 'pine', 'pipe', 'pit', 'pool', 'poor', 'pop', 'pope', 'pot', 'pour', 'puck', 'push',
                 'put', 'race', 'rage', 'rail', 'rain', 'raise', 'ran', 'rash', 'rat', 'rate', 'rave', 'reach', 'rear', 'red', 'reef', 'reel',
                 'rice', 'rich', 'ride', 'ring', 'rise', 'road', 'roam', 'rob', 'rock', 'rode', 'role', 'roll', 'roof', 'room', 'rose', 'rough',
                 'rub', 'rude', 'rule', 'run', 'rush', 'sack', 'sad', 'safe', 'said', 'sake', 'sale', 'sang', 'sat', 'save', 'scene', 'search',
                 'seat', 'seen', 'sell', 'serve', 'set', 'sewn', 'shake', 'shame', 'shape', 'share', 'shave', 'shed', 'sheep', 'sheer', 'sheet',
                 'shell', 'ship', 'shirt', 'shock', 'shoot', 'shop', 'shot', 'shown', 'shun', 'shut', 'sick', 'side', 'sight', 'sign', 'sin', 'sing',
                 'sit', 'site', 'size', 'soap', 'son', 'song', 'soon', 'soul', 'soup', 'south', 'suit', 'sung', 'tab', 'tag', 'tail', 'take', 'talk',
                 'tap', 'tape', 'taught', 'teach', 'team', 'tease', 'teeth', 'tell', 'term', 'theme', 'thick', 'thief', 'thing', 'thought', 'tiff',
                 'tight', 'time', 'tip', 'tongue', 'took', 'tool', 'top', 'tore', 'toss', 'touch', 'tough', 'tour', 'town', 'tub', 'tube',
                 'tune', 'turn', 'type', 'use', 'van', 'vet', 'vice', 'voice', 'vote', 'wade', 'wage', 'wait', 'wake', 'walk', 'wall', 'war',
                 'wash', 'watch', 'wear', 'web', 'week', 'weight', 'wet', 'whack', 'wheat', 'wheel', 'whim', 'whine', 'whip', 'white',
                 'whole', 'wick', 'wide', 'wife', 'win', 'wine', 'wing', 'wise', 'wish', 'woke', 'womb', 'wood', 'word', 'wore', 'work',
                 'worse', 'wreck', 'wright', 'write', 'wrong', 'wrote', 'wrought', 'year', 'yell', 'young', 'youth', 'zip']

        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(1000, 800)

        self.settings = QSettings('settings.ini',QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)

        self.resize(self.settings.value('size', QSize(270, 225)))
        self.move(self.settings.value('pos', QPoint(50, 50)))
        self.speakerTable = TableWidget(self)
        self.dialogTable = TableWidget(self)
        self.tokenTable = TableWidget(self)
        self.speakerTable.setSortingEnabled(True)
        self.speakers = SpeakerTable()
        self.dialogs = DialogTable()
        self.tokens = WordTokenTable()
        self.speakerTable.setModel(self.speakers)
        self.dialogTable.setModel(self.dialogs)
        self.tokenTable.setModel(self.tokens)
        speakerSelectionModel = QItemSelectionModel(self.speakers)
        speakerSelectionModel.selectionChanged.connect(self.lookupDialogs)
        self.speakerTable.setSelectionModel(speakerSelectionModel)
        dialogSelectionModel = QItemSelectionModel(self.dialogs)
        dialogSelectionModel.selectionChanged.connect(self.lookupTokens)
        self.dialogTable.setSelectionModel(dialogSelectionModel)
        self.wrapper = QWidget()
        layout = QHBoxLayout(self.wrapper)
        layout.addWidget(self.speakerTable)
        layout.addWidget(self.dialogTable)
        layout.addWidget(self.tokenTable)
        self.wrapper.setLayout(layout)
        self.setCentralWidget(self.wrapper)

        self.engine_string = self.settings.value('engine_string','sqlite:///dev.db')
        self.engine = create_engine(self.engine_string)
        self.setUpCorpus()

        self.setWindowTitle("Exemplar Network Explorer")
        self.createActions()
        self.createMenus()
        
        #self.loadWordTokens()

    def lookupDialogs(self,sel):
        ind = sel.indexes()
        
        if len(ind) == 1:
            DBSession = sessionmaker(bind=self.engine)
            session = DBSession()
            s = self.speakerTable.model().query[ind[0].row()]
            print(s)
            qs = session.query(Dialog).filter_by(speaker_id=s.id).all()
            print(session.query(Dialog).all())
            print(qs)
            self.dialogTable.setModel(DialogTable(query=qs))
            
    def lookupTokens(self,sel):
        ind = sel.indexes()
        
        if len(ind) == 1:
            DBSession = sessionmaker(bind=self.engine)
            session = DBSession()
            d = self.dialogTable.model().query[ind[0].row()]
            qs = session.query(WordToken).filter_by(dialog_id=d.id).all()
            self.tokenTable.setModel(WordTokenTable(query=qs))
        

    def createActions(self):

        self.loadCorpusAct = QAction( "&Load corpus from folder",
                self, shortcut=QKeySequence.Open,
                statusTip="Load corpus from folder", triggered=self.loadCorpus)
                
        self.exportTokensAct = QAction( "&Export tokens to folder",
                self, shortcut=QKeySequence.Save,
                statusTip="Export tokens to folder", triggered=self.exportTokens)

        #self.editPreferencesAct = QAction( "&Preferences...",
        #        self,
        #        statusTip="Edit preferences", triggered=self.editPreferences)

        #self.specgramAct = QAction( "&View token spectrogram",
                #self,
                #statusTip="View token spectrogram", triggered=self.specgram)

        #self.detailsAct = QAction( "&View token details",
                #self,
                #statusTip="View token details", triggered=self.details)

        #self.envelopeAct = QAction( "&View token envelopes",
                #self,
                #statusTip="View token amplitude envelopes", triggered=self.envelope)

        #self.playfileAct = QAction( "&Play token",
                #self,
                #statusTip="Play token", triggered=self.playfile)

        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q",
                statusTip="Quit the application", triggered=self.close)

        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

    def exportTokens(self):
        export_path = QFileDialog.getExistingDirectory(self,
                "Choose a directory")
        if not export_path:
            return
        corpus_path = self.settings.value('path','')
        DBSession = sessionmaker(bind=self.engine)
        session = DBSession()
        qs = session.query(WordToken)
        print(qs)
        qs = qs.join(WordToken.wordtype)
        print(qs)
        qs = qs.join(WordToken.dialog)
        print(qs)
        qs = qs.filter(WordType.orth.in_(GOOD_WORDS)).order_by(Dialog.id)
        cur_dialog = ''
        for wt in qs:
            #if not wt.wordtype.is_word():
            #   continue
            if cur_dialog != wt.dialog.number:
                apath = os.path.join(corpus_path,'Processed','%sa.wav' % wt.dialog.number)
                bpath = os.path.join(corpus_path,'Processed','%sb.wav' % wt.dialog.number)
                if os.path.exists(apath):
                    sr, a = wavfile.read(apath)
                else:
                    a = None
                if os.path.exists(bpath):
                    sr, b = wavfile.read(bpath)
                else:
                    b = None
            filename = os.path.join(export_path,'%s_%s%s_%s_%d.wav' % (wt.dialog.speaker.number,
                                            wt.dialog.number,
                                            wt.dialog_part,
                                            wt.wordtype.orth,
                                            wt.id))
            
            begin = int(wt.begin * sr)
            end = int(wt.end * sr)
            if wt.dialog_part == 'a':
                out = a[begin:end]
            else:
                out = b[begin:end]
            newsr = 16000
            if newsr != sr:
                numt = int((wt.end - wt.begin) * 16000)
                out = resample(out,numt)
            wavfile.write(filename,sr,out)

    def loadCorpus(self):
        corpus_path = QFileDialog.getExistingDirectory(self,
                "Choose a directory")
        if not corpus_path:
            return
        self.settings.setValue('path',corpus_path)
        self.setUpCorpus()
        
    def setUpCorpus(self):
        if os.path.exists(os.path.split(self.engine_string)[1]):
            DBSession = sessionmaker(bind=self.engine)
            session = DBSession()
            q = session.query(Speaker).all()
            self.speakerTable.model().setQuery(q)
            return
        corpus_path = self.settings.value('path','')
        if corpus_path == '':
            return
        cat_file = os.path.join(corpus_path,'CategoryInfo.txt')
        speaker_file = os.path.join(corpus_path,'SpeakerInfo.txt')
        segment_file = os.path.join(corpus_path,'SegmentInfo.txt')
        if not os.path.exists(cat_file):
            return
        if not os.path.exists(speaker_file):
            return
        if not os.path.exists(segment_file):
            return
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        DBSession = sessionmaker(bind=self.engine)
        session = DBSession()
        speakers = parse_file(speaker_file)
         
        for s in speakers:
         
            new_speaker = Speaker(number=s['Number'],age=s['Age'],gender=s['Gender'])
            session.add(new_speaker)
        session.flush()
        q = session.query(Speaker).all()
        self.speakerTable.model().setQuery(q)
        #self.speakerTable.resizeColumnsToContents()
        
        categories = parse_file(cat_file)
        for c in categories:
            new_cat = Category(cat = c['Label'],
                                description = c['Description'],
                                categorytype = c['Type'])
            session.add(new_cat)
        session.flush()
        
        segs = parse_file(segment_file)
        for s in segs:
            new_st = SegmentType(phon = s['Label'],
                                syllabic = bool(int(s['Syllabic'])),
                                obstruent = bool(int(s['Obstruent'])),
                                nasal = bool(int(s['Nasal'])),
                                vowel = bool(int(s['Vowel'])))
            session.add(new_st)
        session.commit()
        
        for s in q:
            print(s.number)
            s.load_data(os.path.join(corpus_path,'Processed'),self.engine_string)
        
        

    def about(self):
        QMessageBox.about(self, "About Exemplar Network Explorer",
                "Placeholder "
                "Go on... ")

    #def editPreferences(self):
    #    dialog = PreferencesDialog(self,self.settings)
    #    result = dialog.exec_()
    #    if result:
    #        self.settings = dialog.settings
    #        self.loadWordTokens()

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.loadCorpusAct)
        self.fileMenu.addAction(self.exportTokensAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        #self.editMenu.addAction(self.editPreferencesAct)

        self.viewMenu = self.menuBar().addMenu("&View")

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)


    def closeEvent(self, e):
        self.settings.setValue('size', self.size())
        self.settings.setValue('pos', self.pos())
        e.accept()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
