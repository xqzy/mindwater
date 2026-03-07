import re

def parse_capture_text(text: str):
    # Strip common email signatures (e.g., starting with '--')
    main_content = text.split('\n--')[0].strip()
    
    # Extract tags (#tag) and contexts (@context)
    tags = re.findall(r'#\w+', main_content)
    contexts = re.findall(r'@\w+', main_content)
    
    # Clean raw text by removing tags and contexts
    clean_text = main_content
    for tag in tags:
        clean_text = clean_text.replace(tag, '')
    for context in contexts:
        clean_text = clean_text.replace(context, '')
    
    return {
        'text': clean_text.strip(),
        'tags': tags,
        'contexts': contexts
    }
