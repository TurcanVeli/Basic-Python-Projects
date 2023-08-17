

import random
from types import NoneType

from discord.commands import Option
import discord 
from discord.ext import commands
from Cog.modules.utils  import *
from discord.commands import slash_command



class RolePLay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.application_command()
        
        

    @slash_command(name = "kayıt", description = "Kayıt oluştur")
    async def sign(self, ctx,
    sınıf : Option(str, "3 Tane sınıf vardır. Biriniz seçiniz", choices = ["Barbarian","Wizard","Fighter","Ranger"], Required = True)):
        await ctx.defer()
        classes = self.bot.configuration['Classes']
        if sınıf not in classes:
            await ctx.respond("Lütfen 4 sınıftan birini seçiniz", ephemeral = True)
            return
        
        
        
        member = ctx.author
       
        skillName = "Yok"
        
        
       
        ac = 10
        if sınıf == classes[0]:#barbar
            skillName = "Yıkıcı Saldırı" #canı 1d10 kadar değeri vardır
            hp = 12
            uzmanlık = "Yakın"


        elif sınıf == classes[1]:#wizard
            skillName = "Şimşek" #Skill kullanıldığında zayıf düşmanlar bir tur saldıramaz. Damage 1d6 kadar artar
            hp = 10
            uzmanlık = "Menzilli"
        elif sınıf == classes[2]:
            skillName = "Zayıflat"#Skill kullanıldığında düşmanın acsini 1d6 düşürür.
            hp = 12
            uzmanlık = "Yakın"
        
        elif sınıf == classes[3]:
            skillName = "Körelt"
            hp = 12
            uzmanlık = "Yakın"
        else :
            await ctx.respond("Yanlış sınıf seçtiniz", ephemeral = True)
            return
         
        User_Data = { 
        "_id" : member.id,
        "Name" : member.nick,
        "Pvp Shield": False,
        "Uzmanlık" : uzmanlık,
        "Money": 0,
        "Str" : 8 ,
        "Dex" : 8,
        "Cons" : 8,
        "int" : 8,
        "Current Location id" :  self.bot.configuration['Default Start Location'],
        "Travel Status": False,
        "Title" : "Yok",
        "Rp Point" : 0,
        "Npc Kill Count" : 0,
        "Player Kill Count": 0,
        "Lonca" : [0, "yok"],
        "Stats Points" : 10,
        "proficiency": 1,
        "AtWar" : False
        }
        
        settingsData = {
            "_id" : member.id,
            "Travel Time": 5,
            "War Duration": 5,
            "Hunt Energy": 20,
            "War Energy": 30,
            "Travel Energy":10,
            "Size Inventory":10,
            "Xp Multiplier":1,
            "Gold Multiplier":1,
            "Lose Duration": 30,
            "Hunt Duration":5,
            "Skill Turn": 2,
            "LoncaSize": 3,
            "FillingHp":1,
            "FillingEnergy":2,
            "MaxEnergyLimit":100,
            "PvpShield Duration": 3

        }

        battle = {
            "_id" : member.id,
            "Sınıf" : sınıf,
            "Level" : 1,
            "skill" : skillName,
            "starvation": 100,
            "Max starvation": 100,
            "Exp" : 0,
            "MaxExp": 300,
            "Enerji": 100,
            "MaxEnerji": 100, 
            "Hp" : hp,
            "MaxHp": hp,
            "Damage" : "Yok",#itemin damage zarını alacak + bonus(str)
            "Armor Class": ac

        }

        #damage: weapon + bonus(str)ye göre belirlenir.
        #Savunma: kas göğüslük, kalkan: ağır zırh, 
        env = {
            "_id":member.id,
            "Name" : member.nick,
            "Items": [{
                "id": 1154,
                "Name": "Tahta Kılıç",
                "Having": 1,
                "Using": False
            }
           

            ],
            
            "Weapon": { "id": 0, "Name": "Boş"},
            "Kask": {"id": 0,"Name": "Boş"},
            "Body":{"id": 0,"Name": "Boş"},
            "Foot":{"id": 0, "Name": "Boş"}
    
        }
        
        try:
            self.bot.db.userBattle.insert_one(battle)
            self.bot.db._insertUser(User_Data)
            self.bot.db._insertUserEnv(env)
            self.bot.db.Settings.insert_one(settingsData)
            signRole = discord.utils.get(member.guild.roles, id=self.bot.configuration['SignRole']) 
            newMemberRole = discord.utils.get(member.guild.roles, id=self.bot.configuration['NotSignRole']) 
            await member.remove_roles(newMemberRole)
            await member.add_roles(signRole)
            
 
            await ctx.respond("{} kayıt edildi. Kullanıcı profili için /profil [member:opsiyonel] komutunu kullanın.".format(member.mention))
        except Exception as e:
            print(e)
    

        


    @slash_command(name = "killsıralama", description = "Sunucu kill sıralamasını gösterir")
    @commands.cooldown(1, 150, commands.cooldowns.BucketType.role)
    async def killeaderBoard(self, ctx):
        await ctx.defer()
       
        member = ctx.author
     
        
        users = self.bot.Npckillorder
        count = len(users)-1
        if count == 0:
            await ctx.respond("Tek bir kişi var", ephemeral = True)
            return    
        
        embedmessage = ""
        index = 1
        if count >= 10:
            count = 10
        embed = discord.Embed(title="**📝Sunucu Npc Öldürme Sıralaması**", color=0xff0505)
        embed.set_author(name = member.nick)
        while True:
            if users[count][0] == member.id:
                embedmessage += f"\n**#{index}**| **{users[count][1]}** = `{users[count][2]}`"
            else :
                embedmessage += f"\n#{index}| {users[count][1]} = `{users[count][2]}`"
            index+=1
            count-=1
            if count == -1:
                break
        embed.add_field(name= "**EN YÜKSEK ÖLDÜRMEYE SAHİP OYUNCULAR**",
        value= embedmessage)
        embed.set_footer(text="Veriler anlık sayılır")
        await ctx.respond(embed = embed, ephemeral = True)

    
    
    @slash_command(name = "rpsıralama", description = "Sunucu rp sıralamasını gösterir")
    @commands.cooldown(1, 200, commands.cooldowns.BucketType.role)
    async def rporder(self,ctx):#buraya random haftalık ödüller gelecek
        await ctx.defer()
        member = ctx.author
        embedmessage = ""
        index = 1
        users = self.bot.rpusers
        count = len(self.bot.rpusers)-1
        if count == 0:
            await ctx.respond("Tek bir kişi var", ephemeral = True)
            return 
        if count >= 10:
            count = 10
        embed = discord.Embed(title="**📝Sunucu Npc Rp Sıralaması**", color=0xff0505)
        embed.set_author(name = member.nick)
        while True:
            if users[count][0] == member.id:
                embedmessage += f"\n**#{index}**| **{users[count][1]}** = `{users[count][2]}`"
            else :
                embedmessage += f"\n#{index}| {users[count][1]} = `{users[count][2]}`"
            index+=1
            count-=1
            if count == -1:
                break
        embed.add_field(name= "**EN YÜKSEK RP PUANINA SAHİP OYUNCULAR**",
        value= embedmessage)
        embed.set_footer(text="Veriler anlık sayılır")
        await ctx.respond(embed = embed, ephemeral = True)

    @slash_command(name = "harita", description = "Bulunduğunuz konumdan nereye gidebileceğinizi gösterir")
    @commands.cooldown(1, 20, commands.cooldowns.BucketType.member)
    async def map(self,ctx):
        #await ctx.defer()
        channelId =  ctx.channel.id
        locationInfo = self.bot.db.Rp_Channels.find_one({"_id": channelId})
        if type(locationInfo) ==  NoneType:
            await ctx.respond("BU kanal rp kanalı değil", ephemeral =True)
            return
        
        Accesed_Channels = locationInfo["Accesed Channels"]
        if len(Accesed_Channels) == 0:
            await ctx.respond("Çıkmaz sokak!", ephemeral = True)
            return
        embed = discord.Embed(title="**Mini Harita**", color=0xff0505)
        channels = ""
        for index,channel in enumerate(Accesed_Channels):
            channels = channels + f" **{index+1}**. **{channel['Name']}**" + "\n"

        embed.add_field(name= "Bölgeler", value= channels)
        await ctx.respond(embed=embed, ephemeral = True)

        
       
    @slash_command(name = "loncakur", description = "20000 golda lonca kurarsınız")
    async def createlonca(self, ctx, 
    loncaname: Option(str,"Lonca ismi. 20 Karakterden fazla olamaz",  Required =True),
    descirption : Option(str, "Loncanın açıklamasını giriniz.", Required = False) = None):
        user = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id))
        

        if len(loncaname) > self.bot.configuration['SizeOFloncaname']:
            await ctx.respond(f"Lonca ismi {self.bot.configuration['SizeOFloncaname']} karakteri geçemez", ephemeral = True)
            return
        
    
        Money =  user['Money']
        Lonca =  user['Lonca']#Lonca list, first index present id second index present name
            
        if Lonca[0] != 0:
            await ctx.respond("Zaten bir loncaya üyesiniz. Önce ayrılın.",ephemeral = True)
            return

        
        if Money - self.bot.configuration['Money to Create Lonca'] < 0:
            await ctx.respond("Yetersiz Bakyiye.", ephemeral = True)
            return
        
        await ctx.defer()
        
        while True:
            Loncaid = random.randint(100,1000)
            allLonca = await self.bot.db.allLonca()
            if Loncaid not in allLonca:
                break
        
        if descirption == None:
            descirption = "Açıklama Yok"
        LoncaData = {
            "_id" : Loncaid,
            "Name" : loncaname,
            "Desciription" : descirption,
            "FounderName": ctx.author.nick,
            "founderID" : ctx.author.id,
            "Members" : [ctx.author.id]
        }
        
        try :
            Lonca = [Loncaid,loncaname]
            
            founderDataUptade = {
                "$set" : {
                "Money" : Money- 20000,
                "Lonca" : Lonca
                }
            }
            self.bot.db.Lonca.insert_one(LoncaData)
            self.bot.db._uptadeUser(FindCondition(ctx.author.id), founderDataUptade)
        except Exception as e:
            await ctx.respond("Lonca oluşturulurken bir hata oluştu, yetkili ile iletişime geçiniz", ephemeral = True)
            return
        await ctx.respond(f"{loncaname} loncası {ctx.author.mention} tarafından kuruldu.")


    
    
    
    
    @slash_command(name = "uyeekle", description = "Lonacına üye ekleyin")
    async def addmember(self,ctx,
    member: Option(discord.Member,"Eklemek istediğiniz üyeyi giriniz", Required = True)):
        await ctx.defer()
        Founderuser = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id))
        SizeLonca   = self.bot.db.Settings.find_one(FindCondition(ctx.author.id), {"LoncaSize"})
        Lonca = Founderuser["Lonca"]
        if Lonca[0] == 0:
            await ctx.respond(f"Sen bir loncaya ait değilsin. Önce lonca kur {ctx.author.mention}", ephemeral = True)
            return
     
        
        LoncaData = self.bot.db.Lonca.find_one({"_id": Lonca[0]})
       
        if ctx.author.id != LoncaData["founderID"] :
            await ctx.respond(f"Bu loncanın kurucusu olmadığın için üye ekleyemezsin {ctx.author.id}", ephemeral = True)       
            return
        membersofLonca = LoncaData["Members"]
    
      
        if member.id not in await self.bot.db.allUser():
            await ctx.respond("Lütfen rpye kayıtlı birini seçiniz", ephemeral = True)
            return
        
        memberData = self.bot.db.User_Information.find_one(FindCondition(member.id),{"Lonca":1})
        
       
        if memberData["Lonca"][0] != 0:
            await ctx.respond("Başka bir loncanın üyesini ekleyemezsin", ephemeral = True)
            return
        
        memberuptade = {
            "$set" :
            {
                "Lonca" : Lonca
            }
        }
        if len(membersofLonca) <= SizeLonca['LoncaSize']:
            membersofLonca.append(member.id)
        else : 
            await ctx.respond(f"Loncanızın üye sayısı toplam {SizeLonca['LoncaSize']+1}, başka kimseyi alamazsınız.",ephemeral = True)
            return
        
        LoncaUptade = {
            "$set" : {
            "Members" : membersofLonca
            }
        } 
        try :
            self.bot.db._uptadeUser(FindCondition(member.id), memberuptade)
            self.bot.db.Lonca.update_one({"_id": Lonca[0]}, LoncaUptade)
            await ctx.respond(f"{member.mention}, {Lonca[1]} loncasına {ctx.author.mention} tarafından eklendi.")


        except Exception as e :
            print(e)
            await ctx.respond(f"{member.mention} eklenirken ağ hatası oldu, eklenmeyenleri tekrar ekle. ya da yetkiliye ulaş", ephemeral = True )
            
   

    @slash_command(name = "uyecıkar", description = "Lonacınızdan üye çıkarın")
    async def deletemember(self,ctx, 
    member: Option(discord.Member,"Çıkartacağınız üyeyi seçiniz", Required = True)):
        await ctx.defer()
        Founderuser = self.bot.db.User_Information.find(FindCondition(ctx.author.id))
        for element in Founderuser:
            Lonca = element["Lonca"]
            if Lonca[0] == 0:
                await ctx.respond(f"Sen bir loncaya ait değilsin. Önce lonca kur {ctx.author.mention}",ephemeral = True)
                return
        
        LoncaData = self.bot.db.Lonca.find({"_id": Lonca[0]})
        for element in LoncaData:
            if ctx.author.id != element["founderID"] :
                await ctx.respond(f"Bu loncanın kurucusu olmadığın için üye çıkartamazsın {ctx.author.id}", ephemeral = True)       
                return

            membersofLonca = element["Members"]
        
        if ctx.author.id == member.id:
            await ctx.respond("kendini çıkartamazsın, istersen loncayı dağıt,sil", ephemeral = True)
            return
        
        memberData = self.bot.db.User_Information.find(FindCondition(member.id))
        
        for element in memberData:
            LoncaofMember = element["Lonca"]
            if LoncaofMember != Lonca or LoncaofMember[0] == 0:
                await ctx.respond(f"{member.mention} loncanızın üyesi değildir. {ctx.author.mention}", ephemeral = True)
                return

        LoncaofMember = [0,"Yok"]
        membersofLonca.remove(member.id)
        
        memberuptade = {
            "$set" : {
            "Lonca" : LoncaofMember
            }
        }
        
        Loncauptade = {
            "$set": {
                "Members" : membersofLonca
            }
        }
        try :
            self.bot.db._uptadeUser(FindCondition(member.id), memberuptade)
            self.bot.db.Lonca.update_one({"_id": Lonca[0]}, Loncauptade)
            await ctx.repsond(f"{member.mention}, {Lonca[1]} loncasından {ctx.author.mention} tarafından çıkartıldı.", ephemeral = True)
        except Exception as e:
            print(e)
    
    
    @slash_command(name = "ayrıl", description = "Loncadan ayrılın")
    async def leavelonca(self,ctx):
        await ctx.defer()
        user = self.bot.db.User_Information.find(FindCondition(ctx.author.id))
        for element in user:
            LoncaofMember = element["Lonca"]
            if LoncaofMember[0] == 0:
                await ctx.respond(f"Herhangi bir loncaya kayıtlı değilsiniz. {ctx.author.mention}", ephemeral = True)
                return
        
        LoncaData = self.bot.db.Lonca.find({"_id": LoncaofMember[0]})
        for element in LoncaData:
            membersOflonca = element["Members"]
            founderId = element["founderID"]
        
        if founderId  == ctx.author.id:
            await ctx.respond("Ayrılamazsınız loncayı silebilrsiniz", ephemeral = True)

        membersOflonca.remove(ctx.author.id)
        founder = self.bot.get_user(founderId)
        Loncauptade = {
            "$set" :
            {
                "Members" : membersOflonca
            }
        }
        oldLonca = LoncaofMember
        LoncaofMember = [0,"yok"]
        memberuptade = {
            "$set" : {
            "Lonca" : LoncaofMember
            }
        }
        try :
            self.bot.db._uptadeUser(FindCondition(ctx.author.id), memberuptade)
            self.bot.db.Lonca.update_one({"_id": oldLonca[0]}, Loncauptade)
            await ctx.respond(f"{ctx.author.mention}, {oldLonca[1]} loncasından ayrıldı. {founder.mention}")

        except Exception as e:
            print(e)


    @slash_command(name = "loncadagit", description = "Loncanızı dağıtın")
    async def deleteLonca(self,ctx):#Bot sahibi ve kurucular silebilir.
        await ctx.defer()
        
        LoncaInfo = self.bot.db.Lonca.find_one({"founderID" : ctx.author.id})
        
        if type(LoncaInfo) == NoneType:
            await ctx.respond("Herhangi bir loncanın kurucusu değilsiniz", ephemeral = True)
            return
        
        LoncaID = LoncaInfo["_id"]
        LoncaName = LoncaInfo["Name"]
            
        
        self.bot.db.Lonca.delete_one({"_id" : LoncaID})
        data = { 
            "$set" : {"Lonca.0" : 0, "Lonca.1" : "yok"}
           
        }
        self.bot.db._uptadeUser({"Lonca.0" : LoncaID}, data)
       
        await ctx.respond(f"{LoncaName} Loncası {ctx.author.mention} tarafından başarı ile dağıtıldı")




#will add sell npc to one location

def setup(bot):
    bot.add_cog(RolePLay(bot))

