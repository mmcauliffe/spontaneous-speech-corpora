import os
import pickle

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey,Boolean,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class Speaker(Base):
    """
    Model for storing information about speakers.
    """
    __tablename__ = 'speaker'
    
    id = Column(Integer, primary_key=True)
    
    number = Column(String(25), nullable=False)
    gender = Column(String(25), nullable=True)
    age = Column(String(25), nullable=True)
    
    def load_data(self,path,engine_string):
        if not os.path.exists(path):
            return
        engine = create_engine(engine_string)
         
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        files = os.listdir(path)
        files = [x for x in files if x.startswith(self.number) and x.endswith('.txt')]
        qs = session.query(Dialog).filter_by(speaker = self)
        if qs.count() == len(files):
            return
        segs = session.query(SegmentType).all()
        segs = { x.phon: x for x in segs}
        cats = session.query(Category).all()
        cats = { x.cat: x for x in cats}
        s = session.query(Speaker).get(self.id)
        print(s)
        dialogs = set([])
        for f in files:
            name = f.replace('.txt','')[:-1]
            if name not in dialogs:
                new_dialog = Dialog(number = name, speaker=s)
                session.add(new_dialog)
                dialogs.update([name])
            words = pickle.load(open(os.path.join(path,f),'rb'))
            for word in words:
                wordTypes = session.query(WordType).filter_by(orth=word['Word'])
                w = None
                if wordTypes.count():
                    for wType in wordTypes:
                        if wType.is_word() and wType.get_UR() == word['UR']:
                            w = wType
                            break
                        elif not wType.is_word():
                            w = wType
                if w is None:
                    w = WordType(orth=word['Word'])
                    session.add(w)
                    session.flush()
                    if w.is_word():
                        uls = []
                        ur = word['UR'].split(";")
                        for i in range(len(ur)):
                            sType = segs[ur[i]]
                            session.add(Underlying(wordtype=w,segmenttype=sType,position=i))
                        session.flush()
        session.commit()
        for f in files:
            name = f.replace('.txt','')[:-1]
            part = f.replace('.txt','')[-1]
            d = session.query(Dialog).filter_by(number = name)[0]
            words = pickle.load(open(os.path.join(path,f),'rb'))
            for word in words:
                cat = cats[word['Category']]
                wordTypes = session.query(WordType).filter_by(orth=word['Word'])
                if wordTypes.count() > 1:
                    for wType in wordTypes:
                        if wType.get_UR() == word['UR']:
                            w = wType
                            break
                else:
                    w = wordTypes[0]
                wt = WordToken(begin=word['Begin'],end=word['End'],wordtype=w,category=cat,dialog=d,dialog_part = part)
                session.add(wt)
                session.flush()
                if w.is_word():
                    for s in word['Phones']:
                        sType = segs[s['Label']]
                        session.add(Surface(wordtoken=wt,segmenttype = sType,begin=s['Begin'],end=s['End']))
                    session.flush()
        session.commit()
            
        
    
class Dialog(Base):
    """
    Model that allows for grouping words according the specific place
    they were spoken in.
    """
    __tablename__ = 'dialog'
    
    id = Column(Integer, primary_key=True)
    
    number = Column(String(25), nullable=False)
    speaker_id = Column(Integer, ForeignKey('speaker.id'))
    speaker = relationship(Speaker)


class Category(Base):
    """
    Syntactic parts of speech for a given word token, as listed in the
    Buckeye Corpus materials.

    Should probably be redone at some point.  Part of speech tagging
    for spontaneous speech is difficult.
    """
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    
    cat = Column(String(25), nullable=False)
    description = Column(String(250))
    categorytype = Column(String(100))

class SegmentType(Base):
    """
    Model for capturing phonological information about segments.
    """
    __tablename__ = 'segmenttype'
    
    id = Column(Integer, primary_key=True)
    
    phon = Column(String(25), nullable=False)
    syllabic = Boolean()
    obstruent = Boolean()
    nasal = Boolean()
    vowel = Boolean()

class WordType(Base):
    """
    Model for storing lexical information about word types in the corpus.

    Word types are more similar to word forms in CELEX than lemmas.

    No morphological information or lemma information which might be nice.
    """
    __tablename__ = 'wordtype'
    
    id = Column(Integer, primary_key=True)
    
    orth = Column(String(250), nullable=False)
    _segments = relationship('Underlying', backref='wordtype',
                           order_by='Underlying.position',
                           collection_class=ordering_list('position'))
    segments = association_proxy('_segments', 'segmenttype',
                               creator=lambda c: Underlying(segmenttype=c))
             
    def is_word(self):
        """
        Check for whether the word is an annotation label or a word.
        """
        if self.orth.startswith("{") or self.orth.startswith("<"):
            return False
        return True
        
    def get_UR(self):
        """
        Get the underlying representation for a word type, can include
        stress information, and be modified to fit the style for BLICK
        (CMU dictionary).
        """

        t = ';'.join([s.phon for s in self.segments])
        t = t.lower()
        return t
    
class Underlying(Base):
    """
    Many-to-many relation between word types and their underlying/canonical
    segments.
    """
    __tablename__ = 'underlying'
    
    id = Column(Integer, primary_key=True)
    
    wordtype_id = Column(Integer, ForeignKey('wordtype.id'))
    segmenttype_id = Column(Integer, ForeignKey('segmenttype.id'))

    segmenttype = relationship("SegmentType", backref="underlyings")
    
    position = Column(Integer)


class WordToken(Base):
    """
    Model for word tokens.
    """
    __tablename__ = 'wordtoken'
    
    id = Column(Integer, primary_key=True)
    
    wordtype_id = Column(Integer, ForeignKey('wordtype.id'))
    wordtype = relationship(WordType)
    
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    
    dialog_id = Column(Integer, ForeignKey('dialog.id'))
    dialog = relationship(Dialog)
    
    dialog_part = Column(String(2))
    
    begin = Column(Float)
    end = Column(Float)
    
    _segments = relationship('Surface', backref='wordtoken',
                           order_by='Surface.begin',
                           collection_class=ordering_list('begin'))
    segments = association_proxy('_segments', 'segment',
                               creator=lambda c: Surface(segmenttype=c))
    
class Surface(Base):
    """
    Model for surface realizations of words.
    """
    __tablename__ = 'surface'
    
    id = Column(Integer, primary_key=True)
    
    wordtoken_id = Column(Integer, ForeignKey('wordtoken.id'))
    segmenttype_id = Column(Integer, ForeignKey('segmenttype.id'))
    
    segmenttype = relationship("SegmentType", backref="surfaces")
    
    begin = Column(Float)
    end = Column(Float)

