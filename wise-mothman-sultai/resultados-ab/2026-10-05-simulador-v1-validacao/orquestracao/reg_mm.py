import sys, json, time
sys.path.insert(0, '.')
import abgen
cam='/home/user/MTG-Code/wise-mothman-sultai/mothman_goldfish_v1.py'
cwd='/home/user/MTG-Code/wise-mothman-sultai'
n=int(sys.argv[1]); seed0=int(sys.argv[2]) if len(sys.argv)>2 else 1
for modo in ("padrao","resiliencia"):
    t0=time.time()
    r=abgen.regressao(cam,'mm_reg',cwd,{},modo,n,seed0,12)
    print(modo, json.dumps(r,ensure_ascii=False), f"{time.time()-t0:.0f}s")
