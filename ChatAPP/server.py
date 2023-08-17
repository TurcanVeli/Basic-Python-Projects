import socket
import threading
from datetime import datetime
import json
import time

HOST = '127.0.0.1'
PORT = 9090


class server:
    def __init__(self, host, port) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = list()
        self.nicknames = []
    

    def formattedTime(self):
        current_time = datetime.now()
        return current_time.strftime("%H:%M:%S")

    def broadcast(self,message,client = None):
        
        if message['isonlineList'] == 'true':
            data = json.dumps(
                {
                'message': message["message"],
                'status': '202',
                'toWho': "all",
                'isonlineList': 'true',
                'isNickname': 'false',
                'timestamp': self.formattedTime()
            }
                )

            for c in self.clients:
                c.send(bytes(data, encoding='utf-8'))
            
   
        
        elif message['toWho'] != 'all' and  message['toWho'] not in self.nicknames:
            data = json.dumps(
                {
                'message': f'(ERROR) This users not online\n',
                'status': '202',
                'toWho': 'all',
                'isonlineList': 'false',
                'isNickname': 'false',
                'timestamp': self.formattedTime()
            }
                )
            client.send(bytes(data, encoding='utf-8'))
        
        
        elif message['toWho'] != 'all' and message['toWho'] in self.nicknames:
            recv_Clinet = self.clients[self.nicknames.index(message['toWho'])]
            sender_Nickname = self.nicknames[self.clients.index(client)]
            data = json.dumps(
                {
                'message': f'({message["timestamp"]}) from {sender_Nickname} to you >  {message["message"]}\n',
                'status': '202',
                'toWho': message['toWho'],
                'isonlineList': 'false',
                'isNickname': 'false',
                'timestamp': self.formattedTime()
            }
                )
            
            data_sender = json.dumps(
                {
                'message': f'from you to {message["toWho"]} >  {message["message"]}\n',
                'status': '202',
                'toWho': message['toWho'],
                'isonlineList': 'false',
                'isNickname': 'false',
                'timestamp': self.formattedTime()
                }
            )
            recv_Clinet.send(bytes(data,encoding='utf-8'))
            client.send(bytes(data_sender, encoding='utf-8'))
            
        elif message['toWho'] == 'all':
            if message['status'] == '208':
                data = json.dumps(
                    {
                    'message': message['message'],
                    'status': '202',
                    'toWho': message['toWho'],
                    'isonlineList': 'false',
                    'isNickname': 'false',
                    'timestamp': self.formattedTime()
                    }
                )
                for c in self.clients:
                    c.send(bytes(data, encoding='utf-8'))
            elif message['status'] == '202':
                sender_Nickname = self.nicknames[self.clients.index(client)]
                data = json.dumps(
                    {
                    'message': f'({message["timestamp"]}) [{sender_Nickname}] {message["message"]}\n',
                    'status': '202',
                    'toWho': message['toWho'],
                    'isonlineList': 'false',
                    'isNickname': 'false',
                    'timestamp': self.formattedTime()
                    }
                )
                
                for c in self.clients:
                    c.send(bytes(data, encoding='utf-8'))
                
            

    def handle(self,client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                message = json.loads(message)
                self.broadcast(message, client)

            

            except Exception as e:
                print(e)
                index = self.clients.index(client)
                client.close()
                self.clients.remove(client)
                nickname = self.nicknames.pop(index)
                
                
                self.broadcast(
                    {
                    'message': f'({self.formattedTime()}) [{nickname}] has left the chat....\n',
                    'status': '208',
                    'toWho': 'all',
                    'isonlineList': 'false',
                    'isNickname': 'false',
                    'timestamp': self.formattedTime()
                
                }
                )
                time.sleep(0.5)

                self.broadcast({
                    'message': str(self.nicknames),
                    'status': '202',
                    'toWho': 'all',
                    'isonlineList': 'true',
                    'isNickname': 'false',
                    'timestamp': self.formattedTime()
                
                })
                break



    def receive(self):
        while True:
            try:
                client, adrr = self.server.accept()
                print(f"{adrr} just conneted...")
                data = json.dumps({
                    'message': 'none',
                    'status': '202',
                    'toWho': 'all',
                    'isonlineList': 'false',
                    'isNickname': 'true',
                    'timestamp': self.formattedTime()
                })
                
                client.send(bytes(data, encoding='utf-8'))
                ClientsMessage = client.recv(1024).decode('utf-8')     
                ClientsMessage = json.loads(ClientsMessage)
     
                
                
                self.nicknames.append(ClientsMessage['message'])
                self.clients.append(client)
            
                #!!Problem!!
                #Let's say you send 1000 bytes, then send 1000000 bytes, and the other side calls recv.
                # It might get 1000 bytes—but it just as easily might get 1001000 bytes, or 7, or 69102. 
                # There is no way to guarantee that it gets just the first send.
                
                
                self.broadcast({
                    'message': str(self.nicknames),
                    'status': '202',
                    'toWho': 'all',
                    'isonlineList': 'true',
                    'isNickname': 'false',
                    'timestamp': self.formattedTime()
                })
                time.sleep(0.5)       
          
                self.broadcast({
                    'message': 'has joined the chat..\n',
                    'status': '202',
                    'toWho': 'all',
                    'isonlineList': 'false',
                    'isNickname': 'false',
                    'timestamp': self.formattedTime()
                
                }, client)
                
                thread = threading.Thread(target=self.handle, args=(client,))
                thread.start()
            except Exception as e:
                print(e)
                continue



if __name__ == "__main__":

    print('server is running!!')
    s1 =  server(host=HOST, port=PORT)
    s1.receive()
