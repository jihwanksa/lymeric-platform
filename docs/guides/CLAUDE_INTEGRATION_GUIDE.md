# Claude API Integration Guide

**Upgrade from Mock Mode to Real Claude AI**

---

## Prerequisites

- Anthropic API account
- API key with credits
- Understanding of Claude API limits

---

## Step 1: Get API Key

1. Go to https://console.anthropic.com/
2. Create account or sign in
3. Navigate to API Keys
4. Create new key
5. Copy key (format: `sk-ant-xxx`)

**Cost:** ~$0.003 per message (Claude 3.5 Sonnet)

---

## Step 2: Install Dependencies

```bash
cd packages/research-assistant/backend
source venv/bin/activate
pip install anthropic==0.34.0
```

Add to `requirements.txt`:
```
anthropic==0.34.0
```

---

## Step 3: Create Real Claude Service

Create `packages/research-assistant/backend/app/services/claude_service.py`:

```python
"""Real Claude API integration"""
from anthropic import Anthropic
from typing import List, Dict, Optional
import os


class ClaudeService:
    """
    Production Claude service using Anthropic API.
    
    Replaces MockClaudeService for production use.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude client with API key."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 4096
        self.is_mock = False
    
    def send_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        skill_context: Optional[Dict] = None
    ) -> str:
        """
        Send message to Claude API and get response.
        
        Args:
            message: User's message
            conversation_history: Previous messages for context
            skill_context: Results from skill execution, if any
            
        Returns:
            Claude's response text
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(skill_context)
        
        # Build conversation messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Claude API error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def stream_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        skill_context: Optional[Dict] = None
    ):
        """
        Stream response from Claude API (for real-time typing effect).
        
        Yields response chunks as they arrive.
        """
        system_prompt = self._build_system_prompt(skill_context)
        
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def _build_system_prompt(self, skill_context: Optional[Dict] = None) -> str:
        """
        Build system prompt with context from skills.
        
        Customizes Claude's behavior based on skill results.
        """
        base_prompt = """You are an expert materials science research assistant.

Your capabilities:
- Predict material properties (Tg, FFV, Tc, density, Rg)
- Analyze materials datasets
- Search scientific literature
- Suggest synthesis routes
- Recommend similar materials

Always provide detailed, accurate, scientific responses.
Use proper chemical nomenclature and SMILES notation when relevant.
"""
        
        # Add skill context if available
        if skill_context:
            skill_name = skill_context.get('skill_name', '')
            skill_data = skill_context.get('data', {})
            
            if skill_name == 'property_prediction':
                base_prompt += f"\n\nProperty Prediction Results:\n{skill_data}"
            elif skill_name == 'data_analysis':
                base_prompt += f"\n\nDataset Analysis:\n{skill_data}"
            elif skill_name == 'literature_search':
                base_prompt += f"\n\nLiterature Search Results:\n{skill_data}"
        
        return base_prompt
```

---

## Step 4: Update Chat API

Modify `packages/research-assistant/backend/app/api/chat.py`:

```python
"""Chat API endpoints for research assistant"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

from app.core.database import get_db
from app.models.conversation import Conversation, Message
from app.services.conversation_service import ConversationService

# Import the REAL Claude service
from app.services.claude_service import ClaudeService

router = APIRouter()

# Initialize with real Claude (will fail if no API key)
try:
    claude_service = ClaudeService()
    print("✅ Using REAL Claude API")
except ValueError:
    # Fallback to mock if no API key
    from app.services.claude_service_mock import MockClaudeService
    claude_service = MockClaudeService()
    print("⚠️  Using MOCK Claude (no API key found)")

# Rest of the code stays the same...
```

---

## Step 5: Environment Variables

### Development (.env)
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
```

### Production
Set in your deployment platform:
- Render: Environment Variables section
- AWS: ECS Task Definition
- GCP: Cloud Run environment variables

---

## Step 6: Implement Skills System

Create skill implementations that Claude can use:

### Property Prediction Skill
```python
"""Property prediction skill using ML model"""
class PropertyPredictionSkill:
    def can_handle(self, query: str) -> bool:
        keywords = ['predict', 'property', 'tg', 'ffv', 'density']
        return any(kw in query.lower() for kw in keywords)
    
    async def execute(self, query: str, context: dict) -> dict:
        # Extract SMILES from query
        smiles = self._extract_smiles(query)
        
        # Call predictor service
        from packages.ai_services.src.predictor import PolymerPredictor
        predictor = PolymerPredictor()
        results = predictor.predict(smiles)
        
        return {
            'skill_name': 'property_prediction',
            'data': results
        }
```

### Data Analysis Skill
```python
"""Data analysis skill querying materials database"""
class DataAnalysisSkill:
    def can_handle(self, query: str) -> bool:
        keywords = ['analyze', 'dataset', 'statistics', 'materials']
        return any(kw in query.lower() for kw in keywords)
    
    async def execute(self, query: str, context: dict) -> dict:
        # Query data platform API
        import requests
        response = requests.get('http://localhost:8000/api/quality/summary')
        data = response.json()
        
        return {
            'skill_name': 'data_analysis',
            'data': data
        }
```

---

## Step 7: Add Skill Router

Create `packages/research-assistant/backend/app/services/skill_router.py`:

```python
"""Route queries to appropriate skills"""
from typing import Optional, Dict
from .skills import (
    PropertyPredictionSkill,
    DataAnalysisSkill,
    LiteratureSearchSkill,
    SynthesisPlanningSkill,
    MaterialRecommendationSkill
)


class SkillRouter:
    """Routes queries to the best skill handler"""
    
    def __init__(self):
        self.skills = [
            PropertyPredictionSkill(),
            DataAnalysisSkill(),
            LiteratureSearchSkill(),
            SynthesisPlanningSkill(),
            MaterialRecommendationSkill()
        ]
    
    async def route(self, query: str, context: dict) -> Optional[Dict]:
        """
        Find and execute the best skill for this query.
        
        Returns skill results or None if no skill matches.
        """
        for skill in self.skills:
            if skill.can_handle(query):
                return await skill.execute(query, context)
        
        return None  # No skill matched, use general Claude
```

---

## Step 8: Update Chat Endpoint with Skills

```python
@router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest, db: Session = Depends(get_db)):
    """Send message with skill routing"""
    
    # ... (conversation setup code) ...
    
    # Try to route to a skill
    skill_router = SkillRouter()
    skill_result = await skill_router.route(request.message, {})
    
    # Get AI response with skill context
    ai_response = claude_service.send_message(
        request.message,
        conversation_history=context,
        skill_context=skill_result
    )
    
    # Track which skill was used
    skill_used = skill_result['skill_name'] if skill_result else None
    
    # Add assistant message
    assistant_message = ConversationService.add_message(
        db,
        str(conversation.id),
        "assistant",
        ai_response,
        skill_used=skill_used
    )
    
    # ... (return response) ...
```

---

## Step 9: Add Streaming Support

### Backend Streaming Endpoint
```python
from fastapi.responses import StreamingResponse

@router.post("/message/stream")
async def stream_message(request: MessageRequest, db: Session = Depends(get_db)):
    """Stream response in real-time"""
    
    async def generate():
        # ... (setup) ...
        
        for chunk in claude_service.stream_message(message, context):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### Frontend Streaming
```typescript
const sendMessage = async () => {
  const response = await fetch('http://localhost:8001/api/chat/message/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userMessage })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    // Update UI with chunk
    setAssistantMessage(prev => prev + chunk);
  }
};
```

---

## Step 10: Testing

### Test with curl
```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-xxx

# Start backend
cd packages/research-assistant/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001

# Test in another terminal
curl -X POST http://localhost:8001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the glass transition temperature of polystyrene?"}'
```

---

## Cost Management

### Monitor Usage
```python
# Add token counting
def count_tokens(text: str) -> int:
    # Approximate: 1 token ≈ 4 characters
    return len(text) // 4

# Log costs
cost_per_1k_tokens = 0.003
tokens_used = count_tokens(user_message + assistant_response)
cost = (tokens_used / 1000) * cost_per_1k_tokens
print(f"Message cost: ${cost:.4f}")
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat/message")
@limiter.limit("10/minute")  # Max 10 messages per minute
async def send_message(...):
    ...
```

---

## Migration Checklist

- [ ] Get Anthropic API key
- [ ] Install anthropic package
- [ ] Create ClaudeService
- [ ] Update chat.py imports
- [ ] Set ANTHROPIC_API_KEY environment variable
- [ ] Test with real Claude
- [ ] Implement skills (optional)
- [ ] Add streaming (optional)
- [ ] Set up rate limiting
- [ ] Monitor costs
- [ ] Update frontend UI badge ("Real Claude" instead of "Mock Mode")

---

## Rollback Plan

If issues occur, easily rollback to mock:

```python
# In chat.py
USE_REAL_CLAUDE = os.getenv("USE_REAL_CLAUDE", "false").lower() == "true"

if USE_REAL_CLAUDE:
    claude_service = ClaudeService()
else:
    claude_service = MockClaudeService()
```

---

## Expected Results

**Before (Mock):**
- Predefined responses
- No cost
- Instant responses
- Limited context awareness

**After (Real Claude):**
- Intelligent, context-aware responses
- ~$0.003 per message
- ~1-2 second response time
- Full conversation understanding
- Ability to use skills effectively

---

**Status:** Ready for Claude API integration ✅  
**Estimated Time:** 1-2 hours
