"""Chat API endpoints for research assistant"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.conversation import Conversation, Message
from app.services.conversation_service import ConversationService
from app.services.claude_service import MockClaudeService

router = APIRouter()

# Initialize mock Claude service
claude_service = MockClaudeService()


class MessageRequest(BaseModel):
    """Request to send a message"""
    conversation_id: Optional[str] = None
    message: str


class MessageResponse(BaseModel):
    """Response with assistant's message"""
    conversation_id: str
    message_id: str
    content: str
    skill_used: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation summary"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class ConversationDetailResponse(BaseModel):
    """Conversation with messages"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[dict]


@router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest, db: Session = Depends(get_db)):
    """
    Send a message and get AI response
    
    If conversation_id is not provided, creates a new conversation.
    """
    # Create or get conversation
    if request.conversation_id:
        conversation = ConversationService.get_conversation(db, request.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation with title from first message
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        conversation = ConversationService.create_conversation(db, title)
    
    # Add user message
    user_message = ConversationService.add_message(
        db,
        str(conversation.id),
        "user",
        request.message
    )
    
    # Get conversation context
    context = ConversationService.get_conversation_context(db, str(conversation.id))
    
    # Get AI response from mock Claude
    ai_response = claude_service.send_message(
        request.message,
        conversation_history=context
    )
    
    # Add assistant message
    assistant_message = ConversationService.add_message(
        db,
        str(conversation.id),
        "assistant",
        ai_response
    )
    
    return MessageResponse(
        conversation_id=str(conversation.id),
        message_id=str(assistant_message.id),
        content=ai_response,
        skill_used=None
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(limit: int = 50, db: Session = Depends(get_db)):
    """List all conversations"""
    conversations = ConversationService.list_conversations(db, limit)
    
    return [
        ConversationResponse(
            id=str(conv.id),
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages)
        )
        for conv in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation with all messages"""
    conversation = ConversationService.get_conversation(db, conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = ConversationService.get_messages(db, conversation_id)
    
    return ConversationDetailResponse(
        id=str(conversation.id),
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "skill_used": msg.skill_used,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(title: str = "New Conversation", db: Session = Depends(get_db)):
    """Create a new conversation"""
    conversation = ConversationService.create_conversation(db, title)
    
    return ConversationResponse(
        id=str(conversation.id),
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=0
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation"""
    success = ConversationService.delete_conversation(db, conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Conversation deleted successfully"}
