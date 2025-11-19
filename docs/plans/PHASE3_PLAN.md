# Phase 3 Implementation Plan: Research Assistant

## Goal
Build an AI-powered research assistant chatbot using Claude API to help materials researchers with literature search, data analysis, property predictions, synthesis planning, and material recommendations.

## User Review Required

> [!IMPORTANT]
> **Claude API Key Required**: You'll need an Anthropic API key to enable the research assistant. The code will work without it (mock mode), but full functionality requires a valid API key.

> [!WARNING]  
> **API Costs**: Claude API calls incur costs. Implement rate limiting and conversation limits for production use.

---

## Proposed Changes

### Backend: Research Assistant Service

#### [NEW] **`packages/research-assistant/backend/app/services/claude_service.py`**
**Summary:** Core Claude API integration service
- Initialize Anthropic client with API key
- Send messages with system prompts
- Handle streaming responses
- Error handling and retry logic
- Token counting and cost estimation

#### [NEW] **`packages/research-assistant/backend/app/services/conversation_service.py`**
**Summary:** Conversation management and history
- Store conversation history in database
- Context window management (truncate old messages)
- Conversation retrieval and persistence
- Message threading

#### [MODIFY] **`packages/research-assistant/backend/app/services/skills_service.py`**
**Summary:** Enhanced skills with actual implementations
- **Literature Search**: Query PubChem/PubMed APIs for relevant papers
- **Data Analysis**: Query Lymeric data platform for material statistics
- **Property Prediction**: Call ML prediction service
- **Synthesis Planning**: Template-based synthesis route suggestions
- **Material Recommendations**: Similarity search based on properties

---

### Backend: API Endpoints

#### [NEW] **`packages/research-assistant/backend/app/api/chat.py`**
**Summary:** Chat API endpoints
- `POST /api/chat/message` - Send message and get response
- `GET /api/chat/conversations` - List user conversations
- `GET /api/chat/conversations/{id}` - Get conversation history
- `DELETE /api/chat/conversations/{id}` - Delete conversation
- `POST /api/chat/conversations` - Create new conversation

#### [NEW] **`packages/research-assistant/backend/app/models/conversation.py`**
**Summary:** SQLAlchemy models for conversations and messages
```python
class Conversation:
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    
class Message:
    id: UUID
    conversation_id: UUID
    role: str  # 'user' or 'assistant'
    content: str
    skill_used: Optional[str]
    created_at: datetime
```

---

### Frontend: Chat Interface

#### [NEW] **`packages/research-assistant/frontend/app/chat/page.tsx`**
**Summary:** Main chat interface
- Message list with user/assistant bubbles
- Input box with send button
- Conversation sidebar
- New conversation button
- Typing indicator for streaming
- Markdown rendering for responses
- Code syntax highlighting

#### [NEW] **`packages/research-assistant/frontend/components/MessageBubble.tsx`**
**Summary:** Reusable message component
- User vs assistant styling
- Timestamp display
- Skill badge (if skill was used)
- Markdown rendering
- Copy button for code blocks

#### [NEW] **`packages/research-assistant/frontend/components/ConversationSidebar.tsx`**
**Summary:** Conversation list sidebar
- List of conversations with titles
- Active conversation indicator
- Delete conversation button
- Search conversations

---

## Implementation Strategy

### Day 1-2: Backend Foundation
1. Set up Claude API integration
2. Create conversation models and migrations
3. Implement ConversationService
4. Basic ClaudeService with mock responses

### Day 3-4: Skills Implementation
1. Implement Literature Search skill
2. Implement Data Analysis skill (query data platform)
3. Implement Property Prediction skill (call predictor)
4. Implement Synthesis Planning skill
5. Implement Material Recommendations skill

### Day 5-7: Chat API
1. Create chat endpoints
2. Integrate Claude with skills
3. Add streaming support
4. Error handling and validation

### Day 8-10: Frontend Chat UI
1. Create chat page layout
2. Message bubbles and list
3. Input box and send logic
4. Conversation sidebar
5. Markdown rendering

### Day 11-12: Polish & Testing
1. Streaming responses UI
2. Loading states
3. Error messages
4. Conversation management
5. Integration testing

### Day 13-14: Advanced Features
1. Conversation search
2. Export conversation
3. Suggested prompts
4. Rate limiting

---

## API Integrations

### External APIs
1. **Anthropic Claude API** - AI responses
   - Endpoint: `https://api.anthropic.com/v1/messages`
   - Model: `claude-3-5-sonnet-20241022`
   - Max tokens: 4096

2. **PubChem API** (optional)
   - Compound search by SMILES
   - Property data retrieval

3  **Lymeric Data Platform API**
   - Internal integration
   - Query materials for analysis

---

## Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...  # Required for Claude
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
CONVERSATION_LIMIT=50  # Max messages per conversation
```

---

## Dependencies

### Backend
```
anthropic==0.34.0      # Claude API client
markdown==3.5.1        # Markdown processing
beautifulsoup4==4.12.2 # HTML parsing (for literature)
requests==2.31.0       # HTTP requests
```

### Frontend
```
react-markdown==9.0.1   # Markdown rendering
react-syntax-highlighter==15.5.0  # Code highlighting
```

---

## Skills System Architecture

Each skill follows this pattern:
```python
class Skill:
    name: str
    description: str
    
    def can_handle(self, query: str) -> bool:
        """Determine if this skill should handle the query"""
        
    async def execute(self, query: str, context: dict) -> dict:
        """Execute the skill and return results"""
```

**Skill Router:**
- Analyzes user query
- Routes to appropriate skill
- Falls back to general Claude if no skill matches
- Combines skill results with Claude response

---

## Testing Plan

### Unit Tests
- ClaudeService: Mock API responses
- Skills: Mock external API calls
- ConversationService: Database operations

### Integration Tests
- Chat flow: Send message → Get response
- Skills integration: Trigger each skill
- Streaming: Verify chunked responses

### Manual Tests
1. Ask about a material → Property prediction skill
2. Request literature → Literature search skill
3. Analyze dataset → Data analysis skill
4. General question → Claude general knowledge
5. Conversation history → Context preservation

---

## Acceptance Criteria

✅ User can send messages and receive AI responses  
✅ Conversations are saved and retrievable  
✅ 5 skills work correctly:
  - Literature search finds relevant papers
  - Data analysis queries materials database
  - Property prediction uses ML model
  - Synthesis planning suggests routes
  - Material recommendations based on similarity
✅ Streaming responses show typing indicator  
✅ Markdown rendering with code highlighting  
✅ Error handling for API failures  
✅ Rate limiting prevents abuse  

---

## Timeline

**Total:** 14 days (Weeks 9-12 of 16-week plan)

- Days 1-2: Backend foundation
- Days 3-4: Skills implementation
- Days 5-7: Chat API
- Days 8-10: Frontend UI
- Days 11-12: Polish & testing
- Days 13-14: Advanced features

---

## Next: Phase 4 (Optional)

After Phase 3, consider:
- Deployment to cloud (AWS/GCP)
- User authentication
- Team collaboration
- Advanced analytics
- Custom ML model training
