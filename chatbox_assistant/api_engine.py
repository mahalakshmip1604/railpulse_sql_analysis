# chatbox_assistant/api_engine.py
import os
from groq import Groq
from .database_schema import STRUCTURED_SYSTEM_PROMPT

class CloudSQLRouter:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Configuration Error: GROQ_API_KEY environment variable missing.")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile" 

    def generate_sql_query(self, user_question: str) -> str:
        """Dispatches parameters to Groq infrastructure with correct syntax parsing."""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": STRUCTURED_SYSTEM_PROMPT},
                    {"role": "user", "content": user_question}
                ],
                model=self.model,
                temperature=0.0, 
                max_tokens=600
            )
            
            # ─── FIXED LINE ───
            # Properly access the first choice index element, then grab message.content
            raw_response = chat_completion.choices[0].message.content.strip()
            
            # Post-processing normalization
            clean_response = raw_response.replace("```sql", "").replace("```", "").strip()
            return clean_response
            
        except Exception as api_error:
            return f"ERROR: Infrastructure failure on API layer. Trace: {str(api_error)}"
