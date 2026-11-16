"""Inventory actual published guide components without mistaking them for finished models."""
import collections,hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from catalog import ASSETS
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parents[1]
RULES={
 'croissant':r'Croissant|Laminated pastry', 'filled_croissant':r'Cream filling|Chocolate filling',
 'croissant_oozing':r'Chocolate filling', 'pastry_rack':r'Pastry shelf|Visible food rack',
 'display_case':r'Case side support|Pastry shelf', 'bar_counter':r'Bar counter|bar top|bar carcass|Counter front|Public counter',
 'dining_chair':r'Dining chair', 'dining_table':r'Quiet tabletop|Table pedestal',
 'storefront':r'Door jamb|Window|Venue name sign', 'signboard':r'Venue name sign|Studio sign',
 'pastry_box':r'Box base|Box side|Box end|Box hinged lid', 'kitchen_tongs':r'Food tongs',
 'cup_saucer':r'coffee surface|hollow ceramic|open handle|Saucer|Latte rosetta',
 'kettle':r'kettle', 'espresso_machine':r'Coffee machine|coffee machine|Machine drip|espresso outlet|Portafilter|Public machine',
 'menu_board':r'Menu board|Menu frame|Menu resource|Venue resource', 'bar_stool':r'stool|Bar seat',
 'drinking_glass':r'open bowl|liquid level|tumbler', 'bottle':r'bottle',
 'pendant':r'Pendant|Warm lit|switched-on bulb', 'plant':r'Plant ',
 'serving_tray':r'Food tray|Supported flight paddle','cutlery':r'Fork |Place-setting knife',
 'laptop':r'Laptop|laptop', 'glazed_door':r'Door |Glazed door|Doorway',
 'window':r'Window', 'wall_shelf':r'shelf|Shelf',
}

def run():
    templates=json.loads((BASE/'guides/script_templates.json').read_text())['templates']
    ids=sorted({g for t in templates for s in t['steps'] for g in s.get('overlays',[])})
    components=collections.defaultdict(set);guides=[];missing=[]
    for gid in ids:
        source=BASE/'guides/templates'/f'{gid}.json';description=json.loads(source.read_text())['description']
        spec=BASE/'catalog/blender-animations'/gid/'scene-spec.json'
        if not spec.exists():spec=BASE/'catalog/blender-study'/gid/'scene-spec.json'
        if spec.exists():objects=json.loads(spec.read_text()).get('objects',[])
        else:objects=[];missing.append(gid)
        names=sorted({re.sub(r'\.\d+$','',o['name']) for o in objects})
        for n in names:components[n].add(gid)
        humans=any(n.startswith('MakeHuman person') or 'Anatomical' in n for n in names)
        guides.append(dict(id=gid,description=description,component_names=names,uses_humans_or_hands=humans,
            replacement_status='pending_clay_scene_build',two_render_variants_required=['color','ghost'],
            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    assets=[]
    for id,(cat,desc,size) in ASSETS.items():
        usage=sorted({g for n,gs in components.items() if re.search(RULES.get(id,r'(?!)'),n,re.I) for g in gs})
        meta=ROOT/id/'reconstructed/metadata.json'
        if not meta.exists():meta=ROOT/id/'metadata.json'
        data=json.loads(meta.read_text()) if meta.exists() else {}
        assets.append(dict(id=id,category=cat,description=desc,planned_dimensions_m=size,guide_usage=usage,
            design_reference_exists=(ROOT/id/'design/sheet.png').exists() or (ROOT/id/'design/three-quarter.png').exists(),
            model_status=data.get('status','not_built'),model=str(meta.parent.relative_to(ROOT)/'model.blend') if meta.exists() else None))
    result=dict(date='2026-10-28',published_guides=len(ids),component_families=len(components),
        missing_scene_specs=missing,scope='All published guide meshes inventoried; first modeling batch is the reusable cafe/bar prop set. Other component families and human scenes remain explicitly pending.',
        assets=assets,components=[dict(name=n,guide_usage=sorted(gs),
            matches=[a for a,p in RULES.items() if re.search(p,n,re.I)]) for n,gs in sorted(components.items())],guides=guides,
        character_models_required=['creator','barista','friend_locs'],
        human_guide_count=sum(g['uses_humans_or_hands'] for g in guides))
    (ROOT/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Reusable guide models','',f"Audited {len(ids)} published guides and {len(components)} named mesh/component families. {result['human_guide_count']} guides contain full people or anatomical hands.",'',
        'Human scenes must be rebuilt with the approved creator, barista and friend with sculpted locs. Existing realistic MakeHuman actors are not accepted as the new cast. Both full-color and transparent ghost renders are required for every replacement.','',
        '## First reusable asset batch','', '| Asset | Category | Guides using corresponding parts | Design sheet | Native model |','|---|---|---|---|---|']
    for a in assets:lines.append(f"| [{a['id']}]({a['id']}/) | {a['category']} | {len(a['guide_usage'])} | {'Generated' if a['design_reference_exists'] else 'Pending'} | {a['model_status']} |")
    lines+=['','## Complete component inventory','','Component names below come from the saved scenes; a component is not automatically a standalone prop. The JSON retains every guide relationship.','']
    for row in result['components']:lines.append(f"- {row['name']}: {len(row['guide_usage'])} guides")
    (ROOT/'inventory.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:result[k] for k in ['published_guides','component_families','missing_scene_specs','human_guide_count']}))

if __name__=='__main__':run()
