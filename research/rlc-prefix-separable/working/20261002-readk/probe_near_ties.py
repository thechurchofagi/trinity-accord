import sys,random,json,time,itertools
from verify_gray_reflection_graph import graph,optimize,order_and_scores
rng=random.Random(202610030731)
start=time.time()
for n in range(4,11):
    maximum=(-10**9,None)
    maxw=-10**9
    orders=set()
    for i in range(5000):
        # Exact integer perturbation with no subset-sum ties.
        base=rng.sample(range(2,30),n-1)
        rng.shuffle(base)
        base.append(1)
        jitter=list(range(n));rng.shuffle(jitter)
        perturb=[(1<<j)*(1 if rng.randrange(2) else -1) for j in jitter]
        a=[x*(1<<(n+2))+y for x,y in zip(base,perturb)]
        result=order_and_scores(a)
        assert result is not None and min(a)==a[-1]
        p=result[0]
        if p in orders:continue
        orders.add(p)
        g=graph(p,n);e,phi=optimize(g,n)
        net=e-g['D'];maxw=max(maxw,g['W']-g['D'])
        if net>maximum[0]:maximum=(net,a)
        if net>0 or g['W']>g['D']:
            print(json.dumps({'n':n,'i':i,'weights':a,'D':g['D'],'W':g['W'],'E':e,'phi':phi,'C':((1<<n)+g['D']-e)//2,'edges':g['edges'],'strong_counterexample':g['W']>g['D'],'actual_counterexample':net>0}),flush=True)
            if net>0:sys.exit()
    print(json.dumps({'n':n,'orders':len(orders),'max_net':maximum,'max_W_minus_D':maxw,'elapsed':time.time()-start}),flush=True)
