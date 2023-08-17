import discord
import discord.ext.commands as Commands 
import json






class Connect_Frp():
    def __init__(self):
    
        intents = discord.Intents.all()
        self.client = Commands.Bot(description="Aden",  case_insensitive = False, command_prefix= "!", 
        pm_help = False,intents = intents, help_command=Commands.DefaultHelpCommand()) #help_command = None, intents = intents
        with open('Cog\jsons\configuration.json',encoding='utf-8') as f:
            self.Token  = json.load(f)

    

    def Loading(self): 
        
        
            self.client.load_extension(name = "Cog.events")
            self.client.load_extension(name = "Cog.RolePLay")
            self.client.load_extension(name = "Cog.admin")
            self.client.load_extension(name = "Cog.duel")     
            self.client.load_extension(name = "Cog.economy")
            self.client.load_extension(name = "Cog.charachter")
            self.client.load_extension(name = "Cog.setting") 
        
       
            
  
    def Connect(self):
        try :
            self.client.run(self.Token['Token']) #Token of Bot    
        except Exception as e :
            print(e)

    