import os

from sympy import randprime
import random
from exp1 import fermat_primality_test as fpt

import time


# 快速幂取模算法
# 这里使用位操作，相比于直接使用乘法，更加高效
def fast_power_mod(x, n, Mod):
    res = 1
    x %= Mod
    while n != 0:
        if n & 1:
            res = (res * x) % Mod
        n >>= 1
        x = (x * x) % Mod
    return res


# 生成强素数p
# 使用sympy库中的randprime函数生成素数
# 但是2q+1不一定是素数，所以需要再次判断，这里调用了exp1中的费马素性检验
# 此处寻找强素数会需要大量时间，主要原因是2q+1不一定是素数，所以需要多次尝试
def generate_p():
    while True:
        q = randprime(pow(10, 149), pow(10, 150))
        p = 2 * q + 1
        if len(str(p)) == 150 and fpt.fermat_primality_test(p, 3, True):
            break
    return p


# 计算一个原根g
# 随机选取g看上去时间开销无法接受，但其实，对于2*q+1而言，其原根有q-1个，所以每次随机选取到原根的概率有1/2，是可以接受的
def generate_g(p):
    while True:
        g = random.randint(2, p - 2)
        q = (p - 1) // 2
        if fast_power_mod(g, 2, p) != 1 and fast_power_mod(g, q, p) != 1:
            return g


# 加密算法
# 这里不使用python内置的pow函数，而是使用自己实现的快速幂取模算法，前者效率太低
def encrypt(p, g, g_a, m):
    k = random.randint(1, p - 2)
    print("k =", k)
    c1 = fast_power_mod(g, k, p)
    print("c1 =", c1)
    temp = fast_power_mod(g_a, k, p)
    c2 = (m * temp) % p
    print("c2 =", c2)
    return c1, c2


# 解密算法
# 计算m时，是pow(v,-1,p),指的是v模p的逆元
def decrypt(p, c1, c2, a):
    v = fast_power_mod(c1, a, p)
    m = (c2 * pow(v, -1, p)) % p
    return m


if __name__ == "__main__":
    folder_path = r"test_data"
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        print(file_name)
        with open(file_path, 'r') as f:
            m = int(f.read())
            p = generate_p()
            print("p =", p)
            g = generate_g(p)
            print("g =", g)
            a = random.randint(pow(10, 149), pow(10, 150))
            g_a = fast_power_mod(g, a, p)
            print("g^a =", g_a)
            c1, c2 = encrypt(p, g, g_a, m)
            result = decrypt(p, c1, c2, a)
            print("m =", m)
            print("decrypted_result =", result)
            if m == result:
                print("成功解密")
            else:
                print("解密失败")
            print("------------------------------------------------------")
