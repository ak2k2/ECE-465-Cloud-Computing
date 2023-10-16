import time as t

def fib(N):
    if N <= 2:
        return 0
    a = 0
    b = 1
    for i in range(N-1):
        res = a + b
        a = b
        b = res
    return res

st = t.time()
for N in list(range(10000)):
    fib(N)
    
print(f"seq took {t.time() - st} seconds")
