"""
Módulo para gestionar warnings innecesarios de Hugging Face y Transformers
"""

import os
import sys
import warnings
import logging
from dotenv import load_dotenv

load_dotenv()

os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

warnings.filterwarnings('ignore')

logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)

class quitar_warnings:
    def __enter__(self):
        self.original = sys.stderr
        sys.stderr = open(os.devnull, 'w')
    
    def __exit__(self, *args):
        sys.stderr.close()
        sys.stderr = self.original