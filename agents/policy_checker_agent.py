from typing import Dict, List
import re
import google.generativeai as genai
from config import settings


class PolicyCheckerAgent:
    """
    Agent responsible for checking policy answers for:
    - Contradictions across sources
    - Ambiguous language (may vs must)
    - Legal advice detection
    - Confidence scoring
    """

    def __init__(self):
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(settings.llm_model)
            self.use_llm = True
        else:
            self.use_llm = False

        # Modal verbs indicating certainty levels
        self.modal_verbs = {
            'must': 'high_certainty',
            'shall': 'high_certainty',
            'will': 'high_certainty',
            'required': 'high_certainty',
            'mandatory': 'high_certainty',
            'may': 'low_certainty',
            'might': 'low_certainty',
            'could': 'low_certainty',
            'should': 'medium_certainty',
            'recommended': 'medium_certainty'
        }

        # Legal advice indicators
        self.legal_indicators = [
            'legal action',
            'lawsuit',
            'sue',
            'attorney',
            'lawyer',
            'legal counsel',
            'court',
            'litigation'
        ]

    def check_policy(
        self,
        answer: str,
        retrieved_chunks: List[Dict],
        query: str
    ) -> Dict:
        """
        Perform comprehensive policy checking on the generated answer.

        Args:
            answer: Generated answer text
            retrieved_chunks: Chunks used to generate answer
            query: Original query

        Returns:
            Dictionary with checks and confidence score
        """
        checks = {
            'ambiguity_check': self._check_ambiguity(answer),
            'modal_verb_analysis': self._analyze_modal_verbs(answer),
            'legal_advice_check': self._check_legal_advice(answer, query),
            'confidence_score': 0.0,
            'warnings': [],
            'recommendations': []
        }

        # Check for contradictions using LLM if available
        if self.use_llm and len(retrieved_chunks) > 1:
            contradiction_check = self._check_contradictions_llm(
                answer, retrieved_chunks
            )
            checks['contradiction_check'] = contradiction_check
        else:
            checks['contradiction_check'] = self._check_contradictions_heuristic(
                retrieved_chunks
            )

        # Calculate overall confidence score
        checks['confidence_score'] = self._calculate_confidence(checks)

        # Generate warnings and recommendations
        checks['warnings'] = self._generate_warnings(checks)
        checks['recommendations'] = self._generate_recommendations(checks)

        return checks

    def _check_ambiguity(self, answer: str) -> Dict:
        """Check for ambiguous language in the answer."""
        ambiguous_phrases = [
            'it depends',
            'may or may not',
            'unclear',
            'ambiguous',
            'not specified',
            'consult',
            'contact',
            'check with'
        ]

        found_phrases = []
        for phrase in ambiguous_phrases:
            if phrase.lower() in answer.lower():
                found_phrases.append(phrase)

        return {
            'has_ambiguity': len(found_phrases) > 0,
            'ambiguous_phrases': found_phrases,
            'count': len(found_phrases)
        }

    def _analyze_modal_verbs(self, answer: str) -> Dict:
        """Analyze modal verbs to understand certainty level."""
        answer_lower = answer.lower()
        found_modals = {}

        for modal, certainty in self.modal_verbs.items():
            count = len(re.findall(r'\b' + modal + r'\b', answer_lower))
            if count > 0:
                found_modals[modal] = {
                    'count': count,
                    'certainty': certainty
                }

        # Determine overall certainty
        if not found_modals:
            overall_certainty = 'neutral'
        else:
            certainties = [v['certainty'] for v in found_modals.values()]
            if 'high_certainty' in certainties:
                overall_certainty = 'high'
            elif 'low_certainty' in certainties:
                overall_certainty = 'low'
            else:
                overall_certainty = 'medium'

        return {
            'modal_verbs': found_modals,
            'overall_certainty': overall_certainty
        }

    def _check_legal_advice(self, answer: str, query: str) -> Dict:
        """Check if the answer contains legal advice."""
        answer_lower = answer.lower()
        query_lower = query.lower()

        legal_terms_in_answer = [
            term for term in self.legal_indicators
            if term in answer_lower
        ]

        legal_terms_in_query = [
            term for term in self.legal_indicators
            if term in query_lower
        ]

        is_legal_advice = len(legal_terms_in_answer) > 0

        return {
            'is_legal_advice': is_legal_advice,
            'legal_terms_in_answer': legal_terms_in_answer,
            'legal_terms_in_query': legal_terms_in_query,
            'recommendation': 'Consult legal services office' if is_legal_advice else None
        }

    def _check_contradictions_heuristic(self, chunks: List[Dict]) -> Dict:
        """Simple heuristic check for contradictions between chunks."""
        if len(chunks) < 2:
            return {
                'has_contradictions': False,
                'confidence': 1.0
            }

        # Check if chunks come from different documents
        sources = set(chunk['metadata']['filename'] for chunk in chunks)

        return {
            'has_contradictions': False,
            'multiple_sources': len(sources) > 1,
            'source_count': len(sources),
            'sources': list(sources),
            'confidence': 0.8 if len(sources) > 1 else 1.0
        }

    def _check_contradictions_llm(self, answer: str, chunks: List[Dict]) -> Dict:
        """Use LLM to check for contradictions in retrieved content."""
        try:
            # Prepare chunks text
            chunks_text = "\n\n".join([
                f"Source {i+1} ({chunk['metadata']['filename']}, page {chunk['metadata']['page_number']}):\n{chunk['text']}"
                for i, chunk in enumerate(chunks[:5])  # Limit to first 5 chunks
            ])

            prompt = f"""You are a policy-checker assistant. Given an answer and its supporting snippets, detect if there are contradictions across snippets.

Answer: {answer}

Supporting snippets:
{chunks_text}

Analyze:
1. Are there contradictions between the snippets?
2. Do the snippets provide conflicting information?
3. Is the answer consistent with all snippets?

Respond in this format:
HAS_CONTRADICTIONS: [YES/NO]
CONFIDENCE: [0.0-1.0]
EXPLANATION: [brief explanation]"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=300,
                )
            )

            result_text = response.text

            # Parse response
            has_contradictions = 'YES' in result_text.split('\n')[0]
            confidence_line = [line for line in result_text.split('\n') if 'CONFIDENCE' in line]
            confidence = float(confidence_line[0].split(':')[1].strip()) if confidence_line else 0.7

            explanation_lines = [line for line in result_text.split('\n') if 'EXPLANATION' in line]
            explanation = explanation_lines[0].split(':', 1)[1].strip() if explanation_lines else ""

            return {
                'has_contradictions': has_contradictions,
                'confidence': confidence,
                'explanation': explanation
            }

        except Exception as e:
            print(f"Error checking contradictions with LLM: {e}")
            return self._check_contradictions_heuristic(chunks)

    def _calculate_confidence(self, checks: Dict) -> float:
        """Calculate overall confidence score based on all checks."""
        confidence = 1.0

        # Reduce confidence for ambiguity
        if checks['ambiguity_check']['has_ambiguity']:
            confidence -= 0.15 * checks['ambiguity_check']['count']

        # Reduce confidence for low certainty modal verbs
        if checks['modal_verb_analysis']['overall_certainty'] == 'low':
            confidence -= 0.2
        elif checks['modal_verb_analysis']['overall_certainty'] == 'medium':
            confidence -= 0.1

        # Reduce confidence for potential contradictions
        if checks['contradiction_check'].get('has_contradictions'):
            confidence -= 0.3

        # Reduce confidence for legal advice
        if checks['legal_advice_check']['is_legal_advice']:
            confidence -= 0.2

        # Keep confidence in valid range
        confidence = max(0.0, min(1.0, confidence))

        return round(confidence, 2)

    def _generate_warnings(self, checks: Dict) -> List[str]:
        """Generate warnings based on checks."""
        warnings = []

        if checks['ambiguity_check']['has_ambiguity']:
            warnings.append("This answer contains ambiguous language. Consider consulting official sources.")

        if checks['modal_verb_analysis']['overall_certainty'] == 'low':
            warnings.append("The policy contains language indicating flexibility or uncertainty.")

        if checks['contradiction_check'].get('has_contradictions'):
            warnings.append("Potential contradictions detected across source documents.")

        if checks['legal_advice_check']['is_legal_advice']:
            warnings.append("This topic may involve legal matters. Consult the legal services office.")

        if checks['confidence_score'] < 0.5:
            warnings.append("Low confidence answer. Please verify with official university office.")

        return warnings

    def _generate_recommendations(self, checks: Dict) -> List[str]:
        """Generate recommendations based on checks."""
        recommendations = []

        if checks['ambiguity_check']['has_ambiguity']:
            recommendations.append("Contact the relevant university department for clarification.")

        if checks['contradiction_check'].get('multiple_sources'):
            recommendations.append(f"This answer references {checks['contradiction_check']['source_count']} different policy documents. Review all sources for complete information.")

        if checks['legal_advice_check']['is_legal_advice']:
            recommendations.append("Speak with the university legal services office for legal matters.")

        return recommendations
