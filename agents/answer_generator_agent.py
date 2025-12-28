from typing import Dict, List
import google.generativeai as genai
from config import settings


class AnswerGeneratorAgent:
    """
    Agent responsible for generating answers using RAG.
    Takes retrieved context and generates citation-backed answers.
    Uses Google Gemini API (free tier).
    """

    def __init__(self):
        if not settings.google_api_key:
            raise ValueError("Google API key not configured")

        # Configure Google Gemini
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.llm_model)
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.max_tokens

    def generate_answer(
        self,
        query: str,
        context: str,
        citations: List[Dict]
    ) -> Dict:
        """
        Generate an answer to the query based on retrieved context.

        Args:
            query: User's question
            context: Formatted context from retrieved chunks
            citations: Citation information

        Returns:
            Dictionary with answer, citations, and metadata
        """
        prompt = self._create_prompt(query, context)

        try:
            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )

            answer_text = response.text

            # Extract summary and detailed parts
            summary, detailed = self._parse_answer(answer_text)

            # Count tokens (approximate)
            tokens_used = len(prompt.split()) + len(answer_text.split())

            return {
                'answer': answer_text,
                'summary': summary,
                'detailed_answer': detailed,
                'citations': citations,
                'model': settings.llm_model,
                'tokens_used': tokens_used
            }

        except Exception as e:
            return {
                'answer': f"Error generating answer: {str(e)}",
                'citations': citations,
                'error': str(e)
            }

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM."""
        return """You are a helpful assistant that answers questions about university policies and regulations.

Your responsibilities:
1. Answer questions ONLY using the provided document snippets
2. First provide a clear, direct summary in your own words that directly addresses the question
3. Then provide detailed information with explicit inline citations in the format: (filename — page X, para Y)
4. If the answer is not contained in the snippets, respond: "I don't know — please consult the official office" and suggest the appropriate office to contact
5. Be precise and legally accurate
6. Quote relevant policy text when appropriate
7. If information is ambiguous or contradictory, clearly state this

Guidelines:
- Start with a concise summary that directly answers the user's question
- Then provide supporting details with citations
- Always cite your sources inline
- Use professional, clear language
- Never make assumptions beyond the provided text
- If unsure, acknowledge uncertainty

Response Format:
[Brief summary in your own words addressing the question]

[Detailed explanation with citations and relevant policy quotes]"""

    def _create_prompt(self, query: str, context: str) -> str:
        """Create the full prompt with system instructions, context, and query."""
        system_prompt = self._get_system_prompt()

        return f"""{system_prompt}

Use ONLY the provided snippets below to answer the question. Each snippet includes metadata in this format:
[DOC: {{filename}} | page: {{page}} | paragraph: {{p}}]

IMPORTANT: Structure your answer as follows:
1. Start with a clear, concise summary (2-3 sentences) in your own words that directly answers: "{query}"
2. Then provide detailed information with citations inline like: (filename — page X, para Y)

Snippets:
--- SNIPPETS START ---
{context}
--- SNIPPETS END ---

Question: {query}

Answer:"""

    def _parse_answer(self, answer_text: str) -> tuple:
        """
        Parse answer to extract summary and detailed parts.

        Args:
            answer_text: Full answer text

        Returns:
            Tuple of (summary, detailed_answer)
        """
        # Split by double newline to separate summary from details
        parts = answer_text.split('\n\n', 1)

        if len(parts) == 2:
            summary = parts[0].strip()
            detailed = parts[1].strip()
        else:
            # If no clear separation, use first paragraph as summary
            paragraphs = answer_text.split('\n')
            summary = paragraphs[0].strip()
            detailed = '\n'.join(paragraphs[1:]).strip() if len(paragraphs) > 1 else answer_text

        return summary, detailed

    def generate_followup_questions(self, query: str, answer: str) -> List[str]:
        """
        Generate relevant follow-up questions based on the answer.

        Args:
            query: Original query
            answer: Generated answer

        Returns:
            List of follow-up questions
        """
        try:
            prompt = f"""Based on this Q&A about university policies, suggest 3 relevant follow-up questions a student might ask:

Question: {query}
Answer: {answer}

Generate 3 short, specific follow-up questions (one per line):"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=200,
                )
            )

            followup_text = response.text
            questions = [q.strip() for q in followup_text.split('\n') if q.strip() and any(c in q for c in '?')]

            # Remove numbering if present
            questions = [q.lstrip('0123456789.)-• ') for q in questions]

            return questions[:3]

        except Exception as e:
            print(f"Error generating follow-up questions: {e}")
            return []
