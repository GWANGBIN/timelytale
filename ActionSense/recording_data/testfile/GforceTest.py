import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(("127.0.0.1", 3478))

while True:

    bytesAddressPair = sock.recvfrom(2048)
    # data2, addr2 = sock2.recvfrom(1024)
    #
    message = bytesAddressPair[0].decode("utf-8")
    # data2= data2.decode().upper()

    # sock.sendto(message.encode(), bytesAddressPair[1])
    # clientMsg = "{}".format(message)
    # data = message.split()
    print('1111', bytesAddressPair)

    # # # Extract the device timestamp.
    # time_s = float(data[0])
    # #
    # # # Parse the pressure data.
    # data_lower = [float(x) for x in data[1:5]]
    # data_upper = [float(x) for x in data[5:9]]

sock.close()


