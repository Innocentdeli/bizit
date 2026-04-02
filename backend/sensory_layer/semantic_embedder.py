import numpy as np
from typing import Dict, Any, List
from .event_encoder import UnifiedEvent

class SemanticEmbedder:
    """
    Converts raw business events into semantic embeddings for AI processing.
    Uses sentence transformers or custom models to encode event context.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Load sentence transformer model for semantic encoding."""
        try:
            from sentence_transformers import SentenceTransformer
            # Level 11: Added timeout handling/offline fallback
            self.model = SentenceTransformer(self.model_name)
            print(f"[EMBEDDER] Loaded model: {self.model_name}")
        except Exception as e:
            print(f"[EMBEDDER] Model loading failed ({e}). Using fallback encoding.")
            self.model = None
    
    def encode_event(self, event: UnifiedEvent) -> np.ndarray:
        """
        Generate semantic embedding for an event.
        Returns a dense vector representation for similarity search and AI reasoning.
        """
        # Create textual representation of event
        event_text = self._event_to_text(event)
        
        if self.model:
            embedding = self.model.encode(event_text)
            return embedding
        else:
            # Fallback: Simple hash-based encoding
            return self._fallback_encoding(event_text)
    
    def _event_to_text(self, event: UnifiedEvent) -> str:
        """Convert event to natural language description."""
        payload_str = ", ".join([f"{k}: {v}" for k, v in event.payload.items()])
        return f"{event.source} reported {event.event_type} with {payload_str}"
    
    def _fallback_encoding(self, text: str) -> np.ndarray:
        """Simple fallback encoding using character-level hashing."""
        # Create a 384-dim vector (matching MiniLM output size)
        vector = np.zeros(384)
        for i, char in enumerate(text[:384]):
            vector[i] = ord(char) / 255.0
        return vector
    
    def batch_encode(self, events: List[UnifiedEvent]) -> np.ndarray:
        """Encode multiple events in batch for efficiency."""
        if self.model:
            texts = [self._event_to_text(e) for e in events]
            return self.model.encode(texts)
        else:
            return np.array([self._fallback_encoding(self._event_to_text(e)) for e in events])
    
    def find_similar_events(self, query_event: UnifiedEvent, event_pool: List[UnifiedEvent], top_k: int = 5) -> List[tuple]:
        """
        Find semantically similar events using cosine similarity.
        Returns: List of (event, similarity_score) tuples.
        """
        query_embedding = self.encode_event(query_event)
        pool_embeddings = self.batch_encode(event_pool)
        
        # Compute cosine similarities
        similarities = np.dot(pool_embeddings, query_embedding) / (
            np.linalg.norm(pool_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k most similar
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [(event_pool[i], similarities[i]) for i in top_indices]
