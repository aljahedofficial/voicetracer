"""
Text Preprocessor

Handles text cleaning, tokenization, sentence/paragraph segmentation.
Foundation for all metric calculations.
"""

import re
from typing import List, Dict, Any
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)


class TextPreprocessor:
    """
    Preprocesses text for AI detection metrics.
    
    Handles:
    - Sentence tokenization
    - Word tokenization
    - Paragraph segmentation
    - Lemmatization
    - Basic cleaning
    """
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
    
    def preprocess(self, text: str) -> Dict[str, Any]:
        """
        Full preprocessing pipeline.
        
        Args:
            text: Raw input text
            
        Returns:
            Dictionary containing:
            - raw_text: Original text
            - cleaned_text: Cleaned version
            - sentences: List of sentences
            - paragraphs: List of paragraphs
            - tokens: List of word tokens
            - lemmas: List of lemmatized tokens
            - word_count: Total word count
            - sentence_count: Total sentence count
            - paragraph_count: Total paragraph count
        """
        if not text or not text.strip():
            raise ValueError("Cannot preprocess empty text")
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Tokenize sentences
        sentences = self.tokenize_sentences(cleaned_text)
        
        # Tokenize paragraphs
        paragraphs = self.tokenize_paragraphs(text)
        
        # Tokenize words
        tokens = self.tokenize_words(cleaned_text)
        
        # Lemmatize
        lemmas = self.lemmatize_tokens(tokens)
        
        return {
            'raw_text': text,
            'cleaned_text': cleaned_text,
            'sentences': sentences,
            'paragraphs': paragraphs,
            'tokens': tokens,
            'lemmas': lemmas,
            'word_count': len(tokens),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs)
        }
    
    def clean_text(self, text: str) -> str:
        """
        Basic text cleaning.
        
        - Remove extra whitespace
        - Normalize line breaks
        - Keep punctuation (needed for sentence tokenization)
        """
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using NLTK.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        sentences = sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def tokenize_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.
        
        Args:
            text: Input text
            
        Returns:
            List of paragraphs
        """
        # Split on double line breaks or single line break followed by indent
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def tokenize_words(self, text: str) -> List[str]:
        """
        Split text into word tokens.
        
        Args:
            text: Input text
            
        Returns:
            List of word tokens (alphanumeric only)
        """
        tokens = word_tokenize(text)
        # Filter to alphanumeric tokens only
        return [t for t in tokens if t.isalpha()]
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize word tokens to base forms.
        
        Args:
            tokens: List of word tokens
            
        Returns:
            List of lemmatized tokens
        """
        return [self.lemmatizer.lemmatize(t.lower()) for t in tokens]
    
    def get_sentence_lengths(self, sentences: List[str]) -> List[int]:
        """
        Get word count for each sentence.
        
        Args:
            sentences: List of sentences
            
        Returns:
            List of word counts per sentence
        """
        return [len(self.tokenize_words(sent)) for sent in sentences]
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 0) -> List[str]:
        """
        Split text into fixed-size chunks by word count.
        
        Args:
            text: Input text
            chunk_size: Number of words per chunk
            overlap: Number of overlapping words between chunks
            
        Returns:
            List of text chunks
        """
        tokens = self.tokenize_words(text)
        chunks = []
        
        if len(tokens) <= chunk_size:
            return [text]
        
        step = chunk_size - overlap
        for i in range(0, len(tokens), step):
            chunk_tokens = tokens[i:i + chunk_size]
            if len(chunk_tokens) >= 50:  # Minimum chunk size
                chunks.append(' '.join(chunk_tokens))
        
        return chunks
    
    @staticmethod
    def validate_text_length(text: str, min_words: int = 100) -> bool:
        """
        Check if text meets minimum length requirement.
        
        Args:
            text: Input text
            min_words: Minimum word count required
            
        Returns:
            True if text is long enough, False otherwise
        """
        word_count = len(word_tokenize(text))
        return word_count >= min_words
    
    @staticmethod
    def get_text_stats(text: str) -> Dict[str, int]:
        """
        Get basic text statistics.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with character, word, sentence, paragraph counts
        """
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        alpha_words = [w for w in words if w.isalpha()]
        paragraphs = re.split(r'\n\s*\n', text)
        
        return {
            'character_count': len(text),
            'word_count': len(alpha_words),
            'sentence_count': len(sentences),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'avg_sentence_length': len(alpha_words) / len(sentences) if sentences else 0,
            'avg_paragraph_length': len(alpha_words) / len([p for p in paragraphs if p.strip()]) if paragraphs else 0
        }
