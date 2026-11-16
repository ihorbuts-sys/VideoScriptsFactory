"""Apply individually reviewed reconstructed-scene revisions without rebaselining other art."""
import copy,hashlib,json,os,shutil
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
MANIFEST=BASE/'catalog/clay-scenes/active-revisions.json'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def versioned(source,out,kind,name):
    sha=digest(source);relative=f'{kind}/{sha[:16]}/{name}';target=Path(out)/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():shutil.copy2(source,target)
    assert digest(target)==sha
    return relative,sha

def apply(bundle,out):
    if not MANIFEST.exists():return []
    manifest=json.loads(MANIFEST.read_text());records=list(manifest['guides'].items());changed=[]
    records += [(row['guide_id'],row) for row in manifest.get('guide_variants',{}).values()]
    for gid,row in records:
        assert row['reviewed'] and row['scope'] in ['shot_and_handover','complete_final_shot']
        folder=(BASE/row['folder']).resolve();assert folder.is_relative_to(BASE)
        checks=json.loads((folder/'export-checks.json').read_text())
        spec=json.loads((folder/'scene-spec.json').read_text())
        view_mode=row.get('opacity_mode')=='image_view'
        if view_mode:
            assert checks['image_opacity_baked']==1 and checks['max_ghost_alpha']<=255
        else:
            assert checks['whole_overlay_alpha']==.65 and checks['max_ghost_alpha']<=166
        assert spec['scope']==row['scope'] and spec['handover_status']==row['handover_status']
        for name,expected in row['files'].items():assert digest(folder/name)==expected,(gid,name)
        files={};sha=None
        for key,source,kind,name in [('overlay','view-overlay.png' if view_mode else 'ghost.png','overlays',gid+'.png'),
              ('poster','view-overlay-poster.png' if view_mode else 'ghost-poster.png','overlays',gid+'_poster.png'),
              ('strip','view-overlay-strip.jpg' if view_mode else 'ghost-strip.jpg','overlays',gid+'_strip.jpg'),
              ('colorVideo','color.mp4','overlays',gid+'_color.mp4')]:
            files[key],value=versioned(folder/source,out,kind,name)
            if key=='overlay':sha=value
        update=dict(**files,sha256=sha,sourceSha256=sha,animationSeconds=spec['duration_s'],
            alphaFactor=1 if view_mode else .65,style='blender',rendering=row.get('rendering','native-3d-reconstructed-shot-and-handover'),
            scope=spec['scope'],handoverStatus=spec['handover_status'],
            contextTemplateID=row['context_template'],contextStepID=row['context_step'],
            nextGuideID=spec.get('next_guide'),transitionMethod=spec.get('transition_method'),
            sceneRevision=row.get('revision','image-driven-clay-v1'))
        if view_mode:
            update.update(imageViewOpacity=.65,opacityAppliedIn='image_view',viewfinderEmbedded=False)
            scenario_path,_=versioned(folder/'scenario.json',out,'scenarios',gid+'.json')
            files['scenario']=scenario_path
            update.update(scenario=scenario_path,seconds=spec['capture_seconds'],moves=spec['moves'])
        if row.get('update_global',True):bundle['guides'][gid].update(update)
        contexts=row.get('contexts',[dict(template=row['context_template'],step=row['context_step'],direction=row['direction'])])
        for context in contexts:
            step_key=context['template']+'.'+context['step']
            overrides=bundle.setdefault('stepGuideOverrides',{}).setdefault(step_key,{})
            overrides[gid]={**overrides.get(gid,{}),**update,
                'contextTemplateID':context['template'],'contextStepID':context['step']}
            if 'next_guide' in context:overrides[gid]['nextGuideID']=context['next_guide']
            if view_mode:overrides[gid]['seconds']=context.get('capture_seconds',spec['capture_seconds'])
            # Keep the same direction in template and custom-step library APIs.
            for template in bundle['templates']:
                if template['id']==context['template']:
                    for step in template['steps']:
                        if step['id']==context['step']:
                            step['direction']=context['direction']
                            if context.get('update_capture_seconds'):step['seconds']=context['capture_seconds']
            for group in bundle.get('stepGroups',[]):
                for step in group['steps']:
                    if step['templateID']==context['template'] and step['id']==context['step']:
                        step['direction']=context['direction']
                        if context.get('update_capture_seconds'):step['seconds']=context['capture_seconds']
        if row.get('update_global',True):
            for key in ['overlay','poster','strip']+(['scenario'] if view_mode else []):
                source=Path(out)/files[key];alias=Path(out)/('scenarios' if key=='scenario' else 'overlays')/source.name
                temporary=alias.with_name(alias.name+'.clay-tmp');temporary.unlink(missing_ok=True)
                os.link(source,temporary);os.replace(temporary,alias)
        changed.append(gid)
    for tid,row in manifest.get('sequences',{}).items():
        assert row['reviewed'];folder=(BASE/row['folder']).resolve();assert folder.is_relative_to(BASE)
        checks=json.loads((folder/'assembly-checks.json').read_text())
        view_mode=row.get('opacity_mode')=='image_view'
        assert checks['status']=='passed' and checks['max_alpha']<=(255 if view_mode else 166) and not checks['alpha_applied_again']
        for name,expected in row['files'].items():assert digest(folder/name)==expected,(tid,name)
        files={};sha=None
        for key,source,name in [('overlay','ghost.png',tid+'_overlay.png'),('video','preview.mp4',tid+'_video.mp4'),
                               ('poster','poster.png',tid+'_poster.png'),('strip','strip.jpg',tid+'_strip.jpg')]:
            files[key],value=versioned(folder/source,out,'sequences',name)
            if key=='overlay':sha=value
            target=Path(out)/files[key];alias=Path(out)/'sequences'/name;temporary=alias.with_name(name+'.clay-tmp')
            temporary.unlink(missing_ok=True);os.link(target,temporary);os.replace(temporary,alias)
        previous=bundle['scriptGuideSequences'][tid]
        bundle['scriptGuideSequences'][tid]={**previous,**files,'sha256':sha,'sourceSha256':sha,
            'seconds':row['seconds'],'steps':row['steps'],'alphaFactor':1 if view_mode else .65,
            'sceneRevision':row.get('revision','image-driven-clay-v1-partial-script')}
        if view_mode:
            bundle['scriptGuideSequences'][tid].update(imageViewOpacity=.65,opacityAppliedIn='image_view',
                scope='full_script_instruction_sequence',fullScriptSequenceComplete=True,
                viewfinderEmbedded=False,wallsEmbedded=False,floorEmbedded=False)
    return changed

def publish(out):
    out=Path(out);index=out/'catalog.json';before=json.loads(index.read_text());bundle=copy.deepcopy(before)
    changed=apply(bundle,out)
    assert before['previewArt']==bundle['previewArt'],'Step preview art must remain unchanged'
    assert len(bundle['guides'])==len(before['guides'])
    for gid,guide in before['guides'].items():
        if gid not in changed:assert guide==bundle['guides'][gid]
    for guide in bundle['guides'].values():
        for key in ['overlay','poster','strip','scenario','model3D']:assert (out/guide[key]).is_file()
    backup=BASE/'catalog/clay-scenes/publication';backup.mkdir(exist_ok=True)
    old_sha=hashlib.sha256(index.read_bytes()).hexdigest()
    previous=backup/f'catalog-before-{old_sha[:16]}.json'
    if not previous.exists():shutil.copy2(index,previous)
    temporary=index.with_name('catalog.clay-tmp');temporary.write_text(json.dumps(bundle,indent=1)+'\n');os.replace(temporary,index)
    report=dict(changed_guides=changed,live_catalog=str(index),prior_catalog_sha256=old_sha,
        preview_revision_preserved=bundle['previewArt']['revisionSHA256'],total_guides=len(bundle['guides']),
        per_step_overrides_updated=True,changed_sequences=list(json.loads(MANIFEST.read_text()).get('sequences',{})),
        source_manifest=str(MANIFEST),catalog_only_publication=True)
    (backup/'publication.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    print(json.dumps(publish(args.out)))
