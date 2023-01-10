import numpy as np
import pickle


# 학습모델 가져오기
save_path = r'C:\Users\HW\PycharmProjects\m-DDN2\ecmo_ai_model_221007.pickle'
with open(save_path, 'rb') as f:
    trainingdb = pickle.load(f)

w1 = trainingdb['heart']['w1']
w2 = trainingdb['heart']['w2']
w3 = trainingdb['heart']['w3']
w4 = trainingdb['ecmo']['w4']
w5 = trainingdb['ecmo']['w5']
w6 = trainingdb['ecmo']['w6']

b1 = trainingdb['heart']['b1']
b2 = trainingdb['heart']['b2']
b3 = trainingdb['heart']['b3']
b4 = trainingdb['ecmo']['b4']
b5 = trainingdb['ecmo']['b5']
b6 = trainingdb['ecmo']['b6']


def NDivision(arr, n, ref):
    outp = np.array([])
    for i in range(0, len(arr)):
        if i % n == ref:
            outp = np.append(outp, arr[i])
    return outp


def DNN(x, h1_w, h1_b, h2_w, h2_b, o_w, o_b):
    def Dnn_Relu(arr):
        for i in range(0, arr.shape[0]):
            if arr[i] < 0:
                arr[i] = 0
            else:
                pass
        return arr

    z1 = np.matmul(x, h1_w) + h1_b
    z1 = np.array(z1.reshape(z1.shape[0] * z1.shape[1]))
    z1 = Dnn_Relu(z1)
    z2 = np.matmul(z1, h2_w) + h2_b
    z2 = np.array(z2.reshape(z2.shape[0] * z2.shape[1]))
    z2 = Dnn_Relu(z2)
    z = np.matmul(z2, o_w) + o_b
    z = np.array(z.reshape(z.shape[0] * z.shape[1]))
    outp = np.zeros(len(z))
    outp[np.argmax(z)] = 1

    return outp


# DB 경로 지정
fpath = r'C:\Users\HW\PycharmProjects\m-DDN2'

for data_i in range(1, 2):

    # 파일 불러오기
    data = np.loadtxt(r'%s\a%s.csv' % (fpath, data_i), dtype='str', delimiter=',')

    # 파일 내 diff, sac1, sac2 구분
    data_diff = np.array(data[10::, 0], dtype='float32')
    data_sac1 = np.array(data[10::, 1], dtype='float32')
    data_sac2 = np.array(data[10::, 2], dtype='float32')

    for div_i in range(0, 1):
        # diff, sac1, sac2 각각 16분주 중 (div_i) 번째 분주 값 가져오기
        diff = NDivision(data_diff, 16, div_i)
        sac1 = NDivision(data_sac1, 16, div_i)
        sac2 = NDivision(data_sac2, 16, div_i)

        save_diff = np.array([])
        save_sac1 = np.array([])
        save_sac2 = np.array([])
        save_outp_h = np.array([])
        save_outp_e = np.array([])

        for train_i in range(0, len(diff)):

            # 진행상황 파악을 위한 print
            if train_i % 10 == 0:
                print(data_i, 15, div_i, 15, train_i, len(diff))

            # for문 종료조건
            if train_i + 125 > len(diff):
                break

            # diff 필요한 범위만 가져온 뒤 표준화
            diff_inp = diff[train_i:train_i + 125]
            save_diff_val = np.array(diff_inp)
            diff_inp_min = np.min(diff_inp)
            diff_inp_max = np.max(diff_inp)
            diff_inp = (diff_inp - diff_inp_min) / (diff_inp_max - diff_inp_min)

            # sac1 필요한 범위만 가져오기
            sac1_inp = sac1[train_i + 35:train_i + 125]
            save_sac1_val = np.array(sac1_inp)
            for sac_i in range(0, len(sac1_inp)):
                if sac1_inp[sac_i] >= 0.5:
                    sac1_inp[sac_i] = 1
                else:
                    sac1_inp[sac_i] = 0

            # sac2 필요한 범위만 가져오기
            sac2_inp = sac2[train_i + 35:train_i + 125]
            save_sac2_val = np.array(sac2_inp)
            for sac_i in range(0, len(sac2_inp)):
                if sac2_inp[sac_i] >= 0.5:
                    sac2_inp[sac_i] = 1
                else:
                    sac2_inp[sac_i] = 0

            # 입력데이터 합치기
            inp = np.hstack((diff_inp, sac1_inp, sac2_inp))

            # DNN 적용
            outp_h = DNN(inp, w1, b1, w2, b2, w3, b3)
            outp_e = DNN(inp, w4, b4, w5, b5, w6, b6)

            # DNN 출력값 중 마지막 값(파형 없음을 나타내는) 제거
            outp_h = np.array(outp_h[0:-1])
            outp_e = np.array(outp_e[0:-1])

            # 출력값 누적
            if train_i == 0:
                save_diff = np.array(save_diff_val)
                save_sac1 = np.hstack((np.zeros(35), save_sac1_val))
                save_sac2 = np.hstack((np.zeros(35), save_sac2_val))
                save_outp_h = np.hstack((np.zeros(65), outp_h, np.zeros(30)))
                save_outp_e = np.hstack((np.zeros(65), outp_e, np.zeros(30)))
            else:
                save_diff = np.append(save_diff, save_diff_val[-1])

                save_sac1 = np.append(save_sac1, save_sac1_val[-1])
                save_sac2 = np.append(save_sac2, save_sac2_val[-1])

                save_outp_h = np.append(save_outp_h, 0)
                save_outp_h[-60:-30] = save_outp_h[-60:-30] + outp_h

                save_outp_e = np.append(save_outp_e, 0)
                save_outp_e[-60:-30] = save_outp_e[-60:-30] + outp_e

        save_data = np.vstack((save_diff, save_sac1, save_sac2, save_outp_h, save_outp_e)).T
        np.savetxt(r'C:\Users\HW\Desktop\ecmo_ai_apply_230105_a%s_div%s.csv' % (data_i, div_i),
                   save_data, fmt='%s',
                   delimiter=",")