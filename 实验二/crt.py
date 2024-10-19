import os


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


def mod_inverse(a, m):
    return pow(a, -1, m)


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


def select_random_elements(input_list, m):
    # 确保 m 不大于列表的长度，以避免错误
    m = min(m, len(input_list))

    # 从输入列表中随机选择 m 个元素
    selected_elements = random.sample(input_list, m)

    return selected_elements


if __name__ == "__main__":
    folder_path = r"test_data"
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        print(file_name)
        with open(file_path, 'r') as f:
            datas = f.readlines()
            data = [int(i.strip()) for i in datas]
            num_a = len(data) // 2
            ai = data[:num_a]
            mi = data[num_a:]
            if not coprime(mi):
                print("m不满足两两互质，不能直接利用中国剩余定理")
            else:
                # 计算m
                m, Mj = product(mi)
                # 计算Mj的逆元
                inv_Mj = [mod_inverse(Mj[i], mi[i]) for i in range(len(Mj))]
                # 计算x
                x = [ai[i] * Mj[i] * inv_Mj[i] for i in range(len(ai))]
                # 求解
                result = sum(x) % m
                print("x ≡ {} \nmod {}".format(result, m))
