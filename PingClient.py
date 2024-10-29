import socket
import time
import random
import argparse

def ping_client(server_address, server_port):
     
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(0.6) 
    sequence_number = random.randint(10000, 20000)
   
    rtt_list = []
    acknowledged_packets = 0
    total_transmission_time = 0
    
    
    start_time = time.time()

    for i in range(15):
        current_sequence = sequence_number + i
        message = f"PING {current_sequence} {time.time()}"
        send_time = time.time()
        
        try:
            client_socket.sendto(message.encode(), (server_address, server_port))
            modifiedMessage, serverAddress = client_socket.recvfrom(2048)
            receive_time = time.time()

            rtt = (receive_time - send_time) * 1000  
            rtt_list.append(rtt)
            acknowledged_packets += 1

            print(f"PING to 127.0.0.1, seq={current_sequence}, rtt={int(rtt)} ms")

        except socket.timeout:
            print(f"PING to 127.0.0.1, seq={current_sequence}, rtt=timeout")
    
    total_transmission_time = time.time() - start_time
    
    client_socket.close()
    
    
    if rtt_list:
        min_rtt = min(rtt_list)
        max_rtt = max(rtt_list)
        avg_rtt = sum(rtt_list) / len(rtt_list)
    else:
        min_rtt = max_rtt = avg_rtt = 0

    packet_loss = ((15 - acknowledged_packets) / 15) * 100

    jitter = 0
    if len(rtt_list) > 1:
        jitter = sum(abs(rtt_list[i] - rtt_list[i-1]) 
                     for i in range(1, len(rtt_list))) / (len(rtt_list) - 1)
    

    print("...")
    print(f"Total packets sent: {15}")
    print(f"Packets acknowledged: {acknowledged_packets}")
    print(f"Packet loss: {int(packet_loss)}%")
    print(f"Minimum RTT: {int(min_rtt)} ms, Maximum RTT: {int(max_rtt)} ms, Average RTT: {int(avg_rtt)} ms")
    print(f"Total transmission time: {int(total_transmission_time * 1000)} ms")
    print(f"Jitter: {int(jitter)} ms")



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Ping")
    parser.add_argument('host', type=str)
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    ping_client(args.host, args.port)
