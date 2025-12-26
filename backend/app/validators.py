"""
Input validation and edge case handling
"""
import re
from typing import Optional, Tuple

class InputValidator:
    """Validates and sanitizes user input for edge cases"""

    # Medical/Insurance keywords for relevance checking
    MEDICAL_KEYWORDS = {
        'insurance', 'coverage', 'policy', 'procedure', 'treatment',
        'claim', 'denial', 'reimbursement', 'prior authorization',
        'cpt', 'icd', 'diagnosis', 'medical', 'surgery', 'hospital',
        'doctor', 'physician', 'patient', 'healthcare', 'uhc',
        'united', 'health', 'provider', 'benefit', 'eligibility',
        'copay', 'deductible', 'coinsurance', 'out-of-pocket',
        'network', 'formulary', 'prescription', 'drug', 'medication',
        'bariatric', 'orthopedic', 'cardiology', 'oncology',
        'genetic', 'testing', 'imaging', 'mri', 'ct', 'scan',
        'therapy', 'rehabilitation', 'durable', 'equipment', 'dme'
    }

    # Injection attack patterns to block
    DANGEROUS_PATTERNS = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'DROP TABLE',
        r'SELECT \*',
        r'UNION SELECT',
        r'; DELETE',
        r'exec\(',
        r'eval\(',
    ]

    @staticmethod
    def sanitize_input(question: str) -> str:
        """
        Sanitize user input to prevent injection attacks

        Args:
            question: Raw user input

        Returns:
            Sanitized question

        Raises:
            ValueError: If input is too long or contains dangerous patterns
        """
        # Remove leading/trailing whitespace
        question = question.strip()

        # Check length
        if len(question) > 500:
            raise ValueError(
                "Question too long (maximum 500 characters). "
                "Please rephrase your question more concisely."
            )

        if len(question) < 5:
            raise ValueError(
                "Question too short (minimum 5 characters). "
                "Please provide more details."
            )

        # Check for dangerous patterns
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, question, re.IGNORECASE):
                raise ValueError(
                    "Invalid input detected. Please rephrase your question."
                )

        # Remove excessive whitespace
        question = re.sub(r'\s+', ' ', question)

        return question

    @staticmethod
    def is_medical_question(question: str) -> Tuple[bool, float]:
        """
        Check if question is medical/insurance related

        Args:
            question: User's question

        Returns:
            Tuple of (is_medical, relevance_score)
            - is_medical: True if question is medical/insurance related
            - relevance_score: Confidence score (0.0 to 1.0)
        """
        question_lower = question.lower()

        # Count matching keywords
        matches = sum(
            1 for keyword in InputValidator.MEDICAL_KEYWORDS
            if keyword in question_lower
        )

        # Calculate relevance score
        # At least 1 match = relevant
        # 3+ matches = highly relevant
        relevance_score = min(matches / 3.0, 1.0)
        is_medical = matches >= 1

        return is_medical, relevance_score

    @staticmethod
    def extract_provider(question: str) -> Optional[str]:
        """
        Extract insurance provider from question if mentioned

        Args:
            question: User's question

        Returns:
            Provider name (e.g., 'UHC', 'AETNA') or None
        """
        question_lower = question.lower()

        # Provider patterns
        provider_patterns = {
            'UHC': ['uhc', 'united healthcare', 'unitedhealthcare', 'united health'],
            'AETNA': ['aetna'],
            'CIGNA': ['cigna'],
            'BCBS': ['blue cross', 'bcbs', 'blue shield'],
            'HUMANA': ['humana'],
        }

        for provider, patterns in provider_patterns.items():
            for pattern in patterns:
                if pattern in question_lower:
                    return provider

        return None

    @staticmethod
    def validate_and_prepare(question: str, provider: Optional[str] = None) -> dict:
        """
        Complete validation and preparation pipeline

        Args:
            question: Raw user input
            provider: Optional provider override

        Returns:
            Dictionary with:
            - question: Sanitized question
            - provider: Detected or default provider
            - is_relevant: Whether question is medical/insurance related
            - relevance_score: Confidence score
            - warnings: List of warning messages

        Raises:
            ValueError: If input is invalid
        """
        warnings = []

        # Step 1: Sanitize
        try:
            sanitized_question = InputValidator.sanitize_input(question)
        except ValueError as e:
            raise ValueError(f"Invalid input: {str(e)}")

        # Step 2: Check relevance
        is_medical, relevance_score = InputValidator.is_medical_question(
            sanitized_question
        )

        if not is_medical:
            warnings.append(
                "Your question doesn't appear to be about insurance policies. "
                "I can only answer questions about UHC insurance coverage."
            )

        if relevance_score < 0.3:
            warnings.append(
                "Your question might be too general. "
                "Try asking about specific procedures or coverage criteria."
            )

        # Step 3: Detect provider if not specified
        if not provider:
            detected_provider = InputValidator.extract_provider(sanitized_question)
            provider = detected_provider or "UHC"  # Default to UHC
        else:
            provider = provider.upper()

        # Step 4: Return prepared data
        return {
            'question': sanitized_question,
            'provider': provider,
            'is_relevant': is_medical,
            'relevance_score': relevance_score,
            'warnings': warnings
        }
