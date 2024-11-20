from math import ceil, log, floor
import secrets
from gmssl import sm3
import os


def bytes_to_bits(bytes_string: bytes):
    """将字节串转换为比特串"""
    bits = ''
    for byte in bytes_string:
        for i in range(8):
            bit_value = (byte >> (7 - i)) & 1  # 获取当前字节的每一位比特
            bits += str(bit_value)
    return bits


def bits_to_bytes(bits_string: str):
    """将比特串转换为字节串"""
    global l
    byte_string = b''
    for i in range(0, len(bits_string), 8):
        byte = int(bits_string[i:i + 8], 2)  # 每8个比特转换为一个字节
        byte_string += bytes([byte])
    # 如果字节串长度不足l，则左填充补0
    if len(byte_string) < l:
        byte_string = byte_string.rjust(l, b'\x00')
    return byte_string


def int_to_bytes(x: int):
    """将整数转换为字节串"""
    global l
    try:
        byte_string = x.to_bytes(l, byteorder='big')  # 转换为指定长度的字节串
    except OverflowError:
        print("int_to_bytes: l设定太小，溢出")
        return
    return byte_string


def bytes_to_int(byte_string: bytes):
    """将字节串转换为整数"""
    integer = int.from_bytes(byte_string, byteorder='big')
    return integer


def field_to_bytes(x, form: int):
    """将字段值转换为字节串，根据形式选择转换方式"""
    if form == 0:
        return int_to_bytes(x)
    else:
        return bits_to_bytes(x)


def bytes_to_field(x, form: int):
    """将字节串转换为字段值，根据形式选择转换方式"""
    if form == 0:
        return bytes_to_int(x)
    else:
        return bytes_to_bits(x)


def hex_to_bits(h):
    """将十六进制字符串转换为比特串"""
    b_list = []
    for i in h:
        b = bin(eval('0x' + i))[2:].rjust(4, '0')  # 每个十六进制字符转换为4位比特
        b_list.append(b)
    b = ''.join(b_list)
    return b


def bits_to_hex(bits):
    """将比特串转换为十六进制字符串"""
    decimal_value = int(bits, 2)  # 将比特串转换为十进制
    hex_num = hex(decimal_value)  # 转换为十六进制
    return hex_num


def mod_inverse(a, p):
    """计算a在模p下的乘法逆元"""
    return pow(a, -1, p)


def fraction_to_int(numer, denom):
    """将分数转换为整数"""
    global p
    return (numer % p * mod_inverse(denom, p)) % p


def point_to_bytes(P, form: int):
    """将椭圆曲线点P转换为字节串，依据形式选择不同的编码"""
    x, y = P[0], P[1]
    x1 = int_to_bytes(x)  # x坐标转为字节串
    if form == 1:
        yp = y & 1  # 获取y坐标的奇偶性
        if yp == 1:
            pc = b'\x03'  # 奇数y
        else:
            pc = b'\x02'  # 偶数y
        s = pc + x1  # 编码为pc + x
    elif form == 0:
        y1 = int_to_bytes(y)  # y坐标转为字节串
        pc = b'\x04'  # 包含x和y的编码
        s = pc + x1 + y1
    else:
        y1 = int_to_bytes(y)
        yp = y & 1
        if yp == 1:
            pc = b'\x07'  # 特殊情况
        else:
            pc = b'\x06'
        s = pc + x1 + y1
    return s


def bytes_to_point(s, form):
    """将字节串s转换为椭圆曲线点，依据形式解析"""
    global a, b
    PC = s[0]  # 获取前缀标识
    if form == 1:
        x = s[1:]  # 提取x坐标
        if PC == 0x02:
            y_hat = 0  # 奇数y的标识
        elif PC == 0x03:
            y_hat = 1
        else:
            raise Exception("bytes_to_point: PC错误")
    elif form == 0:
        if PC == 0x04:
            x_length = (len(s) - 1) // 2
            x = s[1: l + 1]  # 提取x坐标
            y = s[l + 1: 2 * l + 1]  # 提取y坐标
            xp = bytes_to_field(x, 0)
            yp = bytes_to_field(y, 0)
            if (xp ** 3 + a * xp + b - yp ** 2) % p != 0:
                raise Exception("bytes_to_point: 点不在椭圆曲线上")  # 检查点是否在曲线上
            P = (xp, yp)
            print("C1满足椭圆曲线方程")
            return P
    elif form == 2:
        if PC == 0x06:
            y_hat = 0
        elif PC == 0x07:
            y_hat = 1
        else:
            raise Exception("bytes_to_point: PC错误")


def EC_scalar_add(P, Q):
    """对椭圆曲线点P和Q进行加法运算"""
    global p
    if P == 0:
        return Q
    if Q == 0:
        return P
    x1, y1, x2, y2 = P[0], P[1], Q[0], Q[1]
    lmd = fraction_to_int((y2 - y1), (x2 - x1))  # 计算斜率
    x3 = (lmd ** 2 - x1 - x2) % p  # 计算结果点x坐标
    y3 = (lmd * (x1 - x3) - y1) % p  # 计算结果点y坐标
    result = (x3, y3)
    return result


def EC_scalar_double(P):
    """对椭圆曲线点P进行倍加运算"""
    global p, a
    if P == 0:
        return P
    x, y = P[0], P[1]
    lmd = fraction_to_int((3 * x ** 2 + a), (2 * y))  # 计算斜率
    x3 = (lmd ** 2 - 2 * x) % p  # 计算结果点x坐标
    y3 = (lmd * (x - x3) - y) % p  # 计算结果点y坐标
    result = (x3, y3)
    return result


def EC_scalar_multiple(P, k: int):
    """计算椭圆曲线点P的k倍"""
    global p
    Q = 0  # 初始结果为无穷远点
    k_bits = bin(k)[2:]  # 将k转换为二进制
    for i in k_bits:
        Q = EC_scalar_double(Q)  # 倍加
        if i == '1':
            Q = EC_scalar_add(P, Q)  # 如果当前位为1，进行加法
    return Q


def KDF(Z, klen: int):
    """密钥派生函数KDF"""
    v = 256
    if klen >= (pow(2, 32) - 1) * v:
        raise Exception("密钥派生函数KDF出错，请检查klen的大小！")
    ct = 0x00000001  # 计数器
    t = ceil(klen / v)  # 需要生成的块数
    H_a = []
    for i in range(t):
        ct_bytes = int_to_bytes(ct)
        ct_bits = bytes_to_bits(ct_bytes)
        # 上面填充多了，这里截取后32位
        ct_bits = ct_bits[-32:]
        s_bits = Z + ct_bits  # 组合输入
        s_bytes = bits_to_bytes(s_bits)  # 转换为字节
        s_list = [i for i in s_bytes]  # 转为列表格式
        hash_hex = sm3.sm3_hash(s_list)  # 计算哈希
        hash_bin = hex_to_bits(hash_hex)  # 转换为比特串
        H_a.append(hash_bin)  # 保存哈希值
        ct += 1  # 计数器递增
    if klen % v != 0:
        H_a[-1] = H_a[-1][:klen - v * floor(klen / v)]  # 截取最后一块
    K = ''.join(H_a)  # 连接所有块
    return K


def SM2_encryption(plaintext):
    """SM2加密"""
    # 明文：
    M_str = plaintext  # 明文字符串
    M_bytes = M_str.encode('utf-8')  # 转换为字节
    M_int = int(M_bytes.hex(), 16)  # 转换为整数

    # 用随机数发生器产生随机数k∈[1,n-1]
    k = secrets.randbelow(n)  # 随机选择k
    print("随机数k:", k)

    # 计算椭圆曲线点C1=[k]G=(x1,y1)
    C1_point = EC_scalar_multiple(G, k)

    # 将C1的数据类型转换为比特串
    C1_bytes = point_to_bytes(C1_point, 0)
    C1_bits = bytes_to_bits(C1_bytes)  # 转换为比特串
    C1 = bits_to_hex(C1_bits)[2:]  # 转换为十六进制字符串
    print("C1_x:", hex(C1_point[0]))  # 打印C1的x坐标
    print("C1_y:", hex(C1_point[1]))  # 打印C1的y坐标

    # 计算椭圆曲线点[k]PB=(x2,y2)
    S1 = EC_scalar_multiple(P_B, k)
    print("[k]PB_x:", hex(S1[0]))  # 打印S1的x坐标
    print("[k]PB_y:", hex(S1[1]))  # 打印S1的y坐标
    x2 = S1[0]
    y2 = S1[1]

    # 将坐标x2、y2的数据类型转换为比特串
    x2_bytes = field_to_bytes(x2, 0)
    x2_bits = bytes_to_bits(x2_bytes)
    y2_bytes = field_to_bytes(y2, 0)
    y2_bits = bytes_to_bits(y2_bytes)

    klen = 4 * len(M_bytes.hex())  # 计算输出密钥长度

    # 计算t=KDF(x2 ∥ y2, klen)，若t为全0比特串，则返回A1
    t = KDF(x2_bits + y2_bits, klen)
    if all(bit == '0' for bit in t):  # 检查t是否为全0
        raise Exception("KDF返回了全0比特串，需重新生成k")
    t_hex = bits_to_hex(t)
    print("加密中的t:", t_hex)

    # 计算C2 = M ⊕ t
    C2_int = M_int ^ int(t_hex, 16)  # 明文与t进行异或运算
    C2 = hex(C2_int)[2:]  # 转换为十六进制字符串
    print("C2:", C2)
    s = x2_bytes + M_bytes + y2_bytes  # 合并数据
    hash_list = [i for i in s]
    M_bits = bytes_to_bits(M_bytes)  # 明文转换为比特串
    print("(x2 || M || y2):", bits_to_hex(x2_bits + M_bits + y2_bits))

    # 计算C3 = Hash(x2 ∥ M ∥ y2)
    C3 = sm3.sm3_hash(hash_list)  # 计算哈希值
    print("C3:", C3)

    # 输出密文C = C1 ∥ C2 ∥ C3
    C = C1 + C2 + C3  # 拼接密文
    print("密文:", C)
    return C


def SM2_decryption(C):
    """SM2解密"""
    # 从C中取出比特串C1，将C1的数据类型转换为椭圆曲线上的点，验证C1是否满足椭圆曲线方程，若不满足则报错并退出
    global l
    h = 1  # 设定h值
    C_pad = ''
    if len(C) % 2 != 0:  # 如果C长度为奇数，进行填充
        C_pad = "0" + C
    print("C_pad:", C_pad)
    C_bytes = bytes.fromhex(C_pad)  # 从十六进制转换为字节
    print("C_bytes:", C_bytes)
    C1_length = 2 * l + 1  # C1长度
    C1_hex_length = 2 * C1_length
    C1_bytes = C_bytes[:C1_length]  # 提取C1
    print("C1_HEX:", C_pad[:C1_hex_length])
    C1_point = bytes_to_point(C1_bytes, 0)  # 将C1转换为椭圆曲线点

    # 计算椭圆曲线点S=[h]C1，若S是无穷远点，则报错并退出；
    S = EC_scalar_multiple(C1_point, h)
    if EC_scalar_add(S, G) == G:  # 检查S是否为无穷远点
        raise Exception("S是无穷远点")

    # 计算[dB]C1=(x2,y2)，将坐标x2、y2的数据类型转换为比特串
    point = EC_scalar_multiple(C1_point, dB)  # 计算私钥倍点
    print("[dB]C1_x2:", hex(point[0]))  # 打印x2坐标
    print("[dB]C1_y2:", hex(point[1]))  # 打印y2坐标
    x2 = point[0]
    y2 = point[1]
    x2_bytes = field_to_bytes(x2, 0)  # x2转换为字节
    x2_bits = bytes_to_bits(x2_bytes)  # x2转换为比特
    y2_bytes = field_to_bytes(y2, 0)  # y2转换为字节
    y2_bits = bytes_to_bits(y2_bytes)  # y2转换为比特

    C3_hex_length = 64  # C3长度
    C2_hex_length = len(C) - C1_hex_length - C3_hex_length + 1  # C2长度
    klen = 4 * C2_hex_length  # 计算t的长度

    # 计算t = KDF(x2 ∥ y2, klen)，若t为全0比特串，则报错并退出
    t = KDF(x2_bits + y2_bits, klen)
    if all(bit == '0' for bit in t):  # 检查t是否为全0
        raise Exception("KDF返回了全0比特串")
    t_hex = bits_to_hex(t)
    print("解密中的t:", t_hex)

    # 从C中取出比特串C2，计算M′= C2 ⊕ t；
    C2_int = int(C[C1_hex_length - 1:-C3_hex_length], 16)  # 提取C2
    print("C2:", C[C1_hex_length - 1:-C3_hex_length])
    M_m_int = C2_int ^ int(t_hex, 16)  # 计算明文
    M_m_str = hex(M_m_int)[2:]  # 转换为十六进制
    M_m_bytes = bytes.fromhex(M_m_str)  # 转换为字节

    # 计算u = Hash(x2 ∥ M′ ∥ y2)，从C中取出比特串C3，若u ̸= C3，则报错并退出
    s = x2_bytes + M_m_bytes + y2_bytes  # 合并数据
    hash_list = [i for i in s]
    u = sm3.sm3_hash(hash_list)  # 计算哈希值
    print("u:", u)
    C3 = C[-C3_hex_length:]  # 提取C3
    print("C3:", C3)
    if u != C3:  # 检查解密的有效性
        raise Exception("u != C3")
    print("解密结果为：", M_m_bytes.decode())  # 输出解密结果


if __name__ == "__main__":
    folder_path = r"test_data"
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        print(file_name)
        with open(file_path, 'r') as f:
            m = f.read()
            # 参数：
            p = 0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
            a = 0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
            b = 0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
            Gx = 0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
            Gy = 0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
            G = (Gx, Gy)
            n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
            l = ceil(log(p, 2) / 8)

            # key:

            dB = secrets.randbelow(n-2)
            P_B = EC_scalar_multiple(G, dB)
            print("公钥：", P_B)
            print("私钥：", dB)

            print("本次加密的明文：", m)
            C = SM2_encryption(m)
            SM2_decryption(C)
            print("\n\n\n\n\n")
