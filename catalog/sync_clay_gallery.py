"""Keep the main animation gallery on the reviewed image-driven scene revision."""
import hashlib,html,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent

def apply(text):
    manifest=HERE/'clay-scenes/active-revisions.json'
    if not manifest.exists():return text
    records=json.loads(manifest.read_text())['guides']
    intro='<p id="clay-reconstruction-proof"><strong>New image-driven Blender scenes:</strong> <a href="clay-scenes/index.html">Play full color and ghost versions</a> · <a href="../model_refferences/objects/reconstructed.html">Reconstructed model library</a>. The bar guide is a complete connected replacement; the coffee orbit remains a base-shot proof.</p>'
    if 'id="clay-reconstruction-proof"' in text:text=re.sub(r'<p id="clay-reconstruction-proof">.*?</p>',intro,text,count=1,flags=re.S)
    else:text=text.replace('<h1>Live guide animations</h1>','<h1>Live guide animations</h1>'+intro,1)
    for gid,row in records.items():
        if not row['reviewed']:continue
        folder=Path(row['folder']).relative_to('catalog').as_posix();version=row['files']['ghost.png'][:12]
        pattern=r'<article class="guide" id="'+re.escape(gid)+r'".*?</article>'
        match=re.search(pattern,text,re.S)
        if not match:raise RuntimeError('Guide is missing from the main gallery: '+gid)
        card=match.group();card=re.sub(r'<span class="badge[^>]*>.*?</span>','<span class="badge new">Reconstructed clay / 12 s / continuous handover / 65% overlay</span>',card,count=1)
        card=re.sub(r'<img class="motion-image"[^>]*>',f'<img class="motion-image" loading="lazy" src="{folder}/ghost-poster.png?v={version}" data-poster="{folder}/ghost-poster.png?v={version}" data-animation="{folder}/ghost.png?v={version}" alt="Animated guide: {gid}">',card,count=1)
        card=re.sub(r'<img class="fixed-sights"[^>]*>','',card)
        card=re.sub(r'<img class="strip"[^>]*>',f'<img class="strip" loading="lazy" src="{folder}/ghost-strip.jpg?v={version}" alt="Reconstructed animation frames">',card,count=1)
        card=re.sub(r'<p class="description">.*?</p>','<p class="description">'+html.escape(row['direction'])+'</p>',card,count=1,flags=re.S)
        card=re.sub(r'<p class="blender-scope">.*?</p>','',card)
        card=re.sub(r'<footer>.*?</footer>',f'<p class="blender-scope">One shared interior, matching color and ghost exports. Published to the API.</p><footer><a href="{folder}/ghost.png" download>Ghost APNG</a><a href="{folder}/index.html">Color and ghost comparison</a></footer>',card,count=1,flags=re.S)
        text=text[:match.start()]+card+text[match.end():]
    return text

def apply_context(text):
    manifest=HERE/'clay-scenes/active-revisions.json'
    if not manifest.exists():return text
    data=json.loads(manifest.read_text())
    for gid,row in data['guides'].items():
        key=row['context_template']+'.'+row['context_step'];folder='../'+Path(row['folder']).relative_to('catalog').as_posix()
        pattern=r'<article id="'+re.escape(key)+r'".*?</article>';match=re.search(pattern,text,re.S)
        if not match:continue
        card=match.group();card=re.sub(r'<img class="motion"[^>]*>',f'<img class="motion" loading="lazy" src="{folder}/ghost-poster.png" data-poster="{folder}/ghost-poster.png" data-animation="{folder}/ghost.png" alt="New continuous clay bar-to-table guide">',card,count=1)
        card=re.sub(r'<img class="sights"[^>]*>','',card)
        card=re.sub(r'<p class="meta">.*?</p>','<p class="meta">Reconstructed clay · 4 s primary shot · 12 s continuous demonstration</p>',card,count=1)
        card=re.sub(r'<a href="[^"]+" download>Transparent APNG</a>',f'<a href="{folder}/ghost.png" download>Transparent APNG</a>',card,count=1)
        card=re.sub(r'<a href="[^"]+">Frame samples</a>',f'<a href="{folder}/index.html">Color and ghost review</a>',card,count=1)
        text=text[:match.start()]+card+text[match.end():]
    for tid,row in data.get('sequences',{}).items():
        title=html.escape(row['title']);pattern=r'<section><h2>'+re.escape(title)+r'</h2>.*?</section>'
        match=re.search(pattern,text,re.S)
        if not match:continue
        section=match.group();section=re.sub(r'<p class="clay-sequence">.*?</p>','',section,flags=re.S)
        section=re.sub(r'<p class="deferred">.*?</p>','',section,flags=re.S)
        link=f'<p class="clay-sequence"><a href="../clay-scenes/sequences/{tid}/index.html">Updated full-script sequence</a> · {row["seconds"]:g} seconds. Bar and best table share the new scene; other sections retain their previous artwork.</p>'
        section=section.replace('</h2>','</h2>'+link,1);text=text[:match.start()]+section+text[match.end():]
    return text

if __name__=='__main__':
    path=HERE/'animations.html';path.write_text(apply(path.read_text()))
    context=HERE/'context-animations/index.html'
    if context.exists():context.write_text(apply_context(context.read_text()))
    print('Image-driven scene galleries synchronized')
