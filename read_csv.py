import datetime as dt
import csv
import pandas as pd
import numpy as np


# pre_time_h = "previous heart pulse time"
# now_time_h = "present heart pulse time"
#
#
# pre_time_e = "previous ecmo pulse time"
# now_time_e = "present ecmo pulse time"
#
#
# heart_period = now_time_h - pre_time_h
# heart_ecmo_delay = now_time_e - now_time_h
#
#
# if heart_ecmo_delay / heart_period < 20 lag
# if 20 < heart_ecmo_delay / heart_period < 30 stay
# if heart_ecmo_delay / heart_period > 30 lead

data = np.loadtxt('C:/Users/HW/Desktop/ecmo_ai_apply_230105_a1_div0.csv', delimiter=',')

data_diff = np.array(data[10::, 0], dtype='float32')
data_sac1 = np.array(data[10::, 1], dtype='float32')
data_sac2 = np.array(data[10::, 2], dtype='float32')
data_heart = np.array(data[10::, 3], dtype='float32')
data_ecmo = np.array(data[10::, 4], dtype='float32')


# sac1 전처리
i = 0

while i < len(data_sac1):
    for j in range(1, 10):
        if data_sac1[i] >= 0.9 and data_sac1[i-j] < 0.5:
            data_sac1[i] = 1
        else:
            data_sac1[i] = 0

    # print(data_sac1[i])
    i += 1

    if i > len(data_sac1):
        break

# sac2 전처리
i = 0

while i < len(data_sac2):
    for j in range(1, 10):
        if data_sac2[i] >= 0.9 and data_sac2[i-j] < 0.5:
            data_sac2[i] = 1
        else:
            data_sac2[i] = 0

    # print(data_sac2[i])
    i += 1

    if i > len(data_sac2):
        break

# heart_ai 전처리 * (np.where)
i = 0

while i < len(data_heart):
    if data_heart[i] >= 10 and data_heart[i] > data_heart[i-1]:
        data_heart[i-1] = 0
        data_heart[i] = 1
        if data_heart[i] == data_heart[i-1]:
            data_heart[i-1] = 0
            data_heart[i] = 1

    else:
        data_heart[i] = 0
    # print(data_heart[i])
    i += 1

    if i > len(data_heart):
        break

# ecmo_ai 전처리 * (np.where)
i = 0

while i < len(data_ecmo):
    if data_ecmo[i] >= 10 and data_ecmo[i] > data_ecmo[i-1]:
        data_ecmo[i] = 1
        if data_ecmo[i] == data_ecmo[i-1]:
            data_ecmo[i] = 0

    elif data_ecmo[i] < 10:
        data_ecmo[i] = 0
    # print(data_ecmo[i])
    i += 1

    if i > len(data_ecmo):
        break


# heart BPM 계산
# a = np.array([...])  # peak 위치에 1, 나머지에 0이 저장된 배열(array)
i = 0
b = np.array([])
while 1:
    # while 종료조건 : i 가 a 배열 길이보다 커지면 종료
    if i >= len(data_heart):
        # print(b)
        break
    # a 배열 중 1인 값을 탐색
    if data_heart[i] == 1:
        j = i + 1
        while 1:
            # while 종료조건 : j 가 a 배열 길이보다 커지면 종료
            if j >= len(data_heart):
                break
            # a 배열 중 1인 값을 탐색
            if data_heart[j] == 1:
                b = np.append(b, j-i)
                break
            j += 1
    i += 1

k = 1
while k < len(b):
    # print(60/(b[k]*0.016))
    k += 1
    if k >= len(b):
        break


# ECMO BPM 계산
# a = np.array([...])  # peak 위치에 1, 나머지에 0이 저장된 배열(array)
i = 0
e = np.array([])
while 1:
    # while 종료조건 : i 가 a 배열 길이보다 커지면 종료
    if i >= len(data_ecmo):
        # print(e)
        break
    # a 배열 중 1인 값을 탐색
    if data_ecmo[i] == 1:
        j = i + 1
        while 1:
            # while 종료조건 : j 가 a 배열 길이보다 커지면 종료
            if j >= len(data_ecmo):
                break
            # a 배열 중 1인 값을 탐색
            if data_ecmo[j] == 1:
                e = np.append(e, j-i)
                break
            j += 1
    i += 1

k = 0
while k < len(e):
    # print(60/(e[k]*0.016))
    k += 1
    if k >= len(e):
        break


# heart_ECMO delay 계산
i = 0
j = 0
k = 0
while 1:
    flag = 1
    if i >= len(data_heart):
        # print(b)
        break

    if data_ecmo[i] == 1:
        j = i

        while 1:

            if j >= len(data_ecmo) or flag == 0:
                break

            if data_heart[j] == 1:
                k = j + 1

                while 1:

                    if k >= len(data_ecmo) or flag == 0:
                        break

                    if data_ecmo[k] == 1:

                        if (j - i) < round(3/10*(k - i)) or (k - j) < round(3/10*(k - i)):
                            flag = 0
                            print("co-pulsation")
                            # print(k - i)
                            i = k
                            break
                        else:
                            flag = 0
                            print("counter-pulsation")
                            # print(k - i)
                            i = k
                            break
                    k += 1

            j += 1

    i += 1
