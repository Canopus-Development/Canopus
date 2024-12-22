import spacy
from typing import Dict, List, Tuple
import subprocess
import logging

class NLUProcessor:
    def __init__(self):
        self.logger = logging.getLogger('canopus.nlu')
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.info("Downloading English language model...")
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            self.nlp = spacy.load("en_core_web_sm")
            
        self.intent_patterns = {
            "code_nav": ["find", "goto", "navigate", "open"],
            "code_gen": ["generate", "create", "write"],
            "git": ["commit", "push", "pull", "merge"],
            "debug": ["debug", "fix", "solve"],
            "docs": ["explain", "document", "help"]
        }
        
    def process(self, text: str) -> Dict:
        doc = self.nlp(text.lower())
        
        return {
            "intent": self._detect_intent(doc),
            "entities": self._extract_entities(doc),
            "tokens": [token.text for token in doc],
            "original": text
        }
        
    def _detect_intent(self, doc) -> str:
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in doc.text.lower() for pattern in patterns):
                return intent
        return "unknown"
        
    def _extract_entities(self, doc) -> List[Tuple]:
        entities = []
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))
        return entities
