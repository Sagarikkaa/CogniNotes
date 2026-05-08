"""
Orchestrator Agent (Controller)
Central coordinator that routes user requests to the appropriate
specialized agent (Summarizer, QA, or Keyword Extractor).

This agent acts as the single entry point for all AI processing,
ensuring clean separation of concerns and modular architecture.
"""

from .summarizer import SummarizerAgent
from .qa_agent import QAAgent
from .keyword_agent import KeywordAgent


class OrchestratorAgent:
    

    def __init__(self):
        """
        Initialize all sub-agents.
        Note: Summarizer and QA agents use singleton pattern,
        so models are loaded only once even with multiple orchestrator instances.
        """
        self.summarizer = SummarizerAgent()
        self.qa_agent = QAAgent()
        self.keyword_agent = KeywordAgent()

    def process_request(self, input_text, action, question=None):
        """
        Route a request to the appropriate agent and return the result.
        
        Args:
            input_text (str): The note text to process.
            action (str):     One of 'summarize', 'keywords', or 'qa'.
            question (str):   Required when action is 'qa' — the user's question.
            
        Returns:
            dict: JSON-serializable response with keys:
                - 'status': 'success' or 'error'
                - 'action': the action that was performed
                - 'result': the output data (varies by action)
                
        Raises:
            ValueError: If action is invalid or required params are missing.
        """
        # Validate common input
        if not input_text or not input_text.strip():
            return {
                'status': 'error',
                'action': action,
                'result': 'Please provide some note text to process.'
            }

        # ---- Route to the correct agent ----

        if action == 'summarize':
            return self._handle_summarize(input_text)

        elif action == 'keywords':
            return self._handle_keywords(input_text)

        elif action == 'qa':
            return self._handle_qa(input_text, question)

        else:
            return {
                'status': 'error',
                'action': action,
                'result': f'Unknown action: "{action}". Use "summarize", "keywords", or "qa".'
            }

    def _handle_summarize(self, text):
        """Delegate to the SummarizerAgent."""
        try:
            summary = self.summarizer.summarize(text)
            return {
                'status': 'success',
                'action': 'summarize',
                'result': summary
            }
        except Exception as e:
            return {
                'status': 'error',
                'action': 'summarize',
                'result': str(e)
            }

    def _handle_keywords(self, text):
        """Delegate to the KeywordAgent."""
        try:
            keywords = self.keyword_agent.extract_keywords(text)
            return {
                'status': 'success',
                'action': 'keywords',
                'result': keywords
            }
        except Exception as e:
            return {
                'status': 'error',
                'action': 'keywords',
                'result': str(e)
            }

    def _handle_qa(self, context, question):
        """Delegate to the QAAgent."""
        if not question or not question.strip():
            return {
                'status': 'error',
                'action': 'qa',
                'result': 'Please provide a question to answer.'
            }
        try:
            qa_result = self.qa_agent.answer(
                question=question,
                context=context
            )
            return {
                'status': 'success',
                'action': 'qa',
                'result': qa_result
            }
        except Exception as e:
            return {
                'status': 'error',
                'action': 'qa',
                'result': str(e)
            }
