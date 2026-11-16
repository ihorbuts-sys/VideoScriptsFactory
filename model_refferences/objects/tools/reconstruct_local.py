"""One-image local TripoSR experiment; never silently substitutes parametric geometry.

Install the pinned environment from local-reconstruction.md. The upstream source
stays unchanged; a CPU marching-cubes adapter replaces its CUDA extension at
runtime. The image encoder and 3D reconstruction weights remain upstream.
"""
import argparse,hashlib,json,os,sys,time,types
from pathlib import Path

os.environ.setdefault('HF_HOME','/private/tmp/loca-triposr/huggingface')
os.environ.setdefault('U2NET_HOME','/private/tmp/loca-triposr/u2net')
os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK','1')
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
import numpy as np
import torch
from PIL import Image
from skimage.measure import marching_cubes

def mc_adapter(level,threshold):
    array=level.detach().cpu().numpy()
    vertices,faces,_,_=marching_cubes(array,threshold,allow_degenerate=False)
    # Upstream helper swaps ZYX->XYZ after the native extension returns.
    # skimage returns array-axis XYZ here, so compensate once in the adapter.
    return torch.from_numpy(vertices[:,[2,1,0]].copy()),torch.from_numpy(faces[:,[0,2,1]].astype(np.int64).copy())

adapter=types.ModuleType('torchmcubes');adapter.marching_cubes=mc_adapter
sys.modules['torchmcubes']=adapter

def run():
    p=argparse.ArgumentParser();p.add_argument('image');p.add_argument('out')
    p.add_argument('--source',default='/private/tmp/loca-triposr/source')
    p.add_argument('--weights',default='/private/tmp/loca-triposr/weights')
    p.add_argument('--device',choices=['auto','cpu','mps'],default='auto')
    p.add_argument('--resolution',type=int,default=192)
    p.add_argument('--skip-background-removal',action='store_true');a=p.parse_args()
    sys.path.insert(0,a.source)
    from tsr.system import TSR
    from tsr.utils import resize_foreground,remove_background
    device=('mps' if torch.backends.mps.is_available() else 'cpu') if a.device=='auto' else a.device
    torch.set_num_threads(6);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    def state(stage,**kw):
        data=dict(stage=stage,device=device,input=str(Path(a.image).resolve()),resolution=a.resolution)
        data.update(kw)
        (out/'progress.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data),flush=True)
    start=time.time();state('loading_model')
    model=TSR.from_pretrained(a.weights,config_name='config.yaml',weight_name='model.ckpt')
    model.eval();model.renderer.set_chunk_size(16384);model.to(device)
    state('preparing_image',elapsed_s=time.time()-start)
    image=Image.open(a.image).convert('RGBA')
    if not a.skip_background_removal:
        import rembg
        session=rembg.new_session('u2netp',providers=['CPUExecutionProvider'])
        image=remove_background(image,session)
    image=resize_foreground(image,.85);image.save(out/'input-alpha.png')
    data=np.asarray(image).astype(np.float32)/255
    rgb=data[:,:,:3]*data[:,:,3:4]+(1-data[:,:,3:4])*.5
    prepared=Image.fromarray(np.rint(rgb*255).astype(np.uint8));prepared.save(out/'input.png')
    state('inferring_3d',elapsed_s=time.time()-start)
    with torch.inference_mode():codes=model([prepared],device=device)
    if device=='mps':torch.mps.synchronize()
    torch.save(codes.detach().cpu(),out/'scene-code.pt')
    state('extracting_mesh',elapsed_s=time.time()-start)
    with torch.inference_mode():mesh=model.extract_mesh(codes,True,resolution=a.resolution)[0]
    # Retain the full original reconstruction, before cleanup or unit conversion.
    mesh.export(out/'reconstruction.glb');mesh.export(out/'reconstruction.ply')
    report=dict(method='Official TripoSR single-image reconstruction',upstream='https://github.com/VAST-AI-Research/TripoSR',
        upstream_commit='107cefdc244c39106fa830359024f6a2f1c78871',license='MIT',device=device,
        input=str(Path(a.image).resolve()),input_sha256=hashlib.sha256(Path(a.image).read_bytes()).hexdigest(),
        vertices=len(mesh.vertices),faces=len(mesh.faces),watertight=bool(mesh.is_watertight),bounds=mesh.bounds.tolist(),
        duration_s=time.time()-start,grid_resolution=a.resolution,status='reconstructed_pending_blender_review',
        limitation='Single-image model: only the selected view conditions reconstruction. Other saved views are comparison targets, not claimed multiview inputs.',
        marching_cubes='scikit-image CPU adapter; reconstruction network is unchanged')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');state('mesh_saved',**report)

if __name__=='__main__':run()
