import numpy as np
import math
import argparse
import json

from helpers import *
 
##### хэш не работает для нечетных k!



# k = 1448 
# n = 2*k
# d = 137 
# w = 318
# boarder = 3*512*137 #len of c_part
# nlog = math.ceil(math.log(n,2))
# nlogn = nlog*n

# test_m = np.random.randint(0, 2, 15)

# buf = []
# fname = "../GFSR/H-prime"
# with open(fname, "r") as f:
#     words = f.read().split()
#     for word in words:
#         for bit in bin(int(word, base=16))[2:].rjust(32, '0'):
#             buf.append(int(bit))
# H = np.array(buf, dtype=int)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-path", required=True)
    parser.add_argument("--params-path", required=True)
    parser.add_argument("--message-path", required=True)
    parser.add_argument("--public-key-path", required=True)
    parser.add_argument("--sig-path", required=True)
    args = parser.parse_args()

    params = json.load(open(args.params_path))

    k = params["k"]
    n = params["n"]
    d = params["d"]
    w = params["w"]
    nlog = math.ceil(math.log(n,2))
    nlogn = nlog*n
    
    boarder = 3 * 512 * d #len of c_part

    H = read_matrix_hex(args.h_path, (k, k))

    sig = from_hex_file_to_bit_vector(args.sig_path) 

    y = from_hex_file_to_bit_vector(args.public_key_path) 
    
    c_part = sig[:boarder] 
    r_part = sig[boarder:]

    with open(args.message_path, "rb") as f:
        message = f.read()

    f_input = message + bit_vector_to_bytes(c_part)
    f = F(f_input, d) 

    last_r = 0
    for j in range(d):
        c0 = c_part[512*3*j:512*3*j+512]
        c1 = c_part[512*3*j+512:512*3*j+512*2]
        c2 = c_part[512*3*j+512*2:512*3*j+512*3]
        if f[j] == '0':
            r0 = r_part[last_r:last_r+nlogn]
            perm = bit_vector_to_permutation(r0, nlog)
            last_r = last_r + nlogn
            r1 = r_part[last_r:last_r+n] 
            last_r = last_r + n
            Hr1 = mul(H, r1) 
            #вычисляем хэш-значение 
            prec0 = bit_vector_to_bytes(r0) + bit_vector_to_bytes(Hr1)   
            prec1 = bit_vector_to_bytes(permute(r1, perm))   
            check0 = (h_512(prec0) == bit_vector_to_bytes(c0))
            if check0 == 0:
                print ("c0 went wrong for j = ", j)
            check1 = (h_512(prec1) == bit_vector_to_bytes(c1))
            if check1 == 0:
                print ("c1 went wrong for j = ", j)
            assert check0 * check1 != 0 
        if f[j] == '1': 
            r0 = r_part[last_r:last_r+nlogn]
            perm = bit_vector_to_permutation(r0, nlog)
            last_r = last_r + nlogn
            r1 = r_part[last_r:last_r+n] 
            last_r = last_r + n
            Hr1 = mul(H, r1) 
            #вычисляем хэш-значение 
            prec0 = bit_vector_to_bytes(r0) + bit_vector_to_bytes(Hr1^y)   
            prec2 = bit_vector_to_bytes(permute(r1, perm))   
            check0 = (h_512(prec0) == bit_vector_to_bytes(c0))
            if check0 == 0:
                print ("c0 went wrong for j = ", j)
            check2 = (h_512(prec2) == bit_vector_to_bytes(c2))
            if check2 == 0:
                print ("c2 went wrong for j = ", j)
            assert check0 * check2 != 0  
        if f[j] == '2': 
            r0 = r_part[last_r:last_r+n] 
            last_r = last_r + n
            r1 = r_part[last_r:last_r+n] 
            last_r = last_r + n  
            #вычисляем хэш-значение 
            prec1 = bit_vector_to_bytes(r0)
            prec2 = bit_vector_to_bytes(r0^r1)   
            check1 = (h_512(prec1) == bit_vector_to_bytes(c1))
            if check1 == 0:
                print ("c1 went wrong for j = ", j)
            check2 = (h_512(prec2) == bit_vector_to_bytes(c2))
            if check2 == 0:
                print ("c2 went wrong for j = ", j)
            weight = np.count_nonzero(r1)
            check3 =  (weight == w)
            if check3 == 0:
                print ("weight of secret key went wrong for j = ", j)
            assert check1 * check2 * check3 != 0 

    print("The signature does work!")

if __name__ == "__main__":
    main()
