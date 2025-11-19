"""Mock Claude service for research assistant (no API key required)"""
from typing import List, Dict, Optional
import random
import time


class MockClaudeService:
    """
    Mock Claude service that simulates AI responses without requiring an API key.
    
    In production, replace with real ClaudeService that calls Anthropic API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize mock service. API key is ignored in mock mode."""
        self.api_key = api_key
        self.is_mock = True
        
        # Predefined responses for different query types
        self.responses = {
            "greeting": [
                "Hello! I'm your materials research assistant. I can help you with literature search, data analysis, property predictions, synthesis planning, and material recommendations. What would you like to explore today?",
                "Hi there! I'm here to assist with your materials research. Whether you need property predictions, synthesis routes, or data analysis, I'm ready to help. What can I do for you?"
            ],
            "property_prediction": [
                "Based on the SMILES structure provided, I can help predict material properties. The prediction shows favorable thermal and mechanical characteristics. Would you like me to provide detailed analysis of specific properties?",
                "I've analyzed the molecular structure. The predicted glass transition temperature suggests good thermal stability, and the free volume fraction indicates suitable permeability characteristics."
            ],
            "data_analysis": [
                "I've analyzed the materials database. The dataset shows interesting trends in the relationship between glass transition temperature and density. Materials with higher crystallinity tend to exhibit more predictable thermal behavior.",
                "Looking at the current dataset, I notice several outliers in the FFV (Free Volume Fraction) measurements. These could indicate either measurement errors or genuinely unique material properties worth investigating further."
            ],
            "literature": [
                "I found several relevant papers on polymer glass transition behavior. Key publications include recent work on structure-property relationships in amorphous polymers and computational prediction methods.",
                "The literature suggests that the relationship between molecular weight and Tg is well-established for linear polymers, but branched structures show more complex behavior."
            ],
            "synthesis": [
                "For synthesizing this polymer, I recommend a free radical polymerization approach. Key steps would include: 1) Monomer purification, 2) Initiator selection (AIBN at 60-80°C), 3) Controlled atmosphere (N2 or Ar), and 4) Temperature monitoring.",
                "The synthesis route I suggest involves ring-opening polymerization. This method offers better control over molecular weight distribution and can achieve higher yields compared to traditional approaches."
            ],
            "recommendation": [
                "Based on the target properties (high Tg, low density), I recommend exploring polycarbonates or polyimides. These materials typically exhibit excellent thermal stability while maintaining reasonable processability.",
                "Materials similar to your query include polystyrene derivatives and certain polyacrylates. I can provide detailed comparisons if you'd like to see specific property values."
            ],
            "general": [
                "That's an interesting question! In materials science, we often balance competing properties - improving one characteristic can affect others. Could you provide more details about your specific application requirements?",
                "I can help with that! Materials research involves understanding structure-property relationships. What specific aspect would you like to focus on - thermal properties, mechanical behavior, or processing conditions?"
            ]
        }
    
    def send_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        skill_context: Optional[Dict] = None
    ) -> str:
        """
        Simulate sending a message to Claude and getting a response.
        
        Args:
            message: User's message
            conversation_history: Previous messages for context
            skill_context: Results from skill execution, if any
            
        Returns:
            Simulated AI response
        """
        # Simulate API latency
        time.sleep(0.5)
        
        # If skill context provided, incorporate it
        if skill_context:
            skill_name = skill_context.get('skill_name', '')
            if skill_name == 'property_prediction':
                return self._get_response('property_prediction')
            elif skill_name == 'data_analysis':
                return self._get_response('data_analysis')
            elif skill_name == 'literature_search':
                return self._get_response('literature')
            elif skill_name == 'synthesis_planning':
                return self._get_response('synthesis')
            elif skill_name == 'material_recommendations':
                return self._get_response('recommendation')
        
        # Detect query type from message content
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            response_type = 'greeting'
        elif any(word in message_lower for word in ['predict', 'prediction', 'property', 'tg', 'ffv']):
            response_type = 'property_prediction'
        elif any(word in message_lower for word in ['analyze', 'analysis', 'dataset', 'statistics']):
            response_type = 'data_analysis'
        elif any(word in message_lower for word in ['paper', 'literature', 'research', 'publication']):
            response_type = 'literature'
        elif any(word in message_lower for word in ['synthesis', 'synthesize', 'make', 'prepare']):
            response_type = 'synthesis'
        elif any(word in message_lower for word in ['recommend', 'similar', 'alternative', 'suggest']):
            response_type = 'recommendation'
        else:
            response_type = 'general'
        
        return self._get_response(response_type)
    
    def _get_response(self, response_type: str) -> str:
        """Get a random response for the given type"""
        responses = self.responses.get(response_type, self.responses['general'])
        return random.choice(responses)
    
    def stream_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        skill_context: Optional[Dict] = None
    ):
        """
        Simulate streaming response (for future implementation).
        
        Yields response chunks to simulate real-time streaming.
        """
        response = self.send_message(message, conversation_history, skill_context)
        
        # Simulate streaming by yielding words
        words = response.split(' ')
        for word in words:
            time.sleep(0.05)  # Simulate typing delay
            yield word + ' '
