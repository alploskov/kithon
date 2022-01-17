from os import path, walk, listdir
from . import __path__ as ROOT_DIR


translators_dirr = path.join(path.split(ROOT_DIR[0])[0], 'translators')

def get_lang(lang):
    if lang not in listdir(translators_dirr):
        raise ValueError(f'{lang} is not supported')
    conf = []
    for dirr, _, files in walk(path.join(translators_dirr, lang)):
        conf += [\
            open(f'{dirr}/{f}', 'r') \
            for f in files
        ]
    return conf 
