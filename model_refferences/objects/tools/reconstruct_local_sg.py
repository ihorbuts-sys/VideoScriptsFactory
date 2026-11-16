"""Local MIT TripoSG shape trial for structures the first model merged.

The official network is unchanged. Use the standard marching-cubes decoder at
one dense level to avoid the optional CUDA-only mesh extractor on Apple MPS.
"""
import argparse,hashlib,json,os,sys,time,types
from pathlib import Path
os.environ.setdefault('HF_HOME','/private/tmp/loca-triposg/huggingface')
os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK','1')
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
import numpy as np
import torch
import trimesh
from PIL import Image

module=types.ModuleType('diso')
class DiffDMC:
    def __init__(self,*a,**k):raise RuntimeError('Use the standard decoder; CUDA mesh extraction is disabled on this Mac')
module.DiffDMC=DiffDMC;sys.modules['diso']=module

def run():
    p=argparse.ArgumentParser();p.add_argument('image');p.add_argument('out');p.add_argument('--asset',default='pastry_rack')
    p.add_argument('--source',default='/private/tmp/loca-triposg/source');p.add_argument('--weights',default='/private/tmp/loca-triposg/weights')
    p.add_argument('--steps',type=int,default=25);p.add_argument('--depth',type=int,default=7);a=p.parse_args()
    sys.path.insert(0,a.source)
    from triposg.pipelines.pipeline_triposg import TripoSGPipeline
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);start=time.time()
    def state(stage,**kw):
        data=dict(stage=stage,device='mps',elapsed_s=round(time.time()-start,2),**kw)
        (out/'progress.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data),flush=True)
    state('loading_model');torch.set_num_threads(6)
    pipe=TripoSGPipeline.from_pretrained(a.weights,torch_dtype=torch.float16,low_cpu_mem_usage=True).to('mps')
    original_decode=pipe.vae._decode
    def chunked_decode(*args,**kwargs):
        kwargs['num_chunks']=4096;return original_decode(*args,**kwargs)
    pipe.vae._decode=chunked_decode
    image=Image.open(a.image).convert('RGBA');background=Image.new('RGBA',image.size,'white');background.alpha_composite(image);image=background.convert('RGB');image.save(out/'input.png')
    state('inferring_shape',steps=a.steps)
    def progress(pipeline,step,timestep,kwargs):
        state('inferring_shape',step=step+1,total=a.steps)
        if step==a.steps-1:torch.save(kwargs['latents'].detach().cpu(),out/'latents.pt')
        return kwargs
    with torch.inference_mode():
        result=pipe(image=image,num_inference_steps=a.steps,guidance_scale=7.0,
                    generator=torch.Generator(device='cpu').manual_seed(42),
                    dense_octree_depth=a.depth,hierarchical_octree_depth=a.depth,use_flash_decoder=False,
                    callback_on_step_end=progress)
    state('saving_mesh');mesh=result.meshes[0]
    mesh.export(out/'original-sg.glb')
    extents=np.ptp(mesh.vertices,axis=0)
    up_axis=int(np.argmax(extents)) if a.asset=='pastry_rack' else int(np.argsort(extents)[-2])
    if up_axis==1:mesh.vertices=mesh.vertices[:,[2,0,1]]
    if mesh.volume<0:mesh.invert()
    mesh.export(out/'reconstruction.ply');mesh.export(out/'reconstruction.glb')
    report=dict(method='Official MIT TripoSG local shape reconstruction',upstream='https://github.com/VAST-AI-Research/TripoSG',
        upstream_commit='fc5c40990181e2a756c4e0b1c2f4d6b5202faf8c',license='MIT',asset=a.asset,
        input=str(Path(a.image).resolve()),input_sha256=hashlib.sha256(Path(a.image).read_bytes()).hexdigest(),
        vertices=len(mesh.vertices),faces=len(mesh.faces),watertight=bool(mesh.is_watertight),duration_s=time.time()-start,
        inferred_up_axis_before_conversion=up_axis,raw_extents=extents.tolist(),bounds=mesh.bounds.tolist(),
        status='reconstructed_pending_structural_review',steps=a.steps,grid_resolution=2**a.depth,
        limitation='Single-image shape model. Clay materials and functional openings require independent Blender review.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');state('mesh_saved',faces=report['faces'])

if __name__=='__main__':run()
