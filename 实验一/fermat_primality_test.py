import os
import random

# 测试次数
k_value = 5


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def power_mod(x, n, Mod):
    res = 1
    x %= Mod
    while n != 0:
        if n & 1:
            res = (res * x) % Mod
        n >>= 1
        x = (x * x) % Mod
    return res


def fermat_primality_test(m, k, quiet=False):
    if m < 3 or m % 2 == 0:
        return False  # m必须是奇数且大于等于3

    for _ in range(k):
        a = random.randint(2, m - 2)  # 随机选择a，2 <= a <= m-2
        g = gcd(a, m)

        if g != 1:
            if quiet is False:
                print(f"m = {m}, \na = {a}, \ng = {g}")
            return False  # 若g不为1，则m为合数

        r = power_mod(a, m - 1, m)
        if r != 1:
            if quiet is False:
                print(f"m = {m}, \na = {a}, \nr = {r}")
            return False  # 若r不为1，则m为合数

    return True


if __name__ == '__main__':
    folder_path = r"test_data"
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as f:
            m_to_test = int(f.read())
            print(file_name)
            result = fermat_primality_test(m_to_test, k_value)
            if result:
                print(f"由此算法，{m_to_test}\n是素数的概率为 {1 - 1 / 2 ** k_value}")
            else:
                print(f"{m_to_test}\n不是素数")
            print("------------------------------------------------------")
