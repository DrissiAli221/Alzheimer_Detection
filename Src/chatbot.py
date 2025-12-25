"""
Alzheimer's Disease Chatbot Module
Uses Google Gemini API to provide FAQ, result explanation, and guidance.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# System prompt with Alzheimer's knowledge
SYSTEM_PROMPT = """You are a helpful, empathetic AI assistant specialized in Alzheimer's disease education and support. 
You are integrated into an MRI-based Alzheimer's detection application.

Your capabilities:
1. **Educational Support**: Answer questions about Alzheimer's disease, its stages, symptoms, risk factors, and treatments.
2. **Result Explanation**: When the user has received a prediction, help explain what it means in simple terms.
3. **Guidance**: Provide appropriate next steps and resources, always recommending professional medical consultation.

Important guidelines:
- Be compassionate and sensitive - users may be worried about themselves or loved ones
- Always clarify that you are an AI assistant, not a medical professional
- Never provide definitive diagnoses - the model predictions are for informational purposes only
- Encourage users to consult healthcare professionals for proper diagnosis and treatment
- Keep responses concise but informative
- Use simple, accessible language

The prediction classes in this app are:
- **Non-demented**: No signs of Alzheimer's disease detected in the MRI scan
- **Very Mild Alzheimer's**: Early signs of cognitive decline, often difficult to distinguish from normal aging
- **Mild Alzheimer's**: Noticeable memory problems and cognitive difficulties
- **Moderate Alzheimer's**: Significant memory loss and difficulty with daily activities

When explaining results, be supportive and provide context about what the classification means and what steps might be appropriate."""


class AlzheimerChatbot:
    """Chatbot for Alzheimer's disease education and result explanation."""
    
    def __init__(self):
        """Initialize the chatbot with Gemini API."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        self.chat_history = []
        self.last_prediction = None
        self.last_probabilities = None
    
    def set_prediction_context(self, prediction_label: str, probabilities: dict):
        """Store the latest prediction for context-aware responses."""
        self.last_prediction = prediction_label
        self.last_probabilities = probabilities
    
    def clear_prediction_context(self):
        """Clear the stored prediction context."""
        self.last_prediction = None
        self.last_probabilities = None
    
    def _build_context(self) -> str:
        """Build context string including prediction if available."""
        context = SYSTEM_PROMPT
        
        if self.last_prediction:
            context += f"\n\n**Current User Context:**\nThe user has just received a prediction result: **{self.last_prediction}**"
            if self.last_probabilities:
                context += "\nProbability breakdown:"
                for label, prob in self.last_probabilities.items():
                    context += f"\n- {label}: {prob:.1%}"
        
        return context
    
    def get_response(self, user_message: str) -> str:
        """Get a response from the chatbot."""
        try:
            # Build the full prompt with context
            context = self._build_context()
            
            # Add chat history for conversation continuity
            history_text = ""
            for msg in self.chat_history[-6:]:  # Keep last 6 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                history_text += f"\n{role}: {msg['content']}"
            
            full_prompt = f"""{context}

{f"Previous conversation:{history_text}" if history_text else ""}

User: {user_message}

Please provide a helpful, empathetic response:"""
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            assistant_message = response.text
            
            # Update chat history
            self.chat_history.append({"role": "user", "content": user_message})
            self.chat_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def explain_result(self) -> str:
        """Generate an explanation of the current prediction result."""
        if not self.last_prediction:
            return "I don't have any prediction results to explain yet. Please upload an MRI scan first."
        
        prompt = f"""The user has just received a prediction of **{self.last_prediction}** from the Alzheimer's detection model.

Probability breakdown:
{chr(10).join([f"- {label}: {prob:.1%}" for label, prob in (self.last_probabilities or {}).items()])}

Please provide:
1. A clear, compassionate explanation of what this result means
2. Important context about the limitations of AI-based predictions
3. Recommended next steps
4. Words of support and encouragement

Keep the response warm, supportive, and around 150-200 words."""
        
        try:
            response = self.model.generate_content(prompt)
            explanation = response.text
            
            # Add to chat history
            self.chat_history.append({"role": "user", "content": "Can you explain my result?"})
            self.chat_history.append({"role": "assistant", "content": explanation})
            
            return explanation
        except Exception as e:
            return f"I apologize, but I couldn't generate an explanation: {str(e)}"
    
    def get_next_steps(self) -> str:
        """Provide guidance on next steps based on the prediction."""
        if not self.last_prediction:
            return "Please upload an MRI scan first to receive personalized guidance."
        
        prompt = f"""Based on a prediction of **{self.last_prediction}**, provide clear, actionable next steps the user should consider.

Include:
1. Immediate actions they might take
2. Healthcare professionals to consult
3. Resources for more information
4. Support options for the user and caregivers if applicable

Be supportive and practical. Keep response to about 150 words."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I couldn't generate next steps: {str(e)}"
    
    def clear_history(self):
        """Clear the conversation history."""
        self.chat_history = []
    
    def get_faq_topics(self) -> list:
        """Return common FAQ topics for quick access."""
        return [
            "What is Alzheimer's disease?",
            "What are the early warning signs?",
            "How is Alzheimer's diagnosed?",
            "What treatments are available?",
            "How can I support a loved one?",
            "What lifestyle changes can help?",
        ]
