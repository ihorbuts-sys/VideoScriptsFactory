"""Independent catalog reference UI; animation pixels never include the viewfinder."""
from pathlib import Path
import re


def attach(page,script):
    page=re.sub(r'<img class="(?:fixed-sights|sights)"[^>]*>','',page)
    page=re.sub(r'<script src="[^"]*guide-ui.js" defer></script>','',page)
    return page.replace('</html>',f'<script src="{script}" defer></script></html>')
