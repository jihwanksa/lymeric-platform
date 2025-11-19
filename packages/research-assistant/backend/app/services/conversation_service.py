"""Conversation management service"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.conversation import Conversation, Message


class ConversationService:
    """Service for managing conversations and messages"""
    
    @staticmethod
    def create_conversation(db: Session, title: str = "New Conversation") -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    @staticmethod
    def list_conversations(db: Session, limit: int = 50) -> List[Conversation]:
        """List all conversations, ordered by most recent"""
        return db.query(Conversation).order_by(Conversation.updated_at.desc()).limit(limit).all()
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False
    
    @staticmethod
    def add_message(
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
        skill_used: Optional[str] = None
    ) -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            skill_used=skill_used
        )
        db.add(message)
        
        # Update conversation's updated_at timestamp
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get all messages in a conversation"""
        query = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_conversation_context(
        db: Session,
        conversation_id: str,
        max_messages: int = 20
    ) -> List[dict]:
        """
        Get recent messages as context for AI.
        
        Returns messages in format: [{"role": "user", "content": "..."}, ...]
        """
        messages = ConversationService.get_messages(db, conversation_id)
        
        # Get last N messages
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        # Convert to dict format
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]
    
    @staticmethod
    def update_conversation_title(
        db: Session,
        conversation_id: str,
        title: str
    ) -> Optional[Conversation]:
        """Update conversation title"""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(conversation)
        return conversation
