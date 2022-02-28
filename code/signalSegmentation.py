import numpy as np
from modelPredict import pred as yuce
from dataToh5 import tu as toTu
#import time

def get_win_ch_RMS(data,time,ch):
    temp = abs(int(data[time][ch]))
    result = pow(temp, 2)
    return result

def get_win_ch_SE(win_data,m,r):
    N = len(win_data)
    def _maxdist(x_i,x_j):
        return  max([abs(ua - va) for ua, va in zip (x_i,x_j)])

    def _phi(m):
        x = [[win_data[j] for j in range(i,i+m-1+1)] for i in range(N-m+1)]
        B = [(len([1 for x_j in x if _maxdist(x_i,x_j) <= r ])-1.0)/(N-m) for x_i in x]
        return (N-m+1.0)**(-1) * sum(B)

    temp = _phi(m)
    if temp == 0.0:
        temp += 1e-5
    return -np.log(_phi(m+1) / temp + 1e-5)

def win_ch_RMS(win_len,chs,data,time):
    result = [0,0,0,0,0,0,0,0]
    N = win_len
    for i in range(time,time+win_len):
        if i >= data.shape[0]:
            N = i-time
            break
        for j in range(chs):
            result[j] += get_win_ch_RMS(data,i,j)

    for k in range(chs):
        result[k] = np.sqrt(result[k]/N)
    return result

def win_ch_SE(win_len,chs,data,time,m):
    result = [0,0,0,0,0,0,0,0]
    if time + win_len >= data.shape[0]:
        return result
    for i in range(chs):
        win_data = data[time:time+win_len,i]
        # r= 0.2 * np.std(win_data,ddof = 1)
        r = 0.2
        result[i] = get_win_ch_SE(win_data,m,r)
    return result

def win_ch_RMS_SE(win_len,chs,data,time,m_se):
    win_zresult = 0
    RMS_result = win_ch_RMS(win_len,chs,data,time)
    # print(RMS_result)
    SE_result = win_ch_SE(win_len,chs,data,time,m_se)
    # print(SE_result)
    q = [0.035, 0.01, 0.02, 0.035, 0.225, 0.225, 0.225, 0.225]
    for i in range(chs):
        win_zresult += RMS_result[i] * SE_result[i]*q[i]
    return win_zresult

def extractActiveSegment(signal, win_len, chs, on_set, off_set, min_signal_len, result,model,m_se,win_overloap,input):
    # preprocess_time_start = time.perf_counter()
    start = 0
    end = 0
    for m in range(0,len(signal),win_overloap):
        RMS_SE_now = win_ch_RMS_SE(win_len, chs, signal, m, m_se)
        if start == 0:
            if RMS_SE_now>=on_set:
                start = m
                if m > 100:
                    return start,input
        else:
            if RMS_SE_now <= off_set:
                if (m-start) >= min_signal_len:
                    end = m
                    if start-win_overloap<0:
                        s = 0
                    else:
                        s = start-win_overloap
                    if end+win_overloap>len(signal):
                        e = len(signal)
                    else:
                        e = end+win_overloap
                    signal_res = signal[s:e]
                    signal_res = padding_signal(signal_res, signal_len=400, ch_len=chs)
                    if not signal_res is None:
                        toTu(signal_res)
                        input = yuce(model)
                        return end,input
                else:
                    continue
    if start ==0 and end==0:
        return len(signal),input

def padding_signal(data, signal_len, ch_len):
    signal = np.zeros((signal_len, ch_len), dtype=np.int64)
    if len(data) > signal_len:
        return None
    if len(data) <50:
        return None
    for j in range(ch_len):
        signal[0:data.shape[0], j] = data[:, j]
    return signal
