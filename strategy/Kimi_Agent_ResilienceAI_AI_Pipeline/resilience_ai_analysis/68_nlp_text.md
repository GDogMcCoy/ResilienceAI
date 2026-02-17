# ResilienceAI NLP Capabilities Design Document

## Executive Summary

This document provides a comprehensive design for Natural Language Processing (NLP) capabilities in ResilienceAI. The NLP system is designed to process, analyze, and extract insights from unstructured text data across multiple domains including incident reports, social media, news articles, and internal communications.

---

## 1. NLP Architecture Overview

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ResilienceAI NLP Pipeline                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   Input      │───▶│  Language    │───▶│ Preprocessing│                  │
│  │   Sources    │    │  Detection   │    │   Pipeline   │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                                       │                           │
│         ▼                                       ▼                           │
│  ┌─────────────────────────────────────────────────────────┐               │
│  │              Core NLP Processing Layer                   │               │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │               │
│  │  │   NER   │ │Sentiment│ │Classification│ │ Topic   │       │               │
│  │  │ Module  │ │ Analysis│ │  Module │ │ Modeling│       │               │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │               │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │               │
│  │  │ Keyword │ │Document │ │  Text   │ │Embeddings│       │               │
│  │  │Extract  │ │Similarity│ │Summary │ │  Store  │       │               │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │               │
│  └─────────────────────────────────────────────────────────┘               │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────┐               │
│  │              Output & Visualization Layer               │               │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │               │
│  │  │  API    │ │Dashboard│ │ Reports │ │ Alerts  │       │               │
│  │  │ Gateway │ │   UI    │ │ Engine  │ │ System  │       │               │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │               │
│  └─────────────────────────────────────────────────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Core Framework | spaCy 3.x + Transformers | Fast, production-grade NLP |
| Deep Learning | PyTorch / TensorFlow | Custom model training |
| Embeddings | Sentence-Transformers | Semantic similarity |
| Classification | scikit-learn / Hugging Face | Text classification |
| Topic Modeling | Gensim / BERTopic | Unsupervised topic extraction |
| Summarization | Hugging Face Transformers | Abstractive/Extractive summarization |
| Visualization | Matplotlib, Plotly, WordCloud | Text visualization |
| Vector Store | FAISS / ChromaDB | Document embeddings storage |

---

## 2. Implementation Priority Order

```
Priority 1 (Core - Week 1-2):
├── Text Preprocessing
├── Language Detection
├── Named Entity Recognition
└── Sentiment Analysis

Priority 2 (Essential - Week 3-4):
├── Text Classification
├── Keyword Extraction
└── Document Similarity

Priority 3 (Advanced - Week 5-6):
├── Topic Modeling
├── Text Summarization
└── Text Visualization

Priority 4 (Optimization - Week 7-8):
├── Performance Tuning
├── Model Optimization
└── Integration Testing
```

---

## 3. Module Implementations

### 3.1 Text Preprocessing Module

**File Path:** `/resilience_ai/nlp/preprocessing.py`

```python
"""
Text Preprocessing Module for ResilienceAI
Handles cleaning, normalization, and tokenization of text data.
"""

import re
import string
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
import spacy
from spacy.tokens import Doc
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import unicodedata

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)


@dataclass
class PreprocessingConfig:
    """Configuration for text preprocessing."""
    lowercase: bool = True
    remove_punctuation: bool = True
    remove_numbers: bool = False
    remove_stopwords: bool = True
    remove_urls: bool = True
    remove_emails: bool = True
    remove_html: bool = True
    normalize_whitespace: bool = True
    remove_extra_spaces: bool = True
    lemmatize: bool = True
    stem: bool = False
    min_token_length: int = 2
    custom_stopwords: Optional[List[str]] = None
    preserve_entities: bool = True


class TextPreprocessor:
    """
    Comprehensive text preprocessing pipeline.
    
    Features:
    - Multi-language support
    - Configurable preprocessing steps
    - Entity preservation option
    - Batch processing capability
    """
    
    def __init__(self, config: Optional[PreprocessingConfig] = None, 
                 language: str = 'en'):
        """
        Initialize the text preprocessor.
        
        Args:
            config: Preprocessing configuration
            language: Language code (default: 'en')
        """
        self.config = config or PreprocessingConfig()
        self.language = language
        
        # Load spaCy model
        self.nlp = self._load_spacy_model(language)
        
        # Initialize NLTK components
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        if self.config.custom_stopwords:
            self.stop_words.update(self.config.custom_stopwords)
    
    def _load_spacy_model(self, language: str) -> spacy.Language:
        """Load appropriate spaCy model for the language."""
        model_map = {
            'en': 'en_core_web_sm',
            'es': 'es_core_news_sm',
            'fr': 'fr_core_news_sm',
            'de': 'de_core_news_sm',
            'it': 'it_core_news_sm',
            'pt': 'pt_core_news_sm',
            'nl': 'nl_core_news_sm',
            'ja': 'ja_core_news_sm',
            'zh': 'zh_core_web_sm'
        }
        
        model_name = model_map.get(language, 'en_core_web_sm')
        
        try:
            return spacy.load(model_name)
        except OSError:
            print(f"Downloading spaCy model: {model_name}")
            spacy.cli.download(model_name)
            return spacy.load(model_name)
    
    def preprocess(self, text: str) -> Dict[str, Union[str, List[str], Doc]]:
        """
        Preprocess a single text document.
        
        Args:
            text: Raw input text
            
        Returns:
            Dictionary containing processed text and metadata
        """
        if not text or not isinstance(text, str):
            return {
                'original': text,
                'cleaned': '',
                'tokens': [],
                'sentences': [],
                'spacy_doc': None
            }
        
        original = text
        
        # Step 1: Remove HTML tags
        if self.config.remove_html:
            text = self._remove_html(text)
        
        # Step 2: Remove URLs
        if self.config.remove_urls:
            text = self._remove_urls(text)
        
        # Step 3: Remove email addresses
        if self.config.remove_emails:
            text = self._remove_emails(text)
        
        # Step 4: Normalize Unicode
        text = self._normalize_unicode(text)
        
        # Step 5: Convert to lowercase
        if self.config.lowercase:
            text = text.lower()
        
        # Step 6: Remove numbers (optional)
        if self.config.remove_numbers:
            text = self._remove_numbers(text)
        
        # Step 7: Process with spaCy
        doc = self.nlp(text)
        
        # Step 8: Token processing
        tokens = self._process_tokens(doc)
        
        # Step 9: Normalize whitespace
        if self.config.normalize_whitespace:
            text = self._normalize_whitespace(text)
        
        # Step 10: Extract sentences
        sentences = [sent.text.strip() for sent in doc.sents]
        
        return {
            'original': original,
            'cleaned': text,
            'tokens': tokens,
            'sentences': sentences,
            'spacy_doc': doc,
            'token_count': len(tokens),
            'sentence_count': len(sentences)
        }
    
    def preprocess_batch(self, texts: List[str], 
                         batch_size: int = 100) -> List[Dict]:
        """
        Preprocess multiple texts in batches.
        
        Args:
            texts: List of raw texts
            batch_size: Number of texts to process at once
            
        Returns:
            List of preprocessing results
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Process with spaCy pipeline for efficiency
            docs = list(self.nlp.pipe(batch, batch_size=batch_size))
            
            for text, doc in zip(batch, docs):
                result = self._process_doc(text, doc)
                results.append(result)
        
        return results
    
    def _process_doc(self, text: str, doc: Doc) -> Dict:
        """Process a spaCy document."""
        # Apply preprocessing steps
        cleaned = text
        
        if self.config.remove_html:
            cleaned = self._remove_html(cleaned)
        if self.config.remove_urls:
            cleaned = self._remove_urls(cleaned)
        if self.config.remove_emails:
            cleaned = self._remove_emails(cleaned)
        
        cleaned = self._normalize_unicode(cleaned)
        
        if self.config.lowercase:
            cleaned = cleaned.lower()
        if self.config.remove_numbers:
            cleaned = self._remove_numbers(cleaned)
        
        tokens = self._extract_tokens_from_doc(doc)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        return {
            'original': text,
            'cleaned': cleaned,
            'tokens': tokens,
            'sentences': sentences,
            'token_count': len(tokens),
            'sentence_count': len(sentences)
        }
    
    def _process_tokens(self, doc: Doc) -> List[str]:
        """Extract and process tokens from spaCy document."""
        tokens = []
        
        for token in doc:
            # Skip punctuation if configured
            if self.config.remove_punctuation and token.is_punct:
                continue
            
            # Skip stopwords if configured
            if self.config.remove_stopwords and token.is_stop:
                continue
            
            # Skip short tokens
            if len(token.text) < self.config.min_token_length:
                continue
            
            # Preserve entities if configured
            if self.config.preserve_entities and token.ent_type_:
                tokens.append(token.text)
                continue
            
            # Apply lemmatization or stemming
            if self.config.lemmatize:
                processed_token = token.lemma_
            elif self.config.stem:
                processed_token = self.stemmer.stem(token.text)
            else:
                processed_token = token.text
            
            tokens.append(processed_token)
        
        return tokens
    
    def _extract_tokens_from_doc(self, doc: Doc) -> List[str]:
        """Extract tokens from spaCy document."""
        return self._process_tokens(doc)
    
    @staticmethod
    def _remove_html(text: str) -> str:
        """Remove HTML tags from text."""
        clean = re.compile('<.*?>')
        return re.sub(clean, ' ', text)
    
    @staticmethod
    def _remove_urls(text: str) -> str:
        """Remove URLs from text."""
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|'
            r'(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return url_pattern.sub(' ', text)
    
    @staticmethod
    def _remove_emails(text: str) -> str:
        """Remove email addresses from text."""
        email_pattern = re.compile(r'\S+@\S+')
        return email_pattern.sub(' ', text)
    
    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """Normalize Unicode characters."""
        return unicodedata.normalize('NFKD', text)
    
    @staticmethod
    def _remove_numbers(text: str) -> str:
        """Remove numeric characters from text."""
        return re.sub(r'\d+', ' ', text)
    
    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """Normalize whitespace characters."""
        return ' '.join(text.split())


class CrisisTextPreprocessor(TextPreprocessor):
    """
    Specialized preprocessor for crisis-related text.
    Preserves critical information like locations, dates, and emergency terms.
    """
    
    # Crisis-specific terms to preserve
    CRISIS_TERMS = {
        'emergency', 'disaster', 'evacuation', 'shelter', 'rescue',
        'casualty', 'injured', 'missing', 'trapped', 'flood', 'fire',
        'earthquake', 'hurricane', 'tornado', 'tsunami', 'landslide',
        'explosion', 'collapse', 'outbreak', 'pandemic', 'quarantine'
    }
    
    def __init__(self, config: Optional[PreprocessingConfig] = None):
        """Initialize crisis text preprocessor."""
        super().__init__(config)
        # Remove crisis terms from stopwords
        self.stop_words = self.stop_words - self.CRISIS_TERMS
```

---

### 3.2 Language Detection Module

**File Path:** `/resilience_ai/nlp/language_detection.py`

```python
"""
Language Detection Module for ResilienceAI
Detects the language of input text with confidence scores.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import fasttext
import langdetect
from langdetect import detect, detect_langs
import spacy
from spacy_langdetect import SpacyLanguageDetector
import os


@dataclass
class LanguageDetectionResult:
    """Result of language detection."""
    language_code: str
    language_name: str
    confidence: float
    is_reliable: bool
    alternative_languages: List[Dict[str, float]]


class LanguageDetector:
    """
    Multi-strategy language detection system.
    
    Supports:
    - fasttext (fast, accurate, supports 176 languages)
    - langdetect (Python-based, supports 55 languages)
    - spaCy integration (for pipeline use)
    """
    
    # Language code to name mapping
    LANGUAGE_NAMES = {
        'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
        'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'pl': 'Polish',
        'ru': 'Russian', 'ja': 'Japanese', 'zh': 'Chinese', 'ko': 'Korean',
        'ar': 'Arabic', 'hi': 'Hindi', 'tr': 'Turkish', 'vi': 'Vietnamese',
        'id': 'Indonesian', 'th': 'Thai', 'sv': 'Swedish', 'da': 'Danish',
        'no': 'Norwegian', 'fi': 'Finnish', 'cs': 'Czech', 'el': 'Greek',
        'he': 'Hebrew', 'uk': 'Ukrainian', 'ro': 'Romanian', 'hu': 'Hungarian'
    }
    
    def __init__(self, method: str = 'fasttext', 
                 model_path: Optional[str] = None,
                 confidence_threshold: float = 0.7):
        """
        Initialize language detector.
        
        Args:
            method: Detection method ('fasttext', 'langdetect', 'spacy')
            model_path: Path to fasttext model (if using fasttext)
            confidence_threshold: Minimum confidence for reliable detection
        """
        self.method = method
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        if method == 'fasttext':
            self._load_fasttext_model(model_path)
        elif method == 'spacy':
            self._setup_spacy_detector()
    
    def _load_fasttext_model(self, model_path: Optional[str] = None):
        """Load fasttext language detection model."""
        if model_path is None:
            # Download model if not present
            model_path = 'lid.176.ftz'
            if not os.path.exists(model_path):
                import urllib.request
                url = 'https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz'
                urllib.request.urlretrieve(url, model_path)
        
        self.model = fasttext.load_model(model_path)
    
    def _setup_spacy_detector(self):
        """Setup spaCy language detector."""
        self.nlp = spacy.load('en_core_web_sm')
        self.nlp.add_pipe('language_detector', last=True)
    
    def detect(self, text: str) -> LanguageDetectionResult:
        """
        Detect language of input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            LanguageDetectionResult with detection details
        """
        if not text or len(text.strip()) < 3:
            return LanguageDetectionResult(
                language_code='unknown',
                language_name='Unknown',
                confidence=0.0,
                is_reliable=False,
                alternative_languages=[]
            )
        
        if self.method == 'fasttext':
            return self._detect_fasttext(text)
        elif self.method == 'langdetect':
            return self._detect_langdetect(text)
        elif self.method == 'spacy':
            return self._detect_spacy(text)
        else:
            raise ValueError(f"Unknown detection method: {self.method}")
    
    def _detect_fasttext(self, text: str) -> LanguageDetectionResult:
        """Detect language using fasttext."""
        # fasttext requires single line input
        text = text.replace('\n', ' ')
        
        predictions = self.model.predict(text, k=3)
        labels = predictions[0]
        scores = predictions[1]
        
        # Extract language codes and scores
        languages = []
        for label, score in zip(labels, scores):
            lang_code = label.replace('__label__', '')
            languages.append({
                'code': lang_code,
                'confidence': float(score)
            })
        
        primary = languages[0]
        
        return LanguageDetectionResult(
            language_code=primary['code'],
            language_name=self.LANGUAGE_NAMES.get(primary['code'], 'Unknown'),
            confidence=primary['confidence'],
            is_reliable=primary['confidence'] >= self.confidence_threshold,
            alternative_languages=languages[1:]
        )
    
    def _detect_langdetect(self, text: str) -> LanguageDetectionResult:
        """Detect language using langdetect."""
        try:
            # Get probabilities for all detected languages
            probs = detect_langs(text)
            
            languages = []
            for prob in probs:
                languages.append({
                    'code': prob.lang,
                    'confidence': prob.prob
                })
            
            primary = languages[0]
            
            return LanguageDetectionResult(
                language_code=primary['code'],
                language_name=self.LANGUAGE_NAMES.get(primary['code'], 'Unknown'),
                confidence=primary['confidence'],
                is_reliable=primary['confidence'] >= self.confidence_threshold,
                alternative_languages=languages[1:]
            )
        except Exception as e:
            return LanguageDetectionResult(
                language_code='unknown',
                language_name='Unknown',
                confidence=0.0,
                is_reliable=False,
                alternative_languages=[],
                error=str(e)
            )
    
    def _detect_spacy(self, text: str) -> LanguageDetectionResult:
        """Detect language using spaCy."""
        doc = self.nlp(text)
        lang = doc._.language
        
        return LanguageDetectionResult(
            language_code=lang['language'],
            language_name=self.LANGUAGE_NAMES.get(lang['language'], 'Unknown'),
            confidence=lang['score'],
            is_reliable=lang['score'] >= self.confidence_threshold,
            alternative_languages=[]
        )
    
    def detect_batch(self, texts: List[str]) -> List[LanguageDetectionResult]:
        """Detect languages for multiple texts."""
        return [self.detect(text) for text in texts]
    
    def is_english(self, text: str, threshold: float = 0.8) -> bool:
        """Quick check if text is English."""
        result = self.detect(text)
        return result.language_code == 'en' and result.confidence >= threshold


class MultiLanguageProcessor:
    """
    Processor that handles multiple languages with appropriate models.
    """
    
    def __init__(self):
        """Initialize multi-language processor."""
        self.detector = LanguageDetector(method='fasttext')
        self.language_pipelines = {}
    
    def get_pipeline(self, language_code: str) -> spacy.Language:
        """Get or create spaCy pipeline for a language."""
        if language_code not in self.language_pipelines:
            model_map = {
                'en': 'en_core_web_sm',
                'es': 'es_core_news_sm',
                'fr': 'fr_core_news_sm',
                'de': 'de_core_news_sm'
            }
            
            model_name = model_map.get(language_code, 'en_core_web_sm')
            
            try:
                self.language_pipelines[language_code] = spacy.load(model_name)
            except OSError:
                self.language_pipelines[language_code] = spacy.load('en_core_web_sm')
        
        return self.language_pipelines[language_code]
    
    def process(self, text: str) -> Dict:
        """Process text with appropriate language pipeline."""
        # Detect language
        lang_result = self.detector.detect(text)
        
        # Get appropriate pipeline
        nlp = self.get_pipeline(lang_result.language_code)
        
        # Process text
        doc = nlp(text)
        
        return {
            'language': lang_result,
            'doc': doc,
            'tokens': [token.text for token in doc],
            'entities': [(ent.text, ent.label_) for ent in doc.ents],
            'sentences': [sent.text for sent in doc.sents]
        }
```

---

### 3.3 Named Entity Recognition Module

**File Path:** `/resilience_ai/nlp/entity_recognition.py`

```python
"""
Named Entity Recognition Module for ResilienceAI
Extracts and categorizes named entities from text with crisis-specific enhancements.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import spacy
from spacy.tokens import Doc, Span
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline as hf_pipeline
import re
from collections import defaultdict


class EntityType(Enum):
    """Extended entity types for crisis management."""
    # Standard spaCy types
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "GPE"
    FACILITY = "FAC"
    EVENT = "EVENT"
    DATE = "DATE"
    TIME = "TIME"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    CARDINAL = "CARDINAL"
    ORDINAL = "ORDINAL"
    PRODUCT = "PRODUCT"
    LAW = "LAW"
    LANGUAGE = "LANGUAGE"
    WORK_OF_ART = "WORK_OF_ART"
    
    # Crisis-specific types
    DISASTER_TYPE = "DISASTER_TYPE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    RESOURCE = "RESOURCE"
    CASUALTY = "CASUALTY"
    EMERGENCY_SERVICE = "EMERGENCY_SERVICE"
    SHELTER = "SHELTER"
    EVACUATION_ROUTE = "EVACUATION_ROUTE"
    CONTACT = "CONTACT"
    URGENCY_LEVEL = "URGENCY_LEVEL"


@dataclass
class Entity:
    """Represents a named entity."""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert entity to dictionary."""
        return {
            'text': self.text,
            'label': self.label,
            'start': self.start,
            'end': self.end,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


@dataclass
class EntityExtractionResult:
    """Result of entity extraction."""
    entities: List[Entity]
    entity_counts: Dict[str, int]
    entity_relationships: List[Dict]
    processed_text: str


class CrisisEntityRecognizer:
    """
    Specialized NER for crisis management scenarios.
    
    Features:
    - Standard entity recognition (person, organization, location)
    - Crisis-specific entities (disaster types, casualties, resources)
    - Multi-model ensemble approach
    - Entity relationship extraction
    - Confidence scoring
    """
    
    # Crisis-specific entity patterns
    DISASTER_PATTERNS = {
        'earthquake': ['earthquake', 'tremor', 'seismic', 'aftershock'],
        'flood': ['flood', 'flooding', 'deluge', 'inundation', 'flash flood'],
        'fire': ['fire', 'wildfire', 'bushfire', 'forest fire', 'blaze'],
        'hurricane': ['hurricane', 'typhoon', 'cyclone', 'tropical storm'],
        'tornado': ['tornado', 'twister', 'funnel cloud'],
        'tsunami': ['tsunami', 'tidal wave'],
        'landslide': ['landslide', 'mudslide', 'avalanche', 'rockfall'],
        'explosion': ['explosion', 'blast', 'detonation'],
        'collapse': ['collapse', 'cave-in', 'structural failure'],
        'outbreak': ['outbreak', 'epidemic', 'pandemic']
    }
    
    CASUALTY_PATTERNS = {
        'death': ['dead', 'deceased', 'killed', 'fatalities', 'death toll'],
        'injury': ['injured', 'wounded', 'hurt', 'casualties', 'victims'],
        'missing': ['missing', 'unaccounted for', 'disappeared'],
        'trapped': ['trapped', 'stranded', 'stuck', 'buried']
    }
    
    RESOURCE_PATTERNS = {
        'medical': ['ambulance', 'hospital', 'medic', 'doctor', 'nurse', 'medical'],
        'rescue': ['rescue team', 'search and rescue', 'SAR', 'first responder'],
        'supply': ['food', 'water', 'medicine', 'supplies', 'aid', 'relief'],
        'equipment': ['helicopter', 'boat', 'truck', 'vehicle', 'crane']
    }
    
    URGENCY_PATTERNS = {
        'critical': ['emergency', 'urgent', 'critical', 'immediate', 'life-threatening'],
        'high': ['severe', 'serious', 'major', 'significant'],
        'medium': ['moderate', 'concern', 'watch', 'advisory'],
        'low': ['minor', 'low risk', 'information', 'update']
    }
    
    def __init__(self, 
                 spacy_model: str = 'en_core_web_trf',
                 use_transformer_ner: bool = True,
                 confidence_threshold: float = 0.7):
        """
        Initialize crisis entity recognizer.
        
        Args:
            spacy_model: spaCy model to use
            use_transformer_ner: Whether to use transformer-based NER
            confidence_threshold: Minimum confidence for entity acceptance
        """
        self.confidence_threshold = confidence_threshold
        
        # Load spaCy model
        print(f"Loading spaCy model: {spacy_model}")
        self.nlp = spacy.load(spacy_model)
        
        # Add custom components
        self._add_custom_components()
        
        # Load transformer NER if requested
        self.transformer_ner = None
        if use_transformer_ner:
            self._load_transformer_ner()
    
    def _add_custom_components(self):
        """Add custom pipeline components for crisis NER."""
        # Add entity ruler for pattern-based matching
        if 'entity_ruler' not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe('entity_ruler', before='ner')
            
            # Add crisis-specific patterns
            patterns = []
            
            for disaster_type, terms in self.DISASTER_PATTERNS.items():
                for term in terms:
                    patterns.append({
                        'label': 'DISASTER_TYPE',
                        'pattern': term,
                        'id': disaster_type
                    })
            
            for category, terms in self.CASUALTY_PATTERNS.items():
                for term in terms:
                    patterns.append({
                        'label': 'CASUALTY',
                        'pattern': term,
                        'id': category
                    })
            
            for category, terms in self.RESOURCE_PATTERNS.items():
                for term in terms:
                    patterns.append({
                        'label': 'RESOURCE',
                        'pattern': term,
                        'id': category
                    })
            
            ruler.add_patterns(patterns)
    
    def _load_transformer_ner(self):
        """Load transformer-based NER model."""
        try:
            model_name = "dslim/bert-base-NER"
            self.transformer_ner = hf_pipeline(
                "ner",
                model=model_name,
                tokenizer=model_name,
                aggregation_strategy="simple"
            )
        except Exception as e:
            print(f"Could not load transformer NER: {e}")
            self.transformer_ner = None
    
    def extract_entities(self, text: str, 
                         include_crisis_entities: bool = True) -> EntityExtractionResult:
        """
        Extract entities from text.
        
        Args:
            text: Input text
            include_crisis_entities: Whether to include crisis-specific entities
            
        Returns:
            EntityExtractionResult with all extracted entities
        """
        # Process with spaCy
        doc = self.nlp(text)
        
        entities = []
        
        # Extract spaCy entities
        for ent in doc.ents:
            entity = Entity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
                confidence=getattr(ent._, 'confidence', 1.0),
                metadata={'source': 'spacy'}
            )
            entities.append(entity)
        
        # Extract transformer NER entities if available
        if self.transformer_ner:
            transformer_entities = self._extract_transformer_entities(text)
            entities.extend(transformer_entities)
        
        # Extract crisis-specific entities
        if include_crisis_entities:
            crisis_entities = self._extract_crisis_entities(text)
            entities.extend(crisis_entities)
        
        # Merge overlapping entities
        entities = self._merge_entities(entities)
        
        # Filter by confidence
        entities = [e for e in entities if e.confidence >= self.confidence_threshold]
        
        # Extract relationships
        relationships = self._extract_relationships(entities, doc)
        
        # Count entities by type
        entity_counts = defaultdict(int)
        for entity in entities:
            entity_counts[entity.label] += 1
        
        return EntityExtractionResult(
            entities=entities,
            entity_counts=dict(entity_counts),
            entity_relationships=relationships,
            processed_text=text
        )
    
    def _extract_transformer_entities(self, text: str) -> List[Entity]:
        """Extract entities using transformer model."""
        if not self.transformer_ner:
            return []
        
        results = self.transformer_ner(text)
        entities = []
        
        for result in results:
            entity = Entity(
                text=result['word'],
                label=result['entity_group'],
                start=result['start'],
                end=result['end'],
                confidence=result['score'],
                metadata={'source': 'transformer'}
            )
            entities.append(entity)
        
        return entities
    
    def _extract_crisis_entities(self, text: str) -> List[Entity]:
        """Extract crisis-specific entities using pattern matching."""
        entities = []
        text_lower = text.lower()
        
        # Extract urgency levels
        for level, terms in self.URGENCY_PATTERNS.items():
            for term in terms:
                for match in re.finditer(r'\b' + re.escape(term) + r'\b', text_lower):
                    # Find original case in text
                    start = match.start()
                    end = match.end()
                    original_text = text[start:end]
                    
                    entity = Entity(
                        text=original_text,
                        label='URGENCY_LEVEL',
                        start=start,
                        end=end,
                        confidence=0.9,
                        metadata={'urgency_level': level}
                    )
                    entities.append(entity)
        
        # Extract numbers with casualty context
        casualty_context = self.CASUALTY_PATTERNS
        for category, terms in casualty_context.items():
            for term in terms:
                # Look for patterns like "50 people killed" or "death toll: 100"
                pattern = r'(\d+)\s+(?:people\s+)?' + re.escape(term)
                for match in re.finditer(pattern, text_lower):
                    number = match.group(1)
                    start = match.start()
                    end = match.end()
                    
                    entity = Entity(
                        text=text[start:end],
                        label='CASUALTY_COUNT',
                        start=start,
                        end=end,
                        confidence=0.85,
                        metadata={
                            'category': category,
                            'count': int(number)
                        }
                    )
                    entities.append(entity)
        
        return entities
    
    def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge overlapping entities, keeping highest confidence."""
        if not entities:
            return []
        
        # Sort by start position and confidence
        sorted_entities = sorted(entities, key=lambda e: (e.start, -e.confidence))
        
        merged = []
        for entity in sorted_entities:
            # Check for overlap with last merged entity
            if merged and entity.start < merged[-1].end:
                # Keep the one with higher confidence
                if entity.confidence > merged[-1].confidence:
                    merged[-1] = entity
            else:
                merged.append(entity)
        
        return merged
    
    def _extract_relationships(self, entities: List[Entity], 
                               doc: Doc) -> List[Dict]:
        """Extract relationships between entities."""
        relationships = []
        
        # Group entities by type
        by_type = defaultdict(list)
        for entity in entities:
            by_type[entity.label].append(entity)
        
        # Find location-disaster relationships
        locations = by_type.get('GPE', []) + by_type.get('LOC', [])
        disasters = by_type.get('DISASTER_TYPE', [])
        
        for location in locations:
            for disaster in disasters:
                # Check if they're in the same sentence
                if self._in_same_sentence(location, disaster, doc):
                    relationships.append({
                        'type': 'LOCATION_DISASTER',
                        'location': location.to_dict(),
                        'disaster': disaster.to_dict(),
                        'confidence': min(location.confidence, disaster.confidence)
                    })
        
        # Find casualty-disaster relationships
        casualties = by_type.get('CASUALTY', []) + by_type.get('CASUALTY_COUNT', [])
        
        for casualty in casualties:
            for disaster in disasters:
                if self._in_same_sentence(casualty, disaster, doc):
                    relationships.append({
                        'type': 'CASUALTY_DISASTER',
                        'casualty': casualty.to_dict(),
                        'disaster': disaster.to_dict(),
                        'confidence': min(casualty.confidence, disaster.confidence)
                    })
        
        return relationships
    
    def _in_same_sentence(self, entity1: Entity, entity2: Entity, doc: Doc) -> bool:
        """Check if two entities are in the same sentence."""
        for sent in doc.sents:
            sent_start = sent.start_char
            sent_end = sent.end_char
            
            if (sent_start <= entity1.start < sent_end and 
                sent_start <= entity2.start < sent_end):
                return True
        
        return False
    
    def extract_locations(self, text: str) -> List[Entity]:
        """Extract only location entities."""
        result = self.extract_entities(text)
        location_labels = {'GPE', 'LOC', 'FACILITY', 'FAC'}
        return [e for e in result.entities if e.label in location_labels]
    
    def extract_organizations(self, text: str) -> List[Entity]:
        """Extract only organization entities."""
        result = self.extract_entities(text)
        return [e for e in result.entities if e.label == 'ORG']
    
    def extract_people(self, text: str) -> List[Entity]:
        """Extract only person entities."""
        result = self.extract_entities(text)
        return [e for e in result.entities if e.label == 'PERSON']
```

---

### 3.4 Sentiment Analysis Module

**File Path:** `/resilience_ai/nlp/sentiment_analysis.py`

```python
"""
Sentiment Analysis Module for ResilienceAI
Analyzes emotional tone and sentiment in crisis-related text.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline as hf_pipeline
import spacy
from textblob import TextBlob
import re


class SentimentType(Enum):
    """Sentiment classification types."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class EmotionType(Enum):
    """Emotion types for crisis analysis."""
    FEAR = "fear"
    ANGER = "anger"
    SADNESS = "sadness"
    JOY = "joy"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    HOPE = "hope"
    URGENCY = "urgency"


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    text: str
    sentiment_score: float  # -1 to 1
    sentiment_label: str
    confidence: float
    emotions: Dict[str, float]
    urgency_score: float
    subjectivity: float
    aspects: List[Dict[str, Any]]


@dataclass
class CrisisSentimentResult:
    """Sentiment result with crisis-specific metrics."""
    sentiment: SentimentResult
    panic_indicators: List[str]
    hope_indicators: List[str]
    trust_level: float
    information_reliability: float
    recommended_action: str


class CrisisSentimentAnalyzer:
    """
    Advanced sentiment analyzer for crisis scenarios.
    
    Features:
    - Multi-model ensemble (VADER, TextBlob, Transformers)
    - Crisis-specific emotion detection
    - Panic and urgency detection
    - Aspect-based sentiment analysis
    - Confidence scoring
    """
    
    # Crisis-specific sentiment words
    PANIC_WORDS = {
        'panic', 'terrified', 'horrified', 'desperate', 'chaos', 'catastrophe',
        'devastating', 'doomed', 'hopeless', 'helpless', 'trapped', 'dying',
        'emergency', 'urgent', 'critical', 'life-threatening', 'disaster'
    }
    
    HOPE_WORDS = {
        'hope', 'rescue', 'saved', 'survivors', 'relief', 'support', 'help',
        'recover', 'rebuild', 'together', 'strong', 'brave', 'heroes',
        'grateful', 'thankful', 'safe', 'protected'
    }
    
    TRUST_WORDS = {
        'official', 'confirmed', 'verified', 'authority', 'government',
        'expert', 'professional', 'reliable', 'credible', 'trustworthy'
    }
    
    URGENCY_MARKERS = {
        'immediately', 'urgent', 'asap', 'now', 'hurry', 'quick',
        'emergency', 'critical', 'life-threatening', 'dying'
    }
    
    def __init__(self, 
                 use_transformer: bool = True,
                 transformer_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest",
                 emotion_model: str = "j-hartmann/emotion-english-distilroberta-base"):
        """
        Initialize crisis sentiment analyzer.
        
        Args:
            use_transformer: Whether to use transformer models
            transformer_model: Transformer model for sentiment
            emotion_model: Transformer model for emotion detection
        """
        self.use_transformer = use_transformer
        
        # Load spaCy
        self.nlp = spacy.load('en_core_web_sm')
        
        # Load transformer pipelines
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        
        if use_transformer:
            try:
                self.sentiment_pipeline = hf_pipeline(
                    "sentiment-analysis",
                    model=transformer_model,
                    tokenizer=transformer_model
                )
            except Exception as e:
                print(f"Could not load sentiment pipeline: {e}")
            
            try:
                self.emotion_pipeline = hf_pipeline(
                    "text-classification",
                    model=emotion_model,
                    tokenizer=emotion_model,
                    top_k=None
                )
            except Exception as e:
                print(f"Could not load emotion pipeline: {e}")
    
    def analyze(self, text: str, 
                include_aspects: bool = True) -> CrisisSentimentResult:
        """
        Analyze sentiment of crisis-related text.
        
        Args:
            text: Input text to analyze
            include_aspects: Whether to include aspect-based analysis
            
        Returns:
            CrisisSentimentResult with comprehensive sentiment metrics
        """
        # Get base sentiment
        sentiment_result = self._analyze_sentiment(text, include_aspects)
        
        # Detect crisis-specific indicators
        panic_indicators = self._detect_panic_indicators(text)
        hope_indicators = self._detect_hope_indicators(text)
        
        # Calculate trust level
        trust_level = self._calculate_trust_level(text)
        
        # Calculate information reliability
        info_reliability = self._calculate_info_reliability(text, trust_level)
        
        # Determine recommended action
        recommended_action = self._determine_action(
            sentiment_result, panic_indicators, hope_indicators
        )
        
        return CrisisSentimentResult(
            sentiment=sentiment_result,
            panic_indicators=panic_indicators,
            hope_indicators=hope_indicators,
            trust_level=trust_level,
            information_reliability=info_reliability,
            recommended_action=recommended_action
        )
    
    def _analyze_sentiment(self, text: str, 
                           include_aspects: bool) -> SentimentResult:
        """Analyze base sentiment using multiple methods."""
        scores = []
        
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_score = blob.sentiment.polarity
        scores.append(('textblob', textblob_score, 0.6))
        
        # Transformer sentiment
        transformer_score = None
        transformer_confidence = 0.0
        
        if self.sentiment_pipeline:
            try:
                result = self.sentiment_pipeline(text[:512])[0]
                
                # Map labels to scores
                label_map = {
                    'negative': -1,
                    'neutral': 0,
                    'positive': 1
                }
                
                # Handle different label formats
                if isinstance(result, dict):
                    label = result['label'].lower()
                    if 'negative' in label:
                        transformer_score = -result['score']
                    elif 'positive' in label:
                        transformer_score = result['score']
                    else:
                        transformer_score = 0
                    transformer_confidence = result['score']
                
                scores.append(('transformer', transformer_score, 0.9))
            except Exception as e:
                print(f"Transformer sentiment error: {e}")
        
        # Calculate weighted average
        total_weight = sum(weight for _, _, weight in scores)
        weighted_score = sum(score * weight for _, score, weight in scores) / total_weight
        
        # Determine sentiment label
        sentiment_label = self._score_to_label(weighted_score)
        
        # Detect emotions
        emotions = self._detect_emotions(text)
        
        # Calculate urgency score
        urgency_score = self._calculate_urgency(text)
        
        # Extract aspects
        aspects = []
        if include_aspects:
            aspects = self._extract_aspects(text)
        
        return SentimentResult(
            text=text,
            sentiment_score=weighted_score,
            sentiment_label=sentiment_label,
            confidence=transformer_confidence if transformer_confidence > 0 else 0.7,
            emotions=emotions,
            urgency_score=urgency_score,
            subjectivity=blob.sentiment.subjectivity,
            aspects=aspects
        )
    
    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label."""
        if score <= -0.6:
            return SentimentType.VERY_NEGATIVE.value
        elif score <= -0.2:
            return SentimentType.NEGATIVE.value
        elif score <= 0.2:
            return SentimentType.NEUTRAL.value
        elif score <= 0.6:
            return SentimentType.POSITIVE.value
        else:
            return SentimentType.VERY_POSITIVE.value
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions in text."""
        emotions = {}
        
        if self.emotion_pipeline:
            try:
                result = self.emotion_pipeline(text[:512])[0]
                
                if isinstance(result, list):
                    for item in result:
                        emotions[item['label']] = item['score']
            except Exception as e:
                print(f"Emotion detection error: {e}")
        
        # Add crisis-specific emotions based on keyword matching
        text_lower = text.lower()
        
        # Fear detection
        fear_words = {'afraid', 'scared', 'fear', 'terrified', 'worried', 'anxious'}
        fear_count = sum(1 for word in fear_words if word in text_lower)
        emotions['fear'] = emotions.get('fear', 0) + (fear_count * 0.1)
        
        # Urgency detection
        urgency_count = sum(1 for word in self.URGENCY_MARKERS if word in text_lower)
        emotions['urgency'] = min(urgency_count * 0.2, 1.0)
        
        # Hope detection
        hope_count = sum(1 for word in self.HOPE_WORDS if word in text_lower)
        emotions['hope'] = min(hope_count * 0.15, 1.0)
        
        return emotions
    
    def _calculate_urgency(self, text: str) -> float:
        """Calculate urgency score from text."""
        text_lower = text.lower()
        
        urgency_score = 0.0
        
        # Count urgency markers
        for marker in self.URGENCY_MARKERS:
            if marker in text_lower:
                urgency_score += 0.2
        
        # Check for exclamation marks (capped)
        exclamation_count = text.count('!')
        urgency_score += min(exclamation_count * 0.1, 0.3)
        
        # Check for ALL CAPS words
        caps_words = [word for word in text.split() if word.isupper() and len(word) > 2]
        urgency_score += min(len(caps_words) * 0.05, 0.2)
        
        return min(urgency_score, 1.0)
    
    def _detect_panic_indicators(self, text: str) -> List[str]:
        """Detect panic-related indicators in text."""
        text_lower = text.lower()
        indicators = []
        
        for word in self.PANIC_WORDS:
            if word in text_lower:
                indicators.append(word)
        
        return indicators
    
    def _detect_hope_indicators(self, text: str) -> List[str]:
        """Detect hope-related indicators in text."""
        text_lower = text.lower()
        indicators = []
        
        for word in self.HOPE_WORDS:
            if word in text_lower:
                indicators.append(word)
        
        return indicators
    
    def _calculate_trust_level(self, text: str) -> float:
        """Calculate trust level of the text source."""
        text_lower = text.lower()
        
        trust_score = 0.5  # Neutral starting point
        
        # Check for trust indicators
        for word in self.TRUST_WORDS:
            if word in text_lower:
                trust_score += 0.1
        
        # Check for uncertainty markers (reduce trust)
        uncertainty_words = {'maybe', 'perhaps', 'might', 'possibly', 'rumor', 'unconfirmed'}
        for word in uncertainty_words:
            if word in text_lower:
                trust_score -= 0.1
        
        return max(0.0, min(1.0, trust_score))
    
    def _calculate_info_reliability(self, text: str, trust_level: float) -> float:
        """Calculate information reliability score."""
        # Combine trust level with other factors
        reliability = trust_level
        
        # Check for specific details (increases reliability)
        has_numbers = bool(re.search(r'\d+', text))
        has_locations = bool(re.search(r'\b(in|at|near)\s+\w+', text.lower()))
        
        if has_numbers:
            reliability += 0.1
        if has_locations:
            reliability += 0.1
        
        # Check for first-person accounts (mixed reliability)
        first_person = bool(re.search(r'\b(I|we|my|our)\b', text))
        if first_person:
            reliability += 0.05
        
        return max(0.0, min(1.0, reliability))
    
    def _extract_aspects(self, text: str) -> List[Dict[str, Any]]:
        """Extract aspects and their sentiments."""
        aspects = []
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract noun phrases as aspects
        for chunk in doc.noun_chunks:
            # Get sentiment of the sentence containing this chunk
            sentence = chunk.sent.text
            aspect_sentiment = TextBlob(sentence).sentiment.polarity
            
            aspects.append({
                'aspect': chunk.text,
                'sentiment': aspect_sentiment,
                'label': self._score_to_label(aspect_sentiment)
            })
        
        return aspects
    
    def _determine_action(self, sentiment: SentimentResult,
                          panic_indicators: List[str],
                          hope_indicators: List[str]) -> str:
        """Determine recommended action based on sentiment analysis."""
        if sentiment.urgency_score > 0.7:
            return "URGENT: Immediate response required"
        elif len(panic_indicators) > 2:
            return "HIGH: Address panic and provide reassurance"
        elif sentiment.sentiment_score < -0.5:
            return "MEDIUM: Provide support and accurate information"
        elif len(hope_indicators) > 2:
            return "LOW: Amplify positive messaging"
        else:
            return "MONITOR: Continue monitoring situation"
    
    def analyze_batch(self, texts: List[str]) -> List[CrisisSentimentResult]:
        """Analyze sentiment for multiple texts."""
        return [self.analyze(text) for text in texts]
```
