"""Render integration cases and verify CLI failures without relying on Blender's error flag."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from validate_lineart import validate

def run(args):
    renderer=Path(__file__).with_name('lineart_render.py').resolve()
    fixture=args.fixtures/'cup.blend'
    cases=[
        ('synthetic-top-push',fixture,['--angle','top','--size','detail','--move','push-in']),
        ('cup-top-push',args.model,['--angle','top','--size','detail','--move','push-in']),
        ('cup-top-wide',args.model,['--angle','top','--size','wide']),
        ('cup-eye-hidden',args.model,['--angle','eye','--size','wide','--hidden']),
        ('obj-high',fixture.with_suffix('.obj'),['--angle','high','--size','medium']),
        ('fbx-low',fixture.with_suffix('.fbx'),['--angle','low','--size','wide']),
        ('glb-pan',fixture.with_suffix('.glb'),['--angle','eye','--size','wide','--lens','ultrawide','--move','pan','--duration','1.1']),
        ('glb-tilt',fixture.with_suffix('.glb'),['--angle','high','--size','wide','--move','tilt','--duration','1.1']),
        ('glb-orbit',fixture.with_suffix('.glb'),['--angle','high','--size','wide','--move','orbit','--duration','1.1']),
        ('glb-pull',fixture.with_suffix('.glb'),['--angle','eye','--size','wide','--move','pull-out','--duration','1.1']),
    ]
    results=[]
    for name,model,options in cases:
        out=args.out/name;log=args.out/(name+'.log');args.out.mkdir(parents=True,exist_ok=True)
        if (out/'meta.json').exists():
            assert json.loads((out/'meta.json').read_text()).get('renderer_sha256')==hashlib.sha256(renderer.read_bytes()).hexdigest(),'Renderer changed; use a fresh --out test directory'
        else:
            with log.open('w') as stream:
                subprocess.run([str(args.blender),'-b','--python-exit-code','1','-P',str(renderer),'--','--model',str(model),*options,'--out',str(out)],stdout=stream,stderr=stream,check=True)
        report=validate(out);results.append(dict(case=name,folder=str(out),**report));print('LINEART_CASE_PASSED',name,flush=True)
    errors=[]
    for name,model in [('missing',args.fixtures/'missing.blend'),('unsupported',args.out/'invalid.txt'),('empty',args.fixtures/'empty.blend')]:
        if name=='unsupported':model.write_text('Unsupported format fixture\n')
        log=args.out/(name+'-error.log')
        with log.open('w') as stream:
            result=subprocess.run([str(args.blender),'-b','-P',str(renderer),'--','--model',str(model),'--angle','eye','--size','wide','--out',str(args.out/(name+'-error'))],stdout=stream,stderr=stream)
        assert result.returncode!=0,('CLI failure returned success',name)
        assert 'LINEART_ERROR' in log.read_text(),name
        errors.append(dict(case=name,exit_code=result.returncode))
    report=dict(status='passed',render_cases=results,error_cases=errors,no_active_guide_or_API_replacement=True)
    (args.out/'test-report.json').write_text(json.dumps(report,indent=2)+'\n');print('LINEART_INTEGRATION_PASSED',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--blender',type=Path,required=True);p.add_argument('--model',type=Path,required=True)
    p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--out',type=Path,required=True);run(p.parse_args())
