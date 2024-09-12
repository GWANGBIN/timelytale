from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import socket
import re

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dr = webdriver.Chrome() # chrome driver 107 version
# dr = webdriver.Chrome(ChromeDriverManager().install())
# dr.get("http://192.168.75.51/live.html")
dr.get("http://TG03B-080200110631.local/live.html")
# dr.get("http://172.27.182.61/live.html")
time.sleep(1.5)

#eye_label = dr.find_element(By.XPATH, '/html/body/div[2]/div/table/tbody/tr[2]/td[1]/label[2]')
#eye_label.click()
play_button = dr.find_element(By.XPATH, '//*[@id="play"]')
play_button.click()

while True:
    unixTime = time.time()
    gazedata = dr.find_element(By.XPATH, '//*[@id="gazedata"]')
    gazedataList = gazedata.text.split("\n")
    # print(gazedataList)

    imudata = dr.find_element(By.XPATH, '//*[@id="imudata"]')
    # print(imudata.text)

    imudataList = imudata.text.split("\n")
    # print(imudata.text.split("\n"))

    dataSendList = []
    dataSendList.append(str(unixTime))
    for i in range(len(gazedataList)):
        # print(gazedataList[i])
        if "Time" in gazedataList[i]:
            data = re.findall("-?\d+.\d+", gazedataList[i])
            dataSendList.append('TimeWeb')
            dataSendList.append(data)

        if "gaze2d" in gazedataList[i]:
            # print(gazedataList[i])
            data = re.findall("-?\d+.\d+", gazedataList[i])
            dataSendList.append('gaze2d')
            # print(data)
            dataSendList.append(data)

        elif "gaze3d" in gazedataList[i]:
            # print(gazedataList[i])
            data = re.findall("-?\d+", gazedataList[i])
            # print(data)
            dataSendList.append('gaze3d')
            # print(data)
            dataSendList.append(data[1:4])

        elif "left pupil" in gazedataList[i]:
            # print(gazedataList[i])
            data = re.findall("-?\d+.\d+", gazedataList[i])
            dataSendList.append('leftpupil')
            # print(data)
            dataSendList.append(data)

        elif "right pupil" in gazedataList[i]:
            # print(gazedataList[i])
            data = re.findall("-?\d+.\d+", gazedataList[i])
            dataSendList.append('rightpupil')
            # print(data)
            dataSendList.append(data)

    for i in range(len(imudataList)):
        if "acc" in imudataList[i]:
            data = re.findall("-?\d+.\d+", imudataList[i])
            dataSendList.append('acc')
            # print(data)
            for j in range(len(data)):
                dataSendList.append(data[j])

        elif "gyro" in imudataList[i]:
            data = re.findall("-?\d+.\d+", imudataList[i])
            dataSendList.append('gyro')
            # print(data)
            for j in range(len(data)):
                dataSendList.append(data[j])

        elif "magneto" in imudataList[i]:
            data = re.findall("-?\d+.\d+", imudataList[i])
            dataSendList.append('magneto')
            # print(data)
            for j in range(len(data)):
                dataSendList.append(data[j])

        else:
            data = re.findall("-?\d+.\d+", imudataList[i])
            dataSendList.append(data)
        # elif val_magnetometer:
        #     dataSendList.append(imudataList[i])
        # elif val_gyroscope:
        #     dataSendList.append(imudataList[i])
    print('send data', dataSendList)
    sock.sendto(str(dataSendList).encode(), ("127.0.0.6", 5006))

