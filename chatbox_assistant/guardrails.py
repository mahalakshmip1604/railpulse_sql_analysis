import re

def verify_user_input_safety(user_text: str) -> bool:
    """
    Layer 1 Guardrail (Pre-Inference)
    Blocks malicious engineering injection attempts before hitting the Cloud API.
    """
    normalized_input = user_text.lower()
    
    # Block destructive statements and structural metadata leaks
    # Modified 'update' and 'insert' to check for common explicit SQL mutation patterns
    blacklisted_patterns = [
        "drop table", "delete from", "update table", "update set", "insert into", 
        "alter table", "truncate table", "sqlite_master", "pragma ", "grant privilege"
    ]
    
    for pattern in blacklisted_patterns:
        if pattern in normalized_input:
            return False
            
    return True

def verify_generated_sql_safety(generated_sql: str) -> bool:
    """
    Layer 2 Guardrail (Post-Inference)
    Validates structural parameters of the query before permitting SQLite to execute it.
    """
    # Normalize input and strip optional trailing semicolons natively used by LLMs
    clean_sql = generated_sql.strip().lower()
    if clean_sql.endswith(";"):
        clean_sql = clean_sql[:-1].strip()
    
    # 1. Enforce that queries can only pull read-only tracking blocks
    if not (clean_sql.startswith("select") or clean_sql.startswith("with")):
        return False
        
    # 2. Block stacked multi-queries (detecting semicolons separating valid commands)
    if ";" in clean_sql:
        return False
        
    # 3. Exact word boundary analysis for mutation statements
    destructive_keywords = {"drop", "delete", "update", "insert", "alter", "truncate", "replace", "exec"}
    
    # Tokenize input blocks using regex boundaries
    tokens = re.findall(r'\b\w+\b', clean_sql)
    for token in tokens:
        # Avoid blocking queries targeting the 'stop_times_updates' table explicitly
        if token == "stop_times_updates":
            continue
        if token in destructive_keywords:
            return False
            
    return True
