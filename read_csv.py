import threading

import numpy as np
import math
import time
import serial
import threading


port = 'COM4'
# baud = 921600                                                         # STM32
baud = 9600                                                             # 아두이노
ser = serial.Serial(port, baud, timeout=0.1)

# data = np.loadtxt('C:/Users/user/Desktop/ecmo_ai_apply_230105_a1_div0.csv', delimiter=',')
# data = np.loadtxt('C:/Users/user/Desktop/ecmo_ai_apply_230127_a2_div0.csv', delimiter=',')
data = np.loadtxt('C:/Users/user/Desktop/ecmo_ai_apply_230130_a3_div0.csv', delimiter=',')


data_diff = np.array(data[10::, 0], dtype='float32')
data_sac1 = np.array(data[10::, 1], dtype='float32')
data_sac2 = np.array(data[10::, 2], dtype='float32')
data_heart = np.array(data[10::, 3], dtype='float32')
data_ecmo = np.array(data[10::, 4], dtype='float32')





# sac1 전처리

i = 0
proc_sac1 = np.array([])

while 1:
    for j in range(1, 10):
        if data_sac1[i] >= 0.9 and data_sac1[i-j] < 0.5:
            data_sac1[i] = 1
        else:
            data_sac1[i] = 0

    # print(data_sac1[i])
    proc_sac1 = np.append(proc_sac1, data_sac1[i])

    i += 1

    if i >= len(data_sac1):
        break

# sac2 전처리

i = 0
proc_sac2 = np.array([])

while 1:
    for j in range(1, 10):
        if data_sac2[i] >= 0.9 and data_sac2[i-j] < 0.5:
            data_sac2[i] = 1
        else:
            data_sac2[i] = 0

    # print(data_sac2[i])
    proc_sac2 = np.append(proc_sac2, data_sac2[i])

    i += 1

    if i >= len(data_sac2):
        break

# heart_ai 전처리 * (np.where)

i = 0
proc_heart = np.array([])

while 1:
    if data_heart[i] >= 5:
        data_heart[i] = 1
        if data_heart[i] == data_heart[i - 1]:
            data_heart[i] = 0
        if data_heart[i] == data_heart[i - 2]:
            data_heart[i] = 0
        if data_heart[i] == data_heart[i - 3]:
            data_heart[i] = 0
        if data_heart[i] == data_heart[i - 4]:
            data_heart[i] = 0
        if data_heart[i] == data_heart[i - 5]:
            data_heart[i] = 0

    elif data_heart[i] < 10:
        data_heart[i] = 0

    proc_heart = np.append(proc_heart, data_heart[i])
    # print(proc_heart[i])

    i += 1

    if i >= len(data_heart):
        break

# ecmo_ai 전처리 * (np.where)

i = 0
proc_ecmo = np.array([])

while i < len(data_ecmo):
    if data_ecmo[i] >= 5:
        data_ecmo[i] = 1
        if data_ecmo[i] == data_ecmo[i - 1]:
            data_ecmo[i] = 0
        if data_ecmo[i] == data_ecmo[i - 2]:
            data_ecmo[i] = 0
        if data_ecmo[i] == data_ecmo[i - 3]:
            data_ecmo[i] = 0
        if data_ecmo[i] == data_ecmo[i - 4]:
            data_ecmo[i] = 0
        if data_ecmo[i] == data_ecmo[i - 5]:
            data_ecmo[i] = 0

    elif data_ecmo[i] < 10:
        data_ecmo[i] = 0

    proc_ecmo = np.append(proc_ecmo, data_ecmo[i])
    # print(proc_ecmo[i])

    i += 1

    if i >= len(data_ecmo):
        break


# Heart BPM 계산

# i = 0
# b = np.array([])
# while 1:
#
#     if i >= len(proc_heart):
#         # print(b)
#         break
#
#     if proc_heart[i] == 1:
#         j = i + 1
#         while 1:
#
#             if j >= len(proc_heart):
#                 break
#
#             if proc_heart[j] == 1:
#                 b = np.append(b, 60/((j-i)*0.016))
#                 break
#             j += 1
#     i += 1

# Heart bpm 출력 test
# k = 0
# while k < len(b):
#     print(b[k])
#     k += 1
#     if k >= len(b):
#         break

# ECMO BPM 계산

# i = 0
# e = np.array([])
# while 1:
#
#     if i >= len(proc_ecmo):
#         # print(e)
#         break
#
#     if proc_ecmo[i] == 1:
#         j = i + 1
#         while 1:
#
#             if j >= len(proc_ecmo):
#                 break
#
#             if proc_ecmo[j] == 1:
#                 e = np.append(e, 60/((j-i)*0.016))
#                 break
#             j += 1
#     i += 1

# ECMO bpm 출력 test
# k = 0
# while k < len(e):
#     print(e[k])
#     k += 1
#     if k >= len(e):
#         break


# heart_ECMO delay 계산, co/counter 판정__Ver.1


i = 0
j = 0
k = 0
k_save = 0
k_save2 = 0

flag_j = 0

bpm_len = 0

while 1:

    flag = 1

    var = 0

    if i >= len(proc_heart):

        break

    if proc_heart[i] == 1:

        if i > j:
            print("")                                               # j = i + 1로 생략되는 i 출력

        j = i + 1

        while 1:

            if j >= len(proc_heart) or flag == 0:
                break

            if bpm_len > 0 and j > k_save2 and proc_heart[j] != 1 and proc_ecmo[j] == 1:       # heart 한 펄스에 ecmo가 두번 찍힐 때
                print("co-pulsation, lag")
                flag_j = 1

            if proc_heart[j] == 1 and flag_j == 0:

                k = j

                while 1:

                    # bpm_str = str(b[i])

                    # data_serial_lead = "cp 60 1"
                    # data_serial_lag = "cp 60 2"

                    if k >= len(proc_ecmo) or flag == 0:
                        break

                    if k <= k_save:                                     # proc_ecmo[k]가 안찍혀있을 때
                        k += 1                                          # empty 출력 후 k값 중복 출력 방지

                    if k <= k_save2:                                    # heart와 ecmo가 다시 합쳐지는 구간에서
                        flag = 0                                        # proc_ecmo[k] == 1 중복 출력 방지

                        i = j

                        break

                    if proc_ecmo[k] == 1:

                        k_save2 = k

                        if (k - j) < round(3/10*(j - i)):
                            flag = 0
                            h_bpm = round(60/((j - i)*0.016))

                            print("co-pulsation_lead", h_bpm)
                            # byte_lead = bytes(data_serial_lead, 'utf-8')
                            # ser.write(byte_lead)
                            # ser.write(b'cp 60 1')
                            # time.sleep(5)

                            # ser.write(b'a')

                            ser.write(str(h_bpm).encode())
                            time.sleep(0.3)
                            ser.write("a".encode())                     # 아두이노 시리얼통신 테스트
                            time.sleep(0.3)
                            # print(k - i)

                            i = j

                            break

                        elif round(7/10*(j - i)) < (k - j) <= (j - i):
                            flag = 0
                            h_bpm = round(60/((j - i)*0.016))

                            print("co-pulsation_lag", h_bpm)
                            # byte_lag = bytes(data_serial_lag, 'utf-8')
                            # ser.write(byte_lag)
                            # ser.write(b'cp 60 2')
                            # time.sleep(5)

                            # ser.write(b'b')

                            ser.write(str(h_bpm).encode())
                            time.sleep(0.3)
                            ser.write("b".encode())                     # 아두이노 시리얼통신 테스트
                            time.sleep(0.3)

                            # print(k - i)
                            i = j

                            break

                        elif round(3/10*(j - i)) <= (k - j) <= round(7/10*(j - i)):
                            flag = 0
                            h_bpm = round(60/((j - i)*0.016))

                            # print("counter-pulsation")
                            print("stay", h_bpm)

                            # ser.write(b'c')

                            ser.write(str(h_bpm).encode())
                            time.sleep(0.3)
                            ser.write("c".encode())                     # 아두이노 시리얼통신 테스트
                            time.sleep(0.3)

                            # print(k - i)
                            i = j

                            break

                    elif (j - i) <= (k - j):                             # heart 한 펄스에 ecmo가 안찍힐 때
                        flag = 0

                        print("empty")
                        i = j
                        k_save = k
                        break

                    if flag == 1 and k_save < k:
                        print("")
                        k += 1

            if flag == 1:
                if j > k and j > k_save2 and flag_j == 0:                # j > k_save2를 추가
                    print("")                                            # heart 한 펄스에 ecmo가 안찍힐 때
                flag_j = 0                                               # ecmo beat가 밀려있는 경우 밀린 만큼 j 스킵
                j += 1

    if flag == 1:
        print("")
        i += 1



# activate by heart signal
#
# i = 0
# e_test = np.array([])
# while 1:
#
#     flag = 1
#
#     if i >= len(data_heart) or flag == 0:
#         # print(b)
#         break
#
#     if data_heart[i] == 1:
#
#         j = i
#
#         while 1:
#
#             if j >= len(data_heart) or flag == 0:
#                 # print(b)
#                 break
#
#             if j == i+9:
#                 print("1")
#                 flag = 0
#                 i = j+1
#                 break
#
#             print("0")
#             j += 1
#
#     if flag == 1:
#         # print(i)
#         print("0")
#         i += 1


"""-----------------------test_sin-----------------------"""

# i = 0
# j = 0
# hbpm_init = 0
# flag = 1
#
# while 1:
#
#     if data_heart[i] == 1:
#         j = i + 1
#         while 1:
#             # while 종료조건 : j 가 a 배열 길이보다 커지면 종료
#             if j >= len(data_heart):
#                 break
#             # a 배열 중 1인 값을 탐색
#             if data_heart[j] == 1:
#                 flag = 0
#                 hbpm_init = j - i
#                 # print(j-i)
#                 break
#             j += 1
#     i += 1
#     if flag == 0:
#         break
#
#
# i = 0
# j = 0
# k = 0
# l = 0
#
# sin = np.array([])
#
# while 1:
#
#     arr_x_range = np.linspace(0, 2 * np.pi, num=math.ceil(hbpm_init))
#     sin = np.append(sin, np.sin(arr_x_range[j]))
#
#     if i >= len(data_heart):
#         break
#
#     if data_heart[i] == 1:
#         k = i
#
#     if k > 0:
#         if sin[i] >= 0.99:
#
#             # print(i)
#
#             if (i - k) <= (0.3 * hbpm_init):
#                 hbpm_init += 0.3
#             elif (0.3 * hbpm_init) < (i - k) < (0.6 * hbpm_init):
#                 # hbpm_init = hbpm_init
#                 pass
#             elif (0.6 * hbpm_init) <= (i - k) < hbpm_init:
#                 hbpm_init -= 0.4
#             else:
#                 pass
#
#     # print(np.sin(arr_x_range))
#     # print(hbpm_init)
#
#     print(sin[i])
#
#     i += 1
#     j += 1
#
#     if j >= hbpm_init:
#         j = 0




