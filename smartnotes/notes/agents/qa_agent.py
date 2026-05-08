"""
Question Answering Agent
Uses distilbert-base-uncased-distilled-squad from HuggingFace Transformers
to answer user questions based on the provided note context.

Uses direct model loading (AutoModelForQuestionAnswering) instead of pipeline()
to avoid task-name compatibility issues across transformers versions.
"""

import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering


class QAAgent:
    """
    Agent responsible for answering questions about notes.

    Uses DistilBERT fine-tuned on SQuAD — a lightweight but powerful
    extractive question answering model that finds the answer span
    within the given context.

    Usage:
        agent = QAAgent()
        answer = agent.answer(question="What is X?", context="X is...")
    """

    _instance = None  # Singleton instance for model reuse

    def __new__(cls):
        """
        Singleton pattern: ensures the DistilBERT model is loaded
        only once during the application lifecycle.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Load the QA model only on first init."""
        if not self._initialized:
            print("[QAAgent] Loading distilbert-base-uncased-distilled-squad model...")

            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model_name = "distilbert-base-uncased-distilled-squad"

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForQuestionAnswering.from_pretrained(model_name).to(self.device)
            self.model.eval()

            self._initialized = True
            print("[QAAgent] Model loaded successfully!")

    def answer(self, question, context):
        """
        Answer a question based on the given context.

        Args:
            question (str): The question to answer.
            context (str):  The note text to search for the answer.

        Returns:
            dict: Contains 'answer' (str) and 'confidence' (float).

        Raises:
            ValueError: If question or context is empty.
        """
        # Validate inputs
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")
        if not context or not context.strip():
            raise ValueError("Context (note text) cannot be empty.")

        try:
            # Tokenize
            inputs = self.tokenizer(
                question.strip(),
                context.strip(),
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)

            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Get the most likely answer span
            start_logits = outputs.start_logits
            end_logits = outputs.end_logits

            # Calculate confidence via softmax
            start_probs = torch.softmax(start_logits, dim=-1)
            end_probs = torch.softmax(end_logits, dim=-1)

            start_idx = torch.argmax(start_logits, dim=-1).item()
            end_idx = torch.argmax(end_logits, dim=-1).item()

            # Ensure valid span
            if end_idx < start_idx:
                end_idx = start_idx

            confidence = (start_probs[0, start_idx] * end_probs[0, end_idx]).item()

            # Decode the answer tokens
            answer_tokens = inputs["input_ids"][0][start_idx:end_idx + 1]
            answer = self.tokenizer.decode(answer_tokens, skip_special_tokens=True).strip()

            if confidence < 0.01 or not answer:
                return {
                    'answer': 'No confident answer found in the provided notes.',
                    'confidence': round(confidence, 4)
                }

            return {
                'answer': answer,
                'confidence': round(confidence, 4)
            }
        except Exception as e:
            raise RuntimeError(f"Question answering failed: {str(e)}")
