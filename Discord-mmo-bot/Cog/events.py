




import json
from types import NoneType
import discord
from discord.ext import commands, tasks

from Cog.modules.utils import*
from Cog.modules.mongodb import*
from datetime import datetime, timedelta
import time
from random import randint
#kanal silindiğinde databaseden silinen kanalı çıkar
#kayıtlı ve banner rolünün idsini al oradan bul, ismi değişebilir

class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('Cog\jsons\configuration.json',encoding='utf-8') as f:
            self.bot.configuration  = json.load(f)

        with open('Cog\jsons\player.json',encoding='utf-8') as f:
            self.bot.player  = json.load(f)
        
        with open('Cog\jsons\monster.json',encoding='utf-8') as f:
            self.bot.monster  = json.load(f)
        
        
        self.bot.db = database()
        self.bot.ownerID = self.bot.configuration['OwnerID']
        self.bot.rpusers = []
        self.bot.Npckillorder = []
        self.bot.PLayerkillorder = []
        self.bot.Voldi:object
        self.bot.LogChannel :object
        self.bot.SelectedItems:list = []
        
        

    @tasks.loop(hours=7)
    async def test(self):
        Channel = await self.bot.fetch_channel(855142180612079630)
        msgs = ["Emirhan neredesin canım","Selam millet durumlar nasıl?","Merhaba","Benimle minecraft oynamak isteyen var mı?","Sarp abi yayın aç","Emre hala komutlarımı anlamadın değil mi?"
                ,"Çok sıkıldım","Neyse film izliyeyim","Buralar çok ıssız","Eskiden ne rpler dönermiş buralarda","...",":)",":(","Hmmm..","Sohbetinizi bölüyorum ama yayınlar çok güzel",
                "Ona sorsan ben yokum...", "Artık geri döner mi bilmem, Trenler almış rayında giden", "Kaldığım yerler çok uzak sana artık.."]
        b = random.choice(msgs)
        await Channel.send(b)
    
    if test.current_loop % 2 == 0:
        test.change_interval(hours=10)
    else:
        test.change_interval(hours=4)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot {0.user} şuan online!!'.format(self.bot))
        

        guild = await self.bot.fetch_guild(self.bot.configuration['Guild'])
        self.bot.Voldi = discord.utils.get(guild.roles, id= self.bot.configuration['Warning Role'])
        self.bot.LogChannel = await self.bot.fetch_channel(self.bot.configuration['Log Channel'])
        await self.bot.LogChannel.send("Bot şuan online...")
        #activity = discord.Game(name= "En sevdiğim kardeşim Alisadır", type = 1)
        
   
        self.fill.start()
        self.pointorder.start()
        self.killOrder.start()
        self.Arrived.start()
        self.huntControl.start()
        self.LoseControl.start()
        self.EditingMarket.start()
        self.starvation.start()
        self.PvpShieldControl.start()
        #await self.bot.change_presence(status = discord.Status.do_not_disturb, activity = activity)
        await self.bot.change_presence(activity=discord.Streaming(name="Rednowtv Yayını", url='https://www.twitch.tv/rednowtv'))
    
    @tasks.loop(seconds=60.0)
    async def fill(self):
        UserInfo = self.bot.db.userBattle.find({},{"Hp":1,"MaxHp":1,"Enerji":1,"MaxEnerji":1})
        for element in UserInfo:
            id        = element["_id"]
            Hp        = element['Hp']
            maxHp     = element['MaxHp']
            Energy    = element['Enerji']
            MaxEnergy = element['MaxEnerji']

            if Hp < maxHp or Energy < MaxEnergy:
                settings = self.bot.db.Settings.find_one(FindCondition(id),{"FillingHp":1,"FillingEnergy":1})
                Hp += settings["FillingHp"]
                Energy += settings['FillingEnergy']
                if Hp > maxHp:
                    Hp = maxHp
                if Energy > MaxEnergy:
                    Energy = MaxEnergy
                
                data = {'$set' : {"Hp" : Hp,"Enerji": Energy}}
                self.bot.db.userBattle.update_one(FindCondition(id), data)
    
            else:
                continue
    
    @tasks.loop(minutes=10)
    async def starvation(self):
        starvationInfo = self.bot.db.userBattle.find({},{"starvation":1,"_id":1})
        for element in starvationInfo:
            id = element['_id']
            starvation = element['starvation']
            
            starvation -= self.bot.configuration['Starvation Decrease']
            if starvation < 0:
                starvation = 0
            data = {"$set" : {"starvation" : starvation}}
            self.bot.db.userBattle.update_one(FindCondition(id), data)
    
    
    @tasks.loop(seconds=10.0, reconnect = True)
    async def pointorder(self): 
        users= list()
        self.bot.rpusers = []
        usersInfo =  self.bot.db.User_Information.find({},{'Name':1, "Rp Point" :1})
        for element in usersInfo:
            id    = element["_id"]
            name  = element['Name']
            point = element['Rp Point']
            users.append((id,name,point))
        
        count = len(users)-1
        if count == -1:
            return
        if count == 0:
            
            self.bot.rpusers = users
            return

        self.bot.rpusers = await order(users,count)
        
        
     
   
 
    @tasks.loop(minutes = 5)
    async def EditingMarket(self):
        self.bot.SelectedItems:list = []
        TOTALSELECTEDITEM = self.bot.configuration['Total Selected Item']
        Items = self.bot.db.Items.aggregate([{ '$sample': { 'size': TOTALSELECTEDITEM } }])
        for item in Items:
            id    = item['_id']
            Name  = item['name']
            cost  = item['cost']
            self.bot.SelectedItems.append({"id": id,"Name":Name,"Cost":cost})
      
    

    
    @tasks.loop(seconds=15.0)
    async def Arrived(self):
        allTravelling = self.bot.db.Travel.find({},{'Travelling To':1,'Arrived Time':1})
        for element in allTravelling:
          
            Arrived_Time = element["Arrived Time"]
            Travelling_To = element["Travelling To"]
            User_id  = element["_id"]
            now = datetime.now() 
            
            if now >= Arrived_Time:
                Travel_Status = False
               
                data = {"$set" : {
                    "Travel Status" : Travel_Status,
                    "Current Location id" : Travelling_To
                }}
                self.bot.db.Travel.delete_one({"_id": User_id})
                self.bot.db._uptadeUser({"_id": User_id}, data)

                channel = await self.bot.fetch_channel(Travelling_To)
                user = await self.bot.fetch_user(User_id)
                await channel.send(f"{user.mention} vardınız",delete_after = 5)
                


    @tasks.loop(seconds=30.0)
    async def huntControl(self):
        huntLog = self.bot.db.Logs.find({"Type":0})
        now = datetime.now()
        for hunt in huntLog:
            TimeSetting = self.bot.db.Settings.find_one(FindCondition(hunt["id"]),{"Travel Time":1})
            if hunt["hunt time"] + timedelta(minutes = TimeSetting["Travel Time"]) <= now:
                self.bot.db.Logs.delete_one({"id": hunt["id"], "Type" : 0})

    @tasks.loop(seconds=60.0)
    async def LoseControl(self):
        LoseLog = self.bot.db.Logs.find({"Type":1})
        now = datetime.now()
        for log in LoseLog:
            TimeSetting = self.bot.db.Settings.find_one(FindCondition(log["id"]),{"Lose Duration":1})
            if log["Lose Time"] + timedelta(minutes = TimeSetting["Lose Duration"]) <= now:#settings
                self.bot.db.Logs.delete_one({"id" : log["id"], "Type" : 1})

    @tasks.loop(seconds=60.0)
    async def PvpShieldControl(self):
        LoseLog = self.bot.db.Logs.find({"Type":2})
        now = datetime.now()
        for log in LoseLog:
            TimeSetting = self.bot.db.Settings.find_one(FindCondition(log["id"]),{"PvpShield Duration":1})
            if log["Shield Time"] + timedelta(hours = TimeSetting["PvpShield Duration"]) <= now:#settings
                self.bot.db.Logs.delete_one({"id" : log["id"], "Type" : 2})
                PvpShield = {'$set': {"Pvp Shield": False}}
                self.bot.db.User_Information.update_one({"_id" : log["id"]},PvpShield)

    @tasks.loop(seconds=10.0)
    async def killOrder(self):
        self.bot.Npckillorder = []
        self.bot.PLayerkillorder = []
        userNpc= list()
        usersPlayer = list()
        usersInfo =  self.bot.db.User_Information.find({})
        for element in usersInfo:
            id = element["_id"]
            name = element['Name']
            npckill = element['Npc Kill Count']
            playerkill = element['Player Kill Count']
            
            userNpc.append((id,name,npckill))
            usersPlayer.append((id,name,playerkill))
        
        countNpc = len(userNpc)-1
        if countNpc == -1:
            return
        countPlayer = len(usersPlayer)-1
        if countNpc == 0 and countPlayer == 0:
            self.bot.Npckillorder = userNpc
            self.bot.PLayerkillorder = usersPlayer
            return     
    
        self.bot.Npckillorder = await order(userNpc,countNpc)
        self.bot.PLayerkillorder = await order(usersPlayer,countPlayer)
    
   
    
    
    @commands.Cog.listener()#burası kaldı
    async def on_guild_channel_delete(self,channel):
        rpchannel  = self.bot.db.Rp_Channels.find_one(FindCondition(channel.id))
        if type(rpchannel) == NoneType:
            return
       
        sorgu = {
            "Current Location": channel.name,
            "Current Location" : channel.id
        } 
        
        update = {
            "$set" : {
            "Current Location": "yok",
            "Current Location" : 0
            }
        }
        try :
            self.bot.db._uptadeSUerMany(sorgu,update)
            self.bot.db._deleteRpchannel(FindCondition(channel.id))
        except Exception as e :
            print(e)

   
    @commands.Cog.listener()
    async def on_message(self,msg):
        if msg.author == self.bot.user:
            return
        if msg.content.lower() == "gülüşlerin yabancı artık bana":
            await msg.channel.send(f"Bomboş vagonlar kırık camlar bavullar {msg.author.mention}")
        if msg.content.lower() == "ama bende biri vardı":
            await msg.add_reaction(":heart: ")
        
        userInfo = self.bot.db.User_Information.find_one(FindCondition(msg.author.id))  
    
        if type(userInfo) != NoneType:#düzelt
            self.lastUserCh = msg.channel.id
            channelid = list() 
            chInfo   = self.bot.db.Rp_Channels.find()
            for elem in chInfo:
                channelid.append(elem['_id'])
            
            if msg.channel.id in channelid:
                userInfo = self.bot.db.User_Information.find_one(FindCondition(msg.author.id),{'Rp Point':1,'Current Location id':1,'Travel Status':1})
                LoseLogs = self.bot.db.Logs.find_one({"id" : msg.author.id, "Type" : 1})
                Energy   = self.bot.db.userBattle.find_one(FindCondition(msg.author.id), {'Enerji':1})
                if type(LoseLogs) != NoneType:
                    losetime = LoseLogs["Lose Time"]
                    nowTime = datetime.now()
                    d2_ts = time.mktime(nowTime.timetuple())       
                    d1_ts = time.mktime(losetime.timetuple())
                    diff = int(d2_ts-d1_ts) / 60
                    diff = int(diff)
                    if diff== 0:
                        diff = 1       
                    await msg.channel.send(f"Bayıldınız rp yapamazsınız. {diff} dakika sonra tekrar deneyin " ,  delete_after=5)
                    await msg.delete()
                    return
                
                if Energy['Enerji'] == 0:
                    await msg.channel.send("Enerjiniz 0", delete_after = 4)
                    await msg.delete()
                    return
                
                point = userInfo['Rp Point']
                locationID = userInfo['Current Location id']
                travelStatus = userInfo['Travel Status']
                


                if  locationID != 0:
                    if msg.channel.id != locationID  or travelStatus == True:
                        #await msg.channel.send("Bu kanalda yoksunuz yada yoldasınız")
                        #await msg.channel.send(msg.content)
                        await msg.delete()
                        return

                words = [i for i in msg.content.split() if i[0:3] != "<@&" or i[0:3] !=  "<@&!" ]
                count = [len(i) for i in words]
                RpPoint = sum(count)
                point += RpPoint 
                uptade = {
                    "$set" : {
                        "Rp Point" : point,
                        "Current Location" : msg.channel.name,
                        'Current Location id' : msg.channel.id
                    }
                }
                self.bot.db._uptadeUser(FindCondition(msg.author.id),uptade)
        


    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send(f"hoşgeldiniz, sunucu hakkında bilgi almak istiyorsanız. sohbet kanalına yetkilileri etiketleyiniz.")#ufak bilgilendirme
        await member.add_roles(member.guild.get_role(703629301060337824))
        await member.edit(nick= f"Yeni üye | {member.guild.member_count+1}")
        
     
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):#Will be test
        userInfo = self.bot.db.User_Information.find_one({"_id" : member.id})
        
        Loncaid = userInfo["Lonca"][0]
        self.bot.db._deleteUser(FindCondition(member.id))#envanter ve loncya kayıtlı ise loncadan silinsin
        self.bot.db._deleteEnv(FindCondition(member.id))
        self.bot.db.Settings.delete_one(FindCondition(member.id))
        self.bot.db.userBattle.delete_one(FindCondition(member.id))

        if Loncaid != 0:
            lonca = self.bot.db.Lonca.find_one({"founderID": member.id})

            if type(lonca) != NoneType:
    
                lonca = self.bot.Lonca.find_one({"_id": Loncaid})
                members = lonca['Members']
                if len(members) > 1:

                    newFounderID = members[1]
                    newFounder = await self.bot.fetch_user(id)
                    newFoundername = newFounder.nick
                
                    data = {
                    "$pull" : {"Members" : {member.id}},
                    "$set"  : {"founderId": newFounderID, "FounderName": newFoundername}
                                }
                    self.bot.db.Lonca.uptade_one({"_id": Loncaid}, data)
                
                elif len(members) == 1:

                    self.bot.db.Lonca.delete_one(FindCondition(Loncaid))

    
            else :
                data = {
                    "$pull" : {"Members" : {member.id}}}
                
                self.bot.db.Lonca.uptade_one({"_id": Loncaid}, data)

          
        
    @commands.Cog.listener()
    async def on_disconnect(self):
        await self.bot.LogChannel.send(f"Bot aramızdan ayrıldı. {self.bot.Voldi.mention}")

    @commands.Cog.listener()
    async def on_application_command_error(self,ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            second = str(timedelta(seconds=  int(error.retry_after)))
            await ctx.respond(f"Lütfen {second} saniye sonra tekrar deneyin", ephemeral  =True)
        
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            nameData = {"$set": {'Name' : after.nick}}
            IsFounder = self.bot.db.Lonca.find_one({'FounderName': before.nick})
            if type(IsFounder) != NoneType:
                founderData = {'$set': {'FounderName' : after.nick}}
                self.bot.db.Lonca.update_one({'FounderName': before.nick}, founderData)
            self.bot.db.User_Information.update_one(FindCondition(after.id),nameData)
    



def setup(bot):
    bot.add_cog(Bot(bot))

