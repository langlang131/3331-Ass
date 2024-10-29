import socket
import time
import random

# Configuration
PING_COUNT = 15
TIMEOUT = 0.6  # Timeout in seconds (600 ms)
PORT = 12000   # Default port
BUFFER_SIZE = 1024

def ping_client(host, port):
    # Create UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)

    # Initialize statistics
    rtt_list = []
    packets_acked = 0
    start_time = time.time()
    random_seq_start = random.randint(10000, 20000)

    for seq in range(random_seq_start, random_seq_start + PING_COUNT):
        send_time = time.time()
        message = f"PING {seq} {int(send_time * 1000)}\r\n"
        
        try:
            # Send packet
            client_socket.sendto(message.encode(), (host, port))
            print(f"Sent: PING {seq} {int(send_time * 1000)}")

            # Wait for a response (RTT calculation)
            response, _ = client_socket.recvfrom(BUFFER_SIZE)
            receive_time = time.time()

            # Calculate RTT
            rtt = (receive_time - send_time) * 1000  # Convert to ms
            rtt_list.append(rtt)
            packets_acked += 1

            print(f"Received: {response.decode().strip()} RTT = {rtt:.2f} ms")

        except socket.timeout:
            # Packet lost (timeout)
            print(f"Ping to {host}, seq={seq}, rtt=timeout")

    # Calculate summary statistics
    end_time = time.time()
    total_transmission_time = (end_time - start_time) * 1000  # Total time in ms

    if rtt_list:
        min_rtt = min(rtt_list)
        max_rtt = max(rtt_list)
        avg_rtt = sum(rtt_list) / len(rtt_list)
        jitter = sum(abs(rtt_list[i] - rtt_list[i-1]) for i in range(1, len(rtt_list))) / (len(rtt_list) - 1)
    else:
        min_rtt = max_rtt = avg_rtt = jitter = 0

    # Packet acknowledgment percentage
    ack_percentage = (packets_acked / PING_COUNT) * 100

    # Display final report
    print("\n--- Ping statistics ---")
    print(f"Packets: Sent = {PING_COUNT}, Received = {packets_acked}, Lost = {PING_COUNT - packets_acked} "
          f"({100 - ack_percentage:.2f}% loss)")
    print(f"RTT: Minimum = {min_rtt:.2f} ms, Maximum = {max_rtt:.2f} ms, Average = {avg_rtt:.2f} ms")
    print(f"Total transmission time: {total_transmission_time:.2f} ms")
    print(f"Jitter: {jitter:.2f} ms")

    # Close the socket
    client_socket.close()

if __name__ == "__main__":
    # Example usage: python3 PingClient.py <host> <port>
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 PingClient.py <host> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])

    ping_client(host, port)

