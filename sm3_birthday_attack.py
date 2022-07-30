import random
import time

IV = 0x7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e
t = [0x79cc4519, 0x7a879d8a]

def P0(X):
    return X^Move(X,9)^Move(X,17)

def P1(X):
    #print('type_X',type(X))
    return X^Move(X,15)^Move(X,23)

def T(i):
    if i>=0 and i<=15:
        return t[0]
    else:
        return t[1]    

def Move(a, k):
    #print('LLLLLLL_IIIIIII',OtoB(a, 32))
    #c
    res = list(OtoB(a, 32))
    #print('L_res',res)
    #c
    for i in range(k):
        temp = res.pop(0)
        res.append(temp)
    #print('L_res',res)
    return int(''.join(res), 2)

def Not(a):
    """
    非函数
    """
    a=OtoB(a,32)
    #print(type(a))
    result = ''
    for i in a:
        if i == '1':
            result = result + '0'
        if i == '0':
            result = result + '1'
    return int(result,2)
'''
def tobin(x,k):
    #print('tobin_x=',x)
    #print(type(x))
    x=int(x)
    t=(bin(x)[2:])
    #print('tobin_t=',t)
    for i in range(k-len(t)):
        t='0'+t
    #temp=''
    #for i in range(k):
    #    temp=temp+t[i]
    return t'''

"""
布尔函数FF GG
"""
def FF(x,y,z,j):
    if((j>=0)&(j<=15)):
        ans = x^y^z
    else:
        ans = (x&y)|(x&z)|(y&z)
    #print ('FF',ans)
    return ans

def GG(x,y,z,j):
    #print('xyz',x,y,z)
    if(j<=15):
        ans = x^y^z
    else:
        ans = (x&y)|(Not(x)&z)
    #print('GG',ans)
    return ans

def Expand(b):
    """
    消息拓展 done
    """
    w = []
    w1= []
    for i in range(16):
        w.append(int(b[i*32:(i+1)*32],2))
    #print('E_w_0',w)
    for j in range(16, 68):
        #print(type(Move(w[j-3],15)))
        #print(type(w[j-16]))
        temp=P1(w[j-16]^w[j-9]^Move(w[j-3],15))
        #temp = (P1(w[j-16]^w[j-9]^Move(w[j-3],15)^Move(w[j-13],7)))
        w.append(temp^Move(w[j-13],7)^w[j-6])
    #print('E_w_1',w)
    for j in range(64):
        t1=w[j]^w[j+4]
        w1.append(t1)
    return w,w1

def Compress(V,w,w1):
    """
    消息压缩
    """
    #print('VVVVV',V)
    a = A = int(V[0:32],2)
    b = B = int(V[32:64],2)
    c = C = int(V[64:96],2)
    d = D = int(V[96:128],2)
    e = E = int(V[128:160],2)
    f = F = int(V[160:192],2)
    g = G = int(V[192:224],2)
    h = H = int(V[224:256],2)
    #print('ABCDEFGH',A,B,C,D,E,F,G,H)
    num_max=2**32
    #print('AAAAAAA',A)
    #print('MMMMMMMMMM',Move(A,12))
    for i in range(64):
        #print(type(Move(A,12)))
        #print(type(E))
        ss1=Move((Move(A,12)+E+Move(T(i),i%32))%(2**32),7)
        ss2=ss1 ^ Move(A,12)
        #print(len(w))
        #print(w)
        #print('ss1',ss1)
        #print('ss2',ss2)
        tt1=(FF(A,B,C,i)+D+ss2+w1[i])%num_max
        tt2=(GG(E,F,G,i)+H+ss1+w[i])%num_max
        D=C
        C=Move(B,9)
        B=A
        A=tt1
        H=G
        G=Move(F,19)
        F=E
        E=P0(tt2)
    #res=[a^A,b^B,c^C,d^D,e^E,f^F,g^G,h^H]
    res=int(OtoB(A,32)+OtoB(b,32)+OtoB(c,32)\
         +OtoB(D,32)+OtoB(E,32)+OtoB(F,32)\
         +OtoB(G,32)+OtoB(H,32),2)
    #print(res)
    return res

def OtoB(a, k):
    #if(type(a)=="class 'list'"):
    ans = bin(a)[2:]
    #print('OtoB_ans',ans)
    for i in range(k-len(ans)):
        ans='0'+ans
    return ans

def Iteration(m):
    """
    消息迭代
    """
    #print('Iter_m=',m)

    length = len(m)
    
    n = length//512
    b = []
    #print('Iter_IV',IV)
    #temp=OtoB(IV)
    #print('htobiv=',temp)
    #print('temp',temp)
    #print('IIIIIIIIIII',OtoB(IV, 256))
    #print('tobin(temp,256)',tobin(temp,256))
    #b.append(tobin(temp,256))
    b.append(OtoB(IV,256))
    #print('bbbb',b)
    for i in range(n):
        #print('i',i)
        w,w1 = Expand(m[512*i:512*(i+1)])
        #c
        #print('w,w1',w,w1)
        #print(b)
        temp = Compress(b[i],w,w1)
        #print(type(temp))
        b.append(OtoB(temp,256))
    #print('bbbbbbbb',b)
    return b[n]

def Fill(text):
    """
    消息填充
    """
    text_bin = bin(text)[2:]
    for i in range(4):
        if (len(text_bin)%4!=0):
            text_bin='0'+text_bin
    # add 1
    length = len(text_bin)
    k=448-(length+1)%512
    if(k<0):
        k=k+512
    text_bin_add='1'+'0'*k+OtoB(length,64)
    text_bin=text_bin+text_bin_add
    return text_bin

def sm3(text):
    m=Fill(text)
    #print('sm3_text=',m)
    hex(int(m,2))
    result=hex(int(Iteration(m),2))[2:]
    return result
    
def birthday_attack(n):
    range_n=2**n
    temp_n=n//4
    for i in range(0,range_n):
        s1_random=random.randint(0,range_n)
        #print(s1_random)
        s2_random=random.randint(0,range_n)
        #print(s2_random)
        s1_temp=sm3(s1_random)[:temp_n]
        s2_temp=sm3(s2_random)[:temp_n]
        #print('s1_temp=',s1_temp)
        #print('\n')
        #print('s2_temp=',s2_temp)
        #print('\n')
        if (s1_temp == s2_temp):
            print("find collison.s1_temp=",s2_temp)
            return
        else:
            print("failed")
        
#def func():
if __name__=='__main__':
    time_start=time.time()
    n=16
    birthday_attack(n)
    time_end=time.time()
    print('time=',time_end-time_start)






    
