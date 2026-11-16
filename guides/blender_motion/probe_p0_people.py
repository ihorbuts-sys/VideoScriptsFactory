"""Static pose checkpoints for character review, using the production renderer."""
import argparse,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import render_p0
from p0_people import IDS

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ids',nargs='*',default=sorted(IDS));p.add_argument('--phases',nargs='*',default=['target','middle'])
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    for gid in a.ids:
        for phase in a.phases:
            render_p0.run(argparse.Namespace(id=gid,out=render_p0.ROOT/'catalog/p0/people-study'/gid/phase,probe=phase,replace=True))
