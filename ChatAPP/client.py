import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import simpledialog
import socket
import threading
import ast
import time
import json
from datetime import datetime

HOST  = '127.0.0.1'
PORT  = 9090


class Client():
    def __init__(self, host,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,port))
        msg = tk.Tk()
        msg.withdraw()
        self.nickname = tk.simpledialog.askstring('Nickname', 'Please choose a nickname', parent= msg)
        self.toWho  = 'all'
        if len(self.nickname) == 0:
            self.close()
            
        self.gui_done = False
        self.running = True
        gui_thread = threading.Thread(target=self.gui )
        recieve_thread = threading.Thread(target=self.receive )
        
        gui_thread.start()
        time.sleep(1.0)
        recieve_thread.start()
 
       
    
    def formattedTime(self):
        current_time = datetime.now()
        return current_time.strftime("%H:%M:%S")
    
    def write(self):
        msg = f"{self.MesseageEntry.get()}"
        if len(msg) != 0:
            priv = msg.split()
        
            if priv[0][0] == ':':
                message = {'message':' '.join(priv[1:]), 
                        'status': '202',
                        'toWho': priv[0][1:], 
                        'isonlineList': 'false', 
                        'isNickname':'false',
                        'timestamp': self.formattedTime()}
                self.toWho = priv[0][1:]
                            
            else:
                message = {'message':msg, 
                        'status': '202',
                        'toWho': 'all', 
                        'isonlineList': 'false', 
                        'isNickname':'false',
                        'timestamp': self.formattedTime()}
                
                self.toWho = priv[0][1:]
              
            data = json.dumps(message)    
            self.sock.send(bytes(data,encoding='utf-8'))
            self.MesseageEntry.delete(0, 'end')
        else:
            pass
           
            
    
    def receive(self):
        while self.running:
            try:
                
                msg = self.sock.recv(1024).decode('utf-8')
                msg = json.loads(msg)
                print(msg)
                if msg['status'] != '202':
                    assert ConnectionAbortedError
                    self.close()
                
                else:
                    if msg['isNickname'] == 'true':
                        
                        data = {
                            'message': self.nickname, 
                            'status': '202',
                            'toWho': 'all', 
                            'isonlineList': 'false', 
                            'isNickname':'true',
                            'timestamp': self.formattedTime()
                                }
                        
                        data = json.dumps(data)
                        self.sock.send(bytes(data,encoding='utf-8')) 
                      
                    
                    elif self.gui_done:
                        self.toWho = msg['toWho']
                        if msg['isonlineList'] == 'true':
                            users =  ast.literal_eval(msg['message'])
                            self.OnlineUserTextArea.config(state='normal')
                            self.OnlineUserTextArea.delete('1.0','end')
                            for i,user in enumerate(users):
                                self.OnlineUserTextArea.insert('end',f'{i+1}. {user}\n')
                            self.OnlineUserTextArea.config(state='disabled')
                         
                 
                        else:
                            self.text_area.config(state='normal')
                            self.text_area.insert('end', msg['message'])
                            self.text_area.yview('end')
                            self.text_area.config(state='disabled')
                  
                       
                        
                
            except ConnectionAbortedError:
                break
            
            except ValueError:
                print('Decoding JSON has failed')
                self.close()
                break
                
            except Exception as e:
                print(e)
                self.close()
                break
            
            

    
    def close(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)
    
    
    def gui(self):
        
        self.win = tk.Tk()
       

        self.win.geometry(f"650x550")
        self.win.title("Chat Room")
        self.first_frame = tk.Frame(self.win, bg="black")
        self.first_frame.pack(fill="both", expand=True)
      
        BG_GRAY = "#ABB2B9"
        FONT_BUTTON = "Helvetica 8"
        
    
        self.Title = tk.Label(self.first_frame,text=f'Chat Room - your username: {self.nickname}')
        self.Title.config(background='black', foreground='white', font=('arial 10 bold'))
        self.Title.grid(row=0,column=0 , pady= 1, padx=10, sticky='w')
        
        
        self.GuiedArea = tk.Label(self.first_frame,text='You can send private message with using:  :username message \n')
        self.GuiedArea.config(background='black', foreground='red', font=('Times New Roman', 10))
        self.GuiedArea.grid(row=3,column=0,sticky='w')
        
        self.text_area = st.ScrolledText(self.first_frame)
        
        self.text_area.grid(row=1,column = 0, pady=1,padx=1, sticky='W')
        
        self.text_area.config(background='black', foreground='green',    font = ("Times New Roman",
                                    10))
    

        
        
   
        self.OnlineText  = tk.Label(self.first_frame, text='ONLINE USERS', background='black', foreground='white')
        self.OnlineText.grid(row=0,column=2, sticky='w')
        self.OnlineUserTextArea = st.ScrolledText(self.first_frame)
        self.OnlineUserTextArea.grid(row=1,column=2, pady=30,padx=20, sticky='w')
        self.OnlineUserTextArea.config(background='black', foreground='white', font=("Times New Roman",
                                    10))
     


        #send message layer   
        self.MesseageEntry = EntryWithPlaceholder(self.first_frame,  self.toWho ,color='black')
        self.MesseageEntry.config(background='white',font = ("Times New Roman",
                                    16),cursor="tcross")
        self.MesseageEntry.grid(row=2,column=0,pady=5,padx=80)
        

                
        self.sendButton = tk.Button(self.MesseageEntry, text ="send", command = self.write,width=7,font=FONT_BUTTON, bg=BG_GRAY,)
        self.sendButton.place(x=175,y= 0)
        self.sendButton.config(background='blue', foreground='white')
        
        
        self.exitButton = tk.Button(self.first_frame, text= 'exit',command=self.close ,font=FONT_BUTTON, bg=BG_GRAY)
        self.exitButton.grid(row = 0,column=1, sticky='w',pady=2,padx=2)
        self.exitButton.config(background='red', foreground='white')
        

        self.gui_done  = True
        
        self.win.protocol("WM_DELETE_WIDNOW",self.close)
  
        self.win.mainloop()
    
    
    
    


class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder= "chat/all/", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.default_fg_color = color
        self['fg'] = self.default_fg_color
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)
        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)

    def foc_in(self, *args):
        if self.get() == self.placeholder:
            self.delete('0', 'end')

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
            



if __name__ == "__main__":
    Client(HOST,PORT)






