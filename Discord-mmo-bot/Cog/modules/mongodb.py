
from pymongo import MongoClient

class database():
    def __init__(self):
 
        try:
            cluster = MongoClient("")
            db = cluster[""]
            self.User_Information = db['User_Information']
            self.Logs             = db['Logs']
            self.Rp_Channels      = db['Rp_Channels']
            self.Monsters         = db['Monsters']
            self.UserEnv          = db["User_Env"]
            self.Items            = db["Items"]
            self.Lonca            = db["Lonca"]
            self.Travel           = db["Travel"]
            self.userBattle       = db["userBattle"]
            self.Settings         = db["Settings"]
            
            print("bağlantı kuruldu...")
        except Exception as e:
            print("Databaseye bağlanılamadı...", e)

    async def allLonca(self):
        Loncadata = self.Lonca.find()
        Lonca = list()
        for element in Loncadata:
            Lonca.append(element["_id"])
        return Lonca
    

    async def allItems(self):
        itemdata = self.Items.find()
        Items = list()
        for element in itemdata:
            Items.append([element["_id"],element["name"]])
        return Items
    
    async def findSpecificItem(self, id):
        itemdata = self.Items.find_one({'_id' : id})
        return itemdata
    
    async def allMonsters(self):
        monstersData = self.Monsters.find()
        monsters = list()
        for element in monstersData:
            monsters.append(element["_id"])
        return monsters
    
    async def allUser(self):
        userData = self.User_Information.find()
        users= list()
        for element in userData:
            users.append(element["_id"])
        return users 
    
    async def allrpChannels(self):
        channelsData = self.Items.find()
        channels= list()
        for element in channelsData:
            channels.append(element["_id"])
        return channels
    
    def _insertItem(self,data):
        self.Items.insert_one(data)
    
    def _uptadeItem(self,item,data):
        self.Items.update_one(item,data)
    
    def _deleteItem(self,data):
        self.Items.delete_one(data)
    
    def _insertMonster(self,data):
        self.Monsters.insert_one(data)
    
    def _uptadeMonster(self,monster,newdata):
        self.Monsters.update_one(monster,newdata)
    
    def _deleteMonster(self,data):
        self.Monsters.delete_one(data)

    def _insertUser(self,data):
        self.User_Information.insert_one(data)
    
    def _insertUserEnv(self,data):
       self.UserEnv.insert_one(data)
    
    def _uptadeUserEnv(self,user,newData):
        self.UserEnv.update_one(user,newData)
        
    def _deleteuserEnv(self,data):
        self.UserEnv.delete_one(data)

    def _uptadeUser(self,user,newData):
        self.User_Information.update_one(user,newData)
    
    def _upatdeUserMany(self,user,newdata):
        self.User_Information.update_many(user,newdata)
    
    def _deleteEnv(self,data):
        self.UserEnv.delete_one(data)
    
    def _deleteUser(self,data):
        self.User_Information.delete_one(data)

    def _insertRpchannel(self,data):
       self.Rp_Channels.insert_one(data)

    def _uptadeCh(self,ch,data):
        self.Rp_Channels.update_one(ch,data)
    
    def _deleteRpchannel(self,data):
       self.Rp_Channels.delete_one(data)