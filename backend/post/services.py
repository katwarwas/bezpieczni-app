import re
    
def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)



