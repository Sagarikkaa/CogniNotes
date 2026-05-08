from transformers import pipeline
import torch


class SummarizerAgent:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):

        if not self._initialized:

            print("[SummarizerAgent] Loading BART model...")

            device = 0 if torch.cuda.is_available() else -1

            try:
                self.pipeline = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    device=device
                )
                self._output_key = "summary_text"
            except Exception:
                self.pipeline = pipeline(
                    "text-generation",
                    model="facebook/bart-large-cnn",
                    device=device
                )
                self._output_key = "generated_text"

            self._initialized = True

            print("[SummarizerAgent] Model ready.")

    def summarize(self, text, target_word_count=300):

        if not text.strip():
            raise ValueError("Empty text")

        result = self.pipeline(
            text,
            max_length=450,
            min_length=250,
            do_sample=False,
            truncation=True
        )

        summary = result[0].get(self._output_key, result[0].get("generated_text", ""))
        return self._truncate_to_word_count(summary, target_word_count)

    @staticmethod
    def _truncate_to_word_count(text, max_words):
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]).rstrip(".,;:!?") + "..."