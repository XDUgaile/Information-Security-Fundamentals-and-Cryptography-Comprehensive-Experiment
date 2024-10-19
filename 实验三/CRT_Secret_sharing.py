import os
import random


def generate_d(k, t, n):
    max = pow(10, 200)
    while True:
        primes = [random.randint(2, max)]
        while len(primes) < n:
            primes.append(random.randint(2, max))
            if not coprime(primes):
                primes.pop()
        sorted_primes = sorted(primes)
        product_n = 1
        product_m = 1
        for num in sorted_primes[:t]:
            product_n *= num
        for num in sorted_primes[-t + 1:]:
            product_m *= num
        if product_n > k > product_m:
            for i in range(n):
                print(f"d{i + 1}={sorted_primes[i]}")
            print(f"N={product_n},\nM={product_m}")
            break
    return sorted_primes


def mod_inverse(a, m):
    return pow(a, -1, m)


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def coprime(x):
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            if gcd(x[i], x[j]) != 1:
                return False
    return True


def product(x):
    result = 1
    M = []
    for i in x:
        result *= i
    for i in range(len(x)):
        temp = 1
        for j in range(len(x)):
            if i != j:
                temp *= x[j]
        M.append(temp)
    return result, M


def select_elements(input_list, m):
    # 确保 m 不大于列表的长度，以避免错误
    m = min(m, len(input_list))

    # 从输入列表中随机选择 m 个元素
    selected_elements = random.sample(input_list, m)

    return selected_elements


def crt(data):
    num_a = len(data) // 2
    ai = data[:num_a]
    mi = data[num_a:]
    # 计算m
    m, Mj = product(mi)
    # 计算Mj的逆元
    inv_Mj = [mod_inverse(Mj[i], mi[i]) for i in range(len(Mj))]
    # 计算x
    x = [ai[i] * Mj[i] * inv_Mj[i] for i in range(len(ai))]
    # 求解
    return sum(x) % m


if __name__ == "__main__":
    t = 3
    n = 5
    folder_path = r"test_data"
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        print(file_name)
        with open(file_path, 'r') as f:
            k = int(f.read())
            raw_data = generate_d(k, t, n)
            selected_data = select_elements(raw_data, t)
            data = []
            for i in range(t):
                data.append(k % selected_data[i])
            data += selected_data
            result = crt(data)
            print(f"k={k}")
            print(f"result={result}")
            if result == k:
                print("恢复成功")
            else:
                print("恢复失败")
            print()
