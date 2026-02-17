"""
ResilienceAI - Conversation Manager
Central orchestrator for natural language conversations.

File: src/nl_interface/conversation_manager.py
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Optional imports
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class ConversationStatus(Enum):
    """Conversation session status."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"


@dataclass
class DialogueTurn:
    """Represents a single turn in the conversation."""
    turn_id: str
    timestamp: datetime
    user_message: str
    intent: Optional[str] = None
    entities: Optional[Dict] = None
    agent_response: Optional[str] = None
    tool_calls: List[Dict] = field(default_factory=list)
    context_updates: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "turn_id": self.turn_id,
            "timestamp": self.timestamp.isoformat(),
            "user_message": self.user_message,
            "intent": self.intent,
            "entities": self.entities,
            "agent_response": self.agent_response,
            "tool_calls": self.tool_calls,
            "context_updates": self.context_updates
        }


@dataclass
class ConversationSession:
    """Complete conversation session with full context."""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    status: ConversationStatus
    context: Dict[str, Any] = field(default_factory=dict)
    turns: List[DialogueTurn] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    
    def add_turn(self, turn: DialogueTurn):
        self.turns.append(turn)
        self.last_activity = datetime.now()
    
    def get_last_n_turns(self, n: int = 3) -> List[DialogueTurn]:
        return self.turns[-n:] if len(self.turns) >= n else self.turns
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "status": self.status.value,
            "context": self.context,
            "turns": [t.to_dict() for t in self.turns],
            "user_preferences": self.user_preferences
        }


class ConversationManager:
    """
    Central manager for all NL conversations.
    
    Features:
    - Session lifecycle management
    - Context preservation across turns
    - State machine transitions
    - Multi-turn dialogue support
    - User preference learning
    """
    
    SESSION_TIMEOUT_MINUTES = 30
    MAX_HISTORY_TURNS = 20
    
    def __init__(
        self,
        use_redis: bool = False,
        redis_url: Optional[str] = None
    ):
        # Initialize components
        self.intent_recognizer = None  # Set externally
        self.entity_extractor = None  # Set externally
        self.context_engine = None  # Set externally
        self.response_generator = None  # Set externally
        self.agent_orchestrator = None  # Set externally
        
        # Session storage
        self._sessions: Dict[str, ConversationSession] = {}
        self._use_redis = use_redis and REDIS_AVAILABLE
        if self._use_redis and redis_url:
            self._redis = redis.from_url(redis_url)
        else:
            self._redis = None
    
    def create_session(self, user_id: str) -> ConversationSession:
        """Create a new conversation session."""
        session_id = str(uuid.uuid4())
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            status=ConversationStatus.ACTIVE,
            context={
                "referenced_counties": [],
                "referenced_state": None,
                "active_filters": {},
                "pending_clarification": None
            }
        )
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieve an existing session."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            if self._is_session_expired(session):
                session.status = ConversationStatus.EXPIRED
                return None
            return session
        return None
    
    def _is_session_expired(self, session: ConversationSession) -> bool:
        """Check if session has timed out."""
        timeout = timedelta(minutes=self.SESSION_TIMEOUT_MINUTES)
        return datetime.now() - session.last_activity > timeout
    
    def process_message(
        self,
        session_id: str,
        user_message: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate a response."""
        # Get or create session
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(user_id or "anonymous")
            session_id = session.session_id
        
        # Create new turn
        turn = DialogueTurn(
            turn_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_message=user_message
        )
        
        try:
            # Step 1: Check for pending clarification
            if session.context.get("pending_clarification"):
                return self._handle_clarification(session, user_message, turn)
            
            # Step 2: Recognize intent
            intent = self._recognize_intent(user_message, session)
            turn.intent = intent
            
            # Step 3: Extract entities
            entities = self._extract_entities(user_message, intent, session)
            turn.entities = entities
            
            # Step 4: Check if clarification needed
            if self._needs_clarification(intent, entities, session):
                return self._request_clarification(intent, entities, session, turn)
            
            # Step 5: Execute intent
            response_data = self._execute_intent(intent, entities, session)
            
            # Step 6: Generate response
            response_text = self._generate_response(intent, entities, response_data, session)
            turn.agent_response = response_text
            
            # Step 7: Save turn
            session.add_turn(turn)
            
            return {
                "session_id": session_id,
                "response": response_text,
                "intent": intent,
                "entities": entities,
                "data": response_data,
                "suggestions": self._generate_followup_suggestions(intent, entities)
            }
            
        except Exception as e:
            turn.agent_response = f"I encountered an error: {str(e)}"
            session.add_turn(turn)
            return {
                "session_id": session_id,
                "response": turn.agent_response,
                "error": str(e)
            }
    
    def _recognize_intent(self, message: str, session: ConversationSession) -> str:
        """Recognize user intent."""
        if self.intent_recognizer:
            return self.intent_recognizer.recognize(message, session.context)
        return "unknown"
    
    def _extract_entities(self, message: str, intent: str, session: ConversationSession) -> Dict:
        """Extract entities from message."""
        if self.entity_extractor:
            return self.entity_extractor.extract(message, intent, session.context)
        return {}
    
    def _needs_clarification(self, intent: str, entities: Dict, session: ConversationSession) -> bool:
        """Check if clarification is needed."""
        # County queries need location info
        if intent in ["query_vulnerability", "compare_counties"]:
            if not entities.get("counties") and not entities.get("states"):
                if not session.context.get("referenced_counties"):
                    return True
        return False
    
    def _request_clarification(self, intent: str, entities: Dict, session: ConversationSession, turn: DialogueTurn) -> Dict:
        """Request clarification from user."""
        prompt = "I'd be happy to help. Which county or state would you like to know about?"
        session.context["pending_clarification"] = {"intent": intent, "entities": entities}
        turn.agent_response = prompt
        session.add_turn(turn)
        
        return {
            "session_id": session.session_id,
            "response": prompt,
            "requires_clarification": True
        }
    
    def _handle_clarification(self, session: ConversationSession, message: str, turn: DialogueTurn) -> Dict:
        """Handle clarification response."""
        pending = session.context.pop("pending_clarification")
        # Process with pending context
        return {"session_id": session.session_id, "response": "Processing clarification..."}
    
    def _execute_intent(self, intent: str, entities: Dict, session: ConversationSession) -> Dict:
        """Execute the recognized intent."""
        if self.agent_orchestrator:
            return self.agent_orchestrator.execute(intent, entities)
        return {}
    
    def _generate_response(self, intent: str, entities: Dict, data: Dict, session: ConversationSession) -> str:
        """Generate natural language response."""
        if self.response_generator:
            return self.response_generator.generate(intent, entities, data, session.context)
        return "Response generated."
    
    def _generate_followup_suggestions(self, intent: str, entities: Dict) -> List[str]:
        """Generate follow-up query suggestions."""
        suggestions = {
            "query_vulnerability": [
                "Show me the top 10 highest risk counties",
                "Compare this to neighboring counties",
                "What's the forecast for next year?"
            ],
            "find_hotspots": [
                "Show details for the highest risk county",
                "What interventions would help most?",
                "Generate a briefing for these counties"
            ]
        }
        return suggestions.get(intent, [])[:3]
