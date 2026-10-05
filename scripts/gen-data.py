import json, unicodedata as u

FLAT=set('N035 X001 D021 Q003 AA001 N016 N037 Z002 O029 D036 I009 D046 F013 N001 N017 W024 V031 V030 M003 Y005 D004 N025 N028 D040'.split())
NARROW=set('M017 S029 S034 M023 S040 W019 X008 F031 S042 D045 V028 Q001 I010 R008 O025 P006 U028 F012'.split())
def g(codes):
    out=[]
    for c in codes.split():
        try:
            out.append([u.lookup('EGYPTIAN HIEROGLYPH '+c), 'f' if c in FLAT else ('n' if c in NARROW else 'w')])
        except KeyError:
            print('MISSING', c)
    return out

T_HORUS = dict(codes='G005', tr='Ḥr', en='Horus', note='The falcon of Horus introduces the king\'s Horus name, written inside the serekh below it.')
T_SEREKH = dict(codes='E001 D040 N028 G017 S040 X001 O049', frame='serekh', tr='kꜣ-nḫt ḫꜥ-m-Wꜣst', en='Strong Bull, Appearing in Thebes', note='Thutmose III\'s Horus name, set inside a serekh: a stylised palace façade.')
T_NEBTY = dict(codes='G016 V029 M023 X001 W019 N005 G017 N001', tr='nb.ty wꜣḥ-nsyt mi Rꜥ m pt', en='He of the Two Ladies: Enduring of kingship, like Ra in heaven', note='The Nebty name, under the protection of the vulture (Upper Egypt) and the cobra (Lower Egypt).')
T_GOLD = dict(codes='G008 S042 F022 X001 D045 N028 Z002', tr='Ḥr-nbw sḫm-pḥty ḏsr-ḫꜥw', en='Golden Horus: Powerful of strength, sacred of appearances', note='The Golden Horus name: a falcon perched on the sign for gold.')
T_NSWBITY = dict(codes='M023 L002', tr='nswt-bjtj', en='King of Upper and Lower Egypt', note='Sedge and bee: the title that introduces the throne name.')
T_MENKH = dict(codes='N005 Y005 L001', frame='cartouche', tr='Mn-ḫpr-Rꜥ', en='Menkheperre: “Lasting is the manifestation of Ra”', note='Thutmose III\'s throne name in its cartouche. The sun disc is written first out of respect, but read last.')
T_SARA = dict(codes='G039 N005', tr='sꜣ Rꜥ', en='Son of Ra', note='Goose and sun disc: introduces the king\'s birth name.')
T_THUT = dict(codes='G026 F031 S029 F035 L001 Z002', frame='cartouche', tr='Ḏḥwtj-ms nfr-ḫprw', en='Thutmose, beautiful of forms', note='The birth name: “Thoth is born”. The ibis is the god Thoth.')
T_LIFE = dict(codes='X008 S034 W019 N005 I010 X001 N017', tr='dj ꜥnḫ mj Rꜥ ḏt', en='Given life, like Ra, forever', note='The standard closing formula for a royal inscription.')

def scene(god_side):
    return dict(codes='A040 R008 A030', kind='scene', tr='', en='Thutmose III before Amun-Ra', note='The scene at the top of each face shows the kneeling king presenting offerings to the enthroned god Amun-Ra, who grants him kingship.')

faces = [
  dict(name='Face I', subtitle='The Euphrates crossing', segs=[
    scene(0), T_HORUS, T_SEREKH, T_NSWBITY, T_MENKH,
    dict(codes='U028 G001 D054 Q003 AA001 D021 G036 N035 N035 O004 D021 N035 N025', tr='ḏꜣ pḫr-wr n Nhrn', en='who crossed the Great Bend of Naharin', note='The “Great Bend” is the Euphrates; Naharin is Mitanni in northern Mesopotamia. This is the 8th campaign, c. 1450 BC.'),
    dict(codes='G017 N035 M003 AA001 X001 D040 G017 F012 S029 D021 D040 D002 F004 X001 A012 Z002 I009', tr='m nḫt m wsr ḥr-ḥꜣt mšꜥ.f', en='in might and victory, at the head of his army', note='The core boast of the obelisk: the king personally leading his troops across the river.'),
    dict(codes='D004 F032 G001 M017 M017 X001 A014 O029 X001 M017 G017 S029 N035 Z002', tr='jr ẖꜣyt ꜥꜣt jm.sn', en='making a great slaughter among them', note='The text breaks off here: the lower third of the shaft was lost in antiquity.'),
  ]),
  dict(name='Face II', subtitle='The boundary at the Horn of the Earth', segs=[
    scene(1), T_GOLD, T_NSWBITY, T_MENKH, T_SARA, T_THUT,
    dict(codes='D004 N035 I009 N016 N037 I009 D021 F013 X001 N016', tr='jr.n.f tꜣš.f r wpt-tꜣ', en='who set his boundary at the Horn of the Earth', note='“Horn of the Earth” is the far southern edge of the known world: the claim is an empire from Nubia to the Euphrates.'),
    dict(codes='Q003 V028 G043 N035 O004 D021 N035 N025', tr='pḥw Nhrn', en='and at the marshes of Naharin', note='The northern limit: the marshlands of Mitanni beyond the Euphrates.'),
  ]),
  dict(name='Face III', subtitle='Dedication to Amun-Ra', segs=[
    scene(0), T_HORUS, T_SEREKH, dict(T_NEBTY), T_NSWBITY, T_MENKH,
    dict(codes='D004 N035 I009 G017 Y005 W024 G043 I009 N035 M017 X001 I009', tr='jr.n.f m mnw.f n jt.f', en='He made it as his monument for his father', note='The dedication formula found on almost every Egyptian obelisk.'),
    dict(codes='M017 Y005 N035 N005 V030 Q001 Z002 N016 N016', tr='Jmn-Rꜥ nb nswt tꜣwj', en='Amun-Ra, lord of the thrones of the Two Lands', note='Amun-Ra of Karnak, where the obelisk stood south of the 7th pylon until 357 AD.'),
    dict(codes='S029 D036 P006 D036 N035 I009 X001 AA001 N035 O025 Z002 G036 D021 G043 Z002', tr='sꜥḥꜥ n.f tḫnw wrw', en='erecting for him great obelisks', note='“Obelisks” in the plural: it was one of a pair. Its partner\'s fate is unknown.'),
  ]),
  dict(name='Face IV', subtitle='Lord of victories', segs=[
    scene(1), T_GOLD, T_SARA, T_THUT,
    dict(codes='U007 D021 M017 Y005 N035 N005 V030 Q001 Z002 N016 N016', tr='mrj Jmn-Rꜥ nb nswt tꜣwj', en='beloved of Amun-Ra, lord of the thrones of the Two Lands', note='The king presents himself as the god\'s favourite: victory is Amun\'s gift.'),
    dict(codes='V030 N035 M003 AA001 X001 D040 Z002 V015 N016 Z002 V030', tr='nb nḫtw jṯ tꜣw nbw', en='lord of victories, who seizes every land', note='A stock epithet of Thutmose III, the most campaigning pharaoh of the New Kingdom (17 campaigns).'),
    T_LIFE,
  ]),
]

for f in faces:
    new=[]
    for s in f['segs']:
        s=dict(s); s['glyphs']=g(s.pop('codes')); new.append(s)
    f['segs']=new

base = [
  dict(side='south', title='Pedestal · South', kind='relief', en='Theodosius I in the imperial box (kathisma), holding the victor\'s wreath, flanked by his court; below, spectators, musicians and dancers.', note='Carved c. 390 AD when the obelisk was raised on the spina of the Hippodrome. The water organ appears in the lower register.'),
  dict(side='east', title='Pedestal · East · Latin', kind='latin', lines=['DIFFICILIS QVONDAM DOMINIS PARERE SERENIS','IVSSVS ET EXTINCTIS PALMAM PORTARE TYRANNIS','OMNIA THEODOSIO CEDVNT SVBOLIQVE PERENNI','TER DENIS SIC VICTVS EGO DOMITVSQVE DIEBVS','IVDICE SVB PROCLO SVPERAS ELATVS AD AVRAS'], en='Once I resisted, but I was ordered to obey the serene lords and to carry the palm of victory over the slain tyrants. All things yield to Theodosius and his everlasting heirs. So I, conquered and tamed in thrice ten days, was raised to the heavens under the prefect Proclus.', note='Five Latin hexameters. The obelisk speaks in the first person.'),
  dict(side='north', title='Pedestal · North', kind='relief', en='The emperor and his court watch the races; the lower register shows the obelisk being hauled and raised with capstans.', note='A rare ancient depiction of how an obelisk was actually erected.'),
  dict(side='west', title='Pedestal · West · Greek', kind='greek', lines=['ΚΙΟΝΑ ΤΕΤΡΑΠΛΕΥΡΟΝ ΑΕΙ ΧΘΟΝΙ ΚΕΙΜΕΝΟΝ ΑΧΘΟΣ','ΜΟΥΝΟΣ ΑΝΑΣΤΗΣΑΙ ΘΕΥΔΟΣΙΟΣ ΒΑΣΙΛΕΥΣ','ΤΟΛΜΗΣΑΣ ΠΡΟΚΛΟΣ ΕΠΕΚΕΚΛΕΤΟ ΚΑΙ ΤΟΣΟΣ ΕΣΤΗ','ΚΙΩΝ ΗΕΛΙΟΙΣ ΕΝ ΤΡΙΑΚΟΝΤΑ ΔΥΩ'], en='This four-sided column, a burden long lying on the ground, the emperor Theodosius alone dared to raise. Proclus was charged with the task, and so great a column stood in thirty-two days.', note='Two elegiac couplets. Note the disagreement with the Latin side: 32 days here, 30 there.'),
]

open(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'data.js'),'w').write('window.OBELISK = ' + json.dumps(dict(faces=faces, base=base), ensure_ascii=False, indent=1) + ';\n')
print('ok', sum(len(s['glyphs']) for f in faces for s in f['segs']))
