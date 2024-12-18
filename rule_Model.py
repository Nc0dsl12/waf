import re

rulesDeF = load_cvs_dataset(input_dataset)
txtLabel = ruleDeF[payload_label]
txtText = ruleDeF[payload_col_name]

rules = {
    'sql_injection': re.compile(r'(union|select|insert|delete|update|drop|alter).*', re.IGNORECASE),
    'xss_attack': re.compile(r'(<script>|<iframe>).*', re.IGNORECASE),
    'path_traversal': re.compile(r'(\.\./|\.\.).*', re.IGNORECASE)
}