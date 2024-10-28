import re

def clean_text(content):
    # Step 1: Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Step 2: Replace newlines (\n) and tabs (\t) with spaces
    content = content.replace('\n', ' ').replace('\t', ' ')
    
    # Step 3: Replace multiple spaces with a single space
    content = re.sub(r'\s+', ' ', content)
    
    # Step 4: Remove leading/trailing whitespace
    content = content.strip()
    
    return content

# Example usage
raw_content = """
    <html><body><p>This is some content.\n</p> <p>Here is a tab:\tAnd some more content</p></body></html>
"""

cleaned_content = clean_text(raw_content)
print(cleaned_content)
