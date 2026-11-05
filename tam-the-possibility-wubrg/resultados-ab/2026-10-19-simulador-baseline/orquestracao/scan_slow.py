import sys, time, signal, multiprocessing as mp
sys.path.insert(0, '/home/user/MTG-Code/tam-the-possibility-wubrg')
import tam_goldfish_v1 as T
class TO(Exception): pass
def h(*a): raise TO()
def work(args):
    lo, hi, fn = args
    f = T.simulate_one if fn == "p" else T.simulate_one_with_interaction
    signal.signal(signal.SIGALRM, h)
    slow = []
    for sd in range(lo, hi):
        signal.alarm(8)
        t = time.time()
        try:
            f(sd, 12)
        except TO:
            slow.append((sd, "TIMEOUT"))
        except Exception as e:
            slow.append((sd, "EXC " + type(e).__name__ + str(e)[:50]))
        finally:
            signal.alarm(0)
        if time.time() - t > 2 and not (slow and slow[-1][0] == sd):
            slow.append((sd, round(time.time() - t, 1)))
    return slow
if __name__ == "__main__":
    fn = sys.argv[1]; N = int(sys.argv[2])
    with mp.Pool(4) as p:
        r = p.map(work, [(5_000_000 + i * 500, 5_000_000 + (i + 1) * 500, fn) for i in range(N // 500)])
    print(fn, [x for b in r for x in b])
