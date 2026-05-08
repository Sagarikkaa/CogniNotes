"""
Keyword Extraction Agent
Uses scikit-learn's TF-IDF (Term Frequency-Inverse Document Frequency)
to extract the most important keywords from user notes.

TF-IDF does NOT require a pre-trained model — it's a statistical method
that weighs words by how important they are relative to the document.
"""

from sklearn.feature_extraction.text import TfidfVectorizer


class KeywordAgent:
    """
    Agent responsible for extracting keywords from notes.
    
    Uses TF-IDF vectorization to identify the most significant
    terms in the input text. Returns the top N keywords sorted
    by their TF-IDF scores.
    
    Usage:
        agent = KeywordAgent()
        keywords = agent.extract_keywords("Your text here...")
    """

    def __init__(self):
        """Initialize the TF-IDF vectorizer with English stop words removed."""
        self.vectorizer = TfidfVectorizer(
            stop_words='english',  # Remove common English words (the, is, at...)
            max_features=1000,     # Consider top 1000 terms
            ngram_range=(1, 2),    # Include single words and 2-word phrases
        )

    def extract_keywords(self, text, top_n=10):
        """
        Extract the top N keywords from the input text.
        
        Args:
            text (str):  The text to extract keywords from.
            top_n (int): Number of top keywords to return (default: 10).
            
        Returns:
            list[str]: A list of the most important keywords/phrases.
            
        Raises:
            ValueError: If text is empty.
        """
        # Validate input
        if not text or not text.strip():
            raise ValueError("Cannot extract keywords from empty text.")

        try:
            # TF-IDF needs a list of documents — we pass a single document
            tfidf_matrix = self.vectorizer.fit_transform([text])

            # Get feature names (the actual words/phrases)
            feature_names = self.vectorizer.get_feature_names_out()

            # Get TF-IDF scores for each term
            scores = tfidf_matrix.toarray()[0]

            # Pair each word with its score and sort by score (descending)
            scored_keywords = sorted(
                zip(feature_names, scores),
                key=lambda x: x[1],
                reverse=True
            )

            # Return only the top N keyword strings
            keywords = [word for word, score in scored_keywords[:top_n]]

            # Filter out very short or meaningless terms
            keywords = [kw for kw in keywords if len(kw) > 1]

            return keywords if keywords else ['No significant keywords found']

        except Exception as e:
            raise RuntimeError(f"Keyword extraction failed: {str(e)}")
