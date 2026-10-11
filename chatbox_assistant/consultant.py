import os
from groq import Groq

class RailPulseConsultant:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Configuration Error: GROQ_API_KEY environment variable missing.")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def format_seconds_to_minutes(self, data_rows, columns):
        """Systematically converts any raw delay tracking metrics from seconds to minutes."""
        formatted_rows = []
        
        # Locate indices of delay metrics columns to execute conversion math
        delay_indices = [i for i, col in enumerate(columns) if "delay" in col.lower()]
        
        # If no delay columns exist, bypass math entirely for latency reduction
        if not delay_indices:
            return data_rows
            
        for row in data_rows:
            new_row = list(row)
            row_len = len(new_row)
            
            for idx in delay_indices:
                # Boundary check safeguard to prevent structural IndexError mutations
                if idx < row_len and new_row[idx] is not None:
                    try:
                        # Convert float metrics to minutes cleanly rounded to two decimal places
                        new_row[idx] = round(float(new_row[idx]) / 60.0, 2)
                    except (ValueError, TypeError):
                        # Graceful handling of unparseable raw values
                        pass
                        
            formatted_rows.append(tuple(new_row))
            
        return formatted_rows

    def generate_tactical_recommendation(self, user_query, columns, processed_data):
        """Acts as a senior transit operations advisor to deliver tactical pipeline briefs."""
        
        # FIX: Pass only a small 5-row sample slice to the LLM to safeguard the token budget
        llm_data_slice = processed_data[:5]
        total_records_found = len(processed_data)
        
        data_summary = (
            f"Columns: {columns}\n"
            f"Total Matching Database Rows Found: {total_records_found}\n"
            f"Sample Rows (First 5 records): {llm_data_slice}"
        )
        
        consultant_prompt = f"""
        You are a highly analytical transit coordinator acting as a RailPulse Operations Consultant.
        A user asked the following question regarding network telemetry data: "{user_query}"
        
        Here is the validated database result summary associated with their tracking query:
        {data_summary}
        
        Tasks:
        1. Give a direct, concise 1-2 sentence human-readable summary of what the data indicates. Ensure you state any metrics clearly in minutes.
        2. Provide a specific, actionable 1-2 sentence tactical recommendation for railway operators (e.g., suggest track reassignments, maintenance inspections for structural platform bottlenecks, signaling timing checks, or crew deployment updates).
        
        Tone: Professional, direct, authoritative. Do not echo boilerplate introductory text. Get straight to the analysis.
        """

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": consultant_prompt}],
                model=self.model,
                temperature=0.3,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Consulting Synthesis Error: Failed to generate tactical advice. Trace: {str(e)}"
