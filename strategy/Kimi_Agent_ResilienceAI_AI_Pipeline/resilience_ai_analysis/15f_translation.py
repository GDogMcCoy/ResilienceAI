"""
ResilienceAI - Multi-Language Support
Translation and localization for international users.

File: src/nl_interface/translation.py
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class LanguageCode(Enum):
    """Supported language codes."""
    EN = "en"  # English
    ES = "es"  # Spanish
    FR = "fr"  # French
    DE = "de"  # German
    ZH = "zh"  # Chinese (Simplified)
    AR = "ar"  # Arabic
    HI = "hi"  # Hindi
    VI = "vi"  # Vietnamese
    KO = "ko"  # Korean
    RU = "ru"  # Russian
    PT = "pt"  # Portuguese
    JA = "ja"  # Japanese


class TranslationManager:
    """
    Multi-language translation manager.
    
    Features:
    - Automatic language detection
    - Translation of UI strings
    - Translation of responses
    - RTL language support
    """
    
    # UI strings translations
    UI_STRINGS = {
        "welcome_message": {
            "en": "Welcome to ResilienceAI. How can I help you assess disaster vulnerability today?",
            "es": "Bienvenido a ResilienceAI. Como puedo ayudarle a evaluar la vulnerabilidad a desastres hoy?",
            "fr": "Bienvenue sur ResilienceAI. Comment puis-je vous aider a evaluer la vulnerabilite aux catastrophes aujourd'hui?",
            "de": "Willkommen bei ResilienceAI. Wie kann ich Ihnen heute bei der Bewertung der Katastrophenanfalligkeit helfen?",
            "zh": "欢迎使用 ResilienceAI。今天我可以如何帮助您评估灾害脆弱性？",
            "ar": "مرحبًا بك في ResilienceAI. كيف يمكنني مساعدتك في تقييم الكوارث اليوم؟",
            "hi": "ResilienceAI में आपका स्वागत है। आज मैं आपको आपदा का assessment करने में कैसे मदद कर सकता हूँ?",
        },
        "ask_county": {
            "en": "Which county would you like to know about?",
            "es": "Sobre que condado le gustaria saber?",
            "fr": "De quel comte souhaitez-vous avoir des informations?",
            "de": "Uber welchen Bezirk mochten Sie mehr erfahren?",
            "zh": "您想了解哪个县？",
            "ar": "عن أي مقاطعة تود أن تعرف؟",
            "hi": "आप किस जिले के बारे में जानना चाहेंगे?",
        },
        "risk_score_label": {
            "en": "Risk Score",
            "es": "Puntuacion de Riesgo",
            "fr": "Score de Risque",
            "de": "Risiko-Score",
            "zh": "风险评分",
            "ar": "درجة المخاطرة",
            "hi": "जोखिम स्कोर",
        },
        "vulnerability_index": {
            "en": "Vulnerability Index",
            "es": "Indice de Vulnerabilidad",
            "fr": "Indice de Vulnerabilite",
            "de": "Verwundbarkeitsindex",
            "zh": "脆弱性指数",
            "ar": "مؤشر الضعف",
            "hi": "सूचकांक",
        },
        "high_risk_alert": {
            "en": "⚠️ High Risk Alert",
            "es": "⚠️ Alerta de Alto Riesgo",
            "fr": "⚠️ Alerte a Haut Risque",
            "de": "⚠️ Hochrisiko-Warnung",
            "zh": "⚠️ 高风险警报",
            "ar": "⚠️ تنبيه عالي الخطورة",
            "hi": "⚠️ उच्च जोखिम अलर्ट",
        },
        "error_message": {
            "en": "I'm sorry, I didn't understand. Could you rephrase that?",
            "es": "Lo siento, no entendi. Podria reformular eso?",
            "fr": "Je suis desole, je n'ai pas compris. Pourriez-vous reformuler?",
            "de": "Es tut mir leid, ich habe das nicht verstanden. Konnten Sie das umformulieren?",
            "zh": "抱歉，我没有理解。您能重新表述一下吗？",
            "ar": "عذرًا، لم أفهم. هل يمكنك إعادة صياغة ذلك؟",
            "hi": "मुझे खेद है, मैं समझ नहीं पाया। क्या आप इसे फिर से कह सकते हैं?",
        },
    }
    
    # Disaster type translations
    DISASTER_TYPES = {
        "flood": {
            "en": "Flood",
            "es": "Inundacion",
            "fr": "Inondation",
            "de": "Uberschwemmung",
            "zh": "洪水",
            "ar": "فيضان",
            "hi": "बाढ़",
        },
        "tornado": {
            "en": "Tornado",
            "es": "Tornado",
            "fr": "Tornade",
            "de": "Tornado",
            "zh": "龙卷风",
            "ar": "إعصار",
            "hi": "बवंडर",
        },
        "hurricane": {
            "en": "Hurricane",
            "es": "Huracan",
            "fr": "Ouragan",
            "de": "Hurrikan",
            "zh": "飓风",
            "ar": "إعصار",
            "hi": "हरिकेन",
        },
        "wildfire": {
            "en": "Wildfire",
            "es": "Incendio Forestal",
            "fr": "Feu de Foret",
            "de": "Waldbrand",
            "zh": "野火",
            "ar": "حريق غابات",
            "hi": "जंगल की आग",
        },
        "earthquake": {
            "en": "Earthquake",
            "es": "Terremoto",
            "fr": "Seisme",
            "de": "Erdbeben",
            "zh": "地震",
            "ar": "زلزال",
            "hi": "भूकंप",
        },
    }
    
    # RTL languages
    RTL_LANGUAGES = {"ar", "he", "ur", "fa"}
    
    def __init__(self, default_language: str = "en"):
        """Initialize translation manager."""
        self.default_language = default_language
        self.current_language = default_language
        
        # Try to import translation libraries
        try:
            from googletrans import Translator
            self._translator = Translator()
            self._auto_translate = True
        except ImportError:
            self._translator = None
            self._auto_translate = False
    
    def set_language(self, language_code: str):
        """Set the current language."""
        if language_code in [l.value for l in LanguageCode]:
            self.current_language = language_code
        else:
            raise ValueError(f"Unsupported language: {language_code}")
    
    def get_text(self, key: str, language: Optional[str] = None) -> str:
        """Get translated text for a key."""
        lang = language or self.current_language
        
        # Try to get from UI strings
        if key in self.UI_STRINGS:
            translations = self.UI_STRINGS[key]
            return translations.get(lang, translations.get("en", key))
        
        # Try to get from disaster types
        if key in self.DISASTER_TYPES:
            translations = self.DISASTER_TYPES[key]
            return translations.get(lang, translations.get("en", key))
        
        # Fall back to key itself
        return key
    
    def translate(
        self,
        text: str,
        target_language: Optional[str] = None,
        source_language: Optional[str] = None
    ) -> str:
        """Translate arbitrary text."""
        target = target_language or self.current_language
        source = source_language or "en"
        
        if target == source:
            return text
        
        if self._auto_translate and self._translator:
            try:
                result = self._translator.translate(
                    text,
                    src=source,
                    dest=target
                )
                return result.text
            except Exception as e:
                print(f"Translation failed: {e}")
                return text
        
        return text
    
    def detect_language(self, text: str) -> str:
        """Detect the language of text."""
        if self._translator:
            try:
                detection = self._translator.detect(text)
                return detection.lang
            except:
                pass
        
        # Simple heuristics as fallback
        text_lower = text.lower()
        
        # Spanish indicators
        if any(word in text_lower for word in ["el", "la", "los", "las", "es", "son"]):
            return "es"
        
        # French indicators
        if any(word in text_lower for word in ["le", "la", "les", "est", "sont"]):
            return "fr"
        
        # Default to English
        return "en"
    
    def is_rtl(self, language: Optional[str] = None) -> bool:
        """Check if language is right-to-left."""
        lang = language or self.current_language
        return lang in self.RTL_LANGUAGES
    
    def get_localized_number(self, number: float, language: Optional[str] = None) -> str:
        """Format number according to locale."""
        lang = language or self.current_language
        
        # Different decimal separators
        if lang in ["de", "fr", "es"]:
            return f"{number:.2f}".replace(".", ",")
        
        return f"{number:.2f}"
    
    def get_localized_date(
        self,
        date,
        language: Optional[str] = None,
        format: str = "medium"
    ) -> str:
        """Format date according to locale."""
        from datetime import datetime
        
        lang = language or self.current_language
        
        formats = {
            "short": "%m/%d/%Y" if lang == "en" else "%d/%m/%Y",
            "medium": "%B %d, %Y" if lang == "en" else "%d %B %Y",
            "long": "%A, %B %d, %Y" if lang == "en" else "%A, %d %B %Y",
        }
        
        fmt = formats.get(format, formats["medium"])
        return date.strftime(fmt)


class MultilingualResponseGenerator:
    """Generate responses in multiple languages."""
    
    def __init__(self, translation_manager: TranslationManager):
        self.tm = translation_manager
    
    def generate_vulnerability_response(
        self,
        county_data: Dict[str, Any],
        language: Optional[str] = None
    ) -> str:
        """Generate vulnerability report in specified language."""
        lang = language or self.tm.current_language
        
        county_name = county_data.get("county_name", "")
        state = county_data.get("state", "")
        risk_score = county_data.get("compound_risk_score", 0)
        
        # Template in English
        templates = {
            "en": f"{county_name} County, {state} has a risk score of {risk_score:.2f}.",
            "es": f"El condado de {county_name}, {state} tiene una puntuacion de riesgo de {risk_score:.2f}.",
            "fr": f"Le comte de {county_name}, {state} a un score de risque de {risk_score:.2f}.",
            "de": f"Der Bezirk {county_name}, {state} hat einen Risiko-Score von {risk_score:.2f}.",
            "zh": f"{county_name}县，{state}的风险评分为{risk_score:.2f}。",
        }
        
        return templates.get(lang, templates["en"])
