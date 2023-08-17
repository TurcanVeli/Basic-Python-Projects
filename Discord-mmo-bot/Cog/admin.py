
from types import NoneType

import discord 
from discord.ext import commands

from Cog.modules.utils import*
from Cog.modules.processInventory import*
from discord.commands import Option
from discord.commands import slash_command


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(hidden=True)
    async def logout(self, ctx):
        if ctx.author.id != self.bot.ownerID:
            await ctx.send("Bu komutu kullanamazsınız", delete_after = 10)
            return
        await ctx.send("Logging out")
        self.bot.running = False
        for shutdown in self.bot.shutdowns:
            await shutdown()
        await self.bot.logout()
    
   
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("{0:.2f} ms ".format(self.bot.latency))
    
    

    @slash_command(name = "setmoney", description = "Parayı istediğin miktara çekeresin")
    async def setmoney(self,ctx, 
    member: Option(discord.Member, "Parasını artıracağın kullanıcı", Required = True), 
    money: Option(int, "Artırma miktarı", min_value = 0,Required = True)):
        await ctx.defer()
        if money < 0  or money > 99999999:
            await ctx.respond("`Yanlış para değeri girdiniz`", )
            return
       
        updateUser = {
            "$set": {
                "Money" : money
            }
        } 
        self.bot.db._uptadeUser(FindCondition(member.id),updateUser)
        
        await ctx.respond(f"{member.mention} `parası {money} gold olarak ayarlandı.`")
            


    @slash_command(name = "addmoney", description = "Para eklersin")
    async def addmoney(self,ctx, 
    member: Option(discord.Member, "Parasını artıracağın kullanıcı", Required = True), 
    money: Option(int, "Artırma miktarı", Required = True)):
        await ctx.defer()
        if money > 99999999:
            await ctx.send("`Yanlış para değeri girdiniz`", delete_after = 3)
            return
       
        userMoney = self.bot.db.User_Information.find_one(FindCondition(member.id),{"Money":1})
        
        oldMoney = userMoney["Money"]
        updateUser = {
            "$set": {
                "Money" : oldMoney + money
            }
        } 
        self.bot.db._uptadeUser(FindCondition(member.id),updateUser)
        
        await ctx.respond(f"{member.mention} `, artık {oldMoney+money} golda sahip.`")

    @slash_command(name = "paraazalt", description = "kullanıcının parasını azaltır")
    async def reducemoney(self,
    ctx, 
    member: Option(discord.Member, "Parasını azaltacağın kullanıcı", Required = True), 
    money: Option(int, "Azaltma miktarı", Required = True)):
        await ctx.defer()
        userMoney = self.bot.db.User_Information.find_one(FindCondition(member.id),{"Money":1})
        oldMoney = userMoney["Money"]
        if oldMoney - money < 0 : oldMoney = 0
        updateUser = {
            "$set": {
                "Money" : oldMoney + money
            }
        } 
        self.bot.db._uptadeUser(FindCondition(member.id),updateUser)
        
        await ctx.respond(f"{member.mention}`, artık {oldMoney-money} golda sahip.`")




    @slash_command(name = "rpkanalıyap", description = "Rp kanalı yaparsın")
    async def setrpchannel(self,
    ctx,
    level: Option(int, "Rp kanalının derecesi", choices = [0,1,2,3], Required = True)):
        await ctx.defer()
        chData = {
           "_id" : ctx.channel.id,
           "name": ctx.channel.name,
           "danger level": level,
           "Accesed Channels" : [],
           "Monsters" : []
        }
        if level ==  4 :
            await ctx.respond("`Lütfen 0 ve 3 arasında level seçiniz.`",  ephemeral = True)
            return
        
        try : 
            self.bot.db._insertRpchannel(chData)
            await ctx.respond("`Rp kanalı olarak ayarlandı.`",  ephemeral = True)
        except Exception as e :
            await ctx.respond("`Rp kanalı ayarlanamadı bir kez daha deneyin`", ephemeral = True)
        
    @slash_command(name = "setacces", description = "Yolları belirlersin")
    async def setaccess(self,ctx,
        channel :Option( discord.TextChannel,"Başlangıç noktası", Required = True),
        tochannel: Option( discord.TextChannel,"Varış noktası", Required = True)):
        
        await ctx.defer()
        channelInfo = self.bot.db.Rp_Channels.find_one(FindCondition(ctx.channel.id))
        
        if type(channelInfo)  == NoneType:
            await ctx.respond("Bu kanal rp kanalı değil", ephemeral = True)
            return

        if type(self.bot.db.Rp_Channels.find_one(FindCondition(ctx.channel.id))) == None:
            await ctx.respond("Eklemek istediğiniz kanal rp kanalı değil")
            return
        data = {"id" :tochannel.id, "Name" : tochannel.name}
        update = {
            "$addToSet" : {
                "Accesed Channels" : data 
            }
        }
  
       
        self.bot.db.Rp_Channels.update_one(FindCondition(channel.id),update)
        data = {"id" :ctx.channel.id, "Name" : ctx.channel.name}
        update = {
            "$addToSet" : {
                "Accesed Channels" : data 
            }
        }
        self.bot.db.Rp_Channels.update_one(FindCondition(tochannel.id),update)
        
        await ctx.respond("Rota eklendi",ephemeral = True)

   


    @slash_command(name = "rpkanalısil", description = "Rp kanalının kaydını siler")
    async def unsetrpchannel(self,ctx):
        await ctx.defer()
        try :
            self.bot.db._deleteRpchannel(FindCondition(ctx.channel.id))
            await ctx.respond("Artık rp kanalı değil",ephemeral = True)
        except Exception as e :
            print(e)
            await ctx.respond("`Bir hata oldu. Bir kez daha deneyin`",ephemeral = True)
    
    @slash_command(name = "puansıfırla",description  = "Rp puanlarını ve Killeri resetler ödülleri dağıtırsın")
    async def resetpoint(self,ctx,
    ödül: Option(int,"ilk 10a dağıtılacak ödül miktarı", default = 2000, Required = False)):
        
        for index, user in enumerate(self.bot.rpusers):

            data = {"$inc" : {"Money" : ödül}
            }
            self.bot.db.User_Information.update_one(FindCondition(user[0], data))

            ödül -= 200
            if index == 9:
                break

        
        RppointReset = {"$set" : {"Rp Point" : 0, "Npc Kill Count" : 0,"Player Kill Count" : 0}}
        self.bot.db.User_Information.update_many({},RppointReset) 
   
    @slash_command(name = "kayıtsil", description = "tüm kayıtlarını siler")
    async def deletesign(self,ctx, member: discord.Member):
        await ctx.defer()
        if ctx.author.id != self.bot.ownerID:
            await ctx.respond("Yetkiniz yok")
            return

        userInfo = self.bot.db.User_Information.find_one({"_id" : member.id})
        
        Loncaid = userInfo["Lonca"][0]
        self.bot.db._deleteUser(FindCondition(member.id))#envanter ve loncya kayıtlı ise loncadan silinsin
        self.bot.db._deleteEnv(FindCondition(member.id))
        self.bot.db.Settings.delete_one(FindCondition(member.id))
        self.bot.db.userBattle.delete_one(FindCondition(member.id))
        if Loncaid != 0:
            lonca = self.bot.db.Lonca.find_one({"founderID": member.id})

            if type(lonca) != NoneType:
              
                lonca = self.bot.db.Lonca.find_one({"_id": Loncaid})
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

       
        
        
        
        signRole = discord.utils.get(member.guild.roles, id=957667937123196978) 
        newMemberRole = discord.utils.get(member.guild.roles, id=703629301060337824) 
        
        await member.remove_roles(signRole)
        await member.add_roles(newMemberRole)
        await ctx.respond(f"`Kullanıcı kaydı silindi` {member.mention}")

   

    @slash_command(name = "monster", description = "Yaratık oluştur.")
    async def addnpc(
    self,
    ctx,
    name: Option(str,"Yaratığın ismi", Required = True),
    size : Option(str,"Yaratığın boyutu", Required = True),
    armorclass : Option(int, "yaratığın armor classı", Required = True),
    strenght: Option(int, "Yaratığın Strsi", Required = True),
    int: Option(int, "Yaratığın inti", Required = True),
    dex: Option(int, "Yaratığın dexi", Required = True),
    cons: Option(int, "Yaratığın consusi", Required = True),
    healtydie: Option(str, "yaratığın can zarı", Required = True),
    attackname: Option(str,"Yaratğın saldırısının ismi", Required = True),
    damagedice: Option(str, "Hasar zarı. format: 1d6", Required = True) , 
    damagebonus: Option(int, "Hasar bonusu. Zorunlu değil", Required = False) = 0, 
    attackbonus: Option(int, "Saldırı bonusu. Zorunlu değil", Required = False ) =0, 
    weight: Option(int, "yaratığın çıkma olasılığı 1-100 arasında. 1 en nadir", Required= False) = 99,
    cr: Option(int,"yaratoğın crsi", Required = True) = 1
    ):#attack value will be dice pattern
        await ctx.defer()
        
        while True:
            id = random.randint(1,3000)
            monster  = self.bot.db.Monsters.find_one({"_id" : id})
            if type(monster) == NoneType:
                break
            
        attack = {'Name' : attackname, 'Damage Dice' : damagedice }
        data = {
            "_id" : id,
            "name" : name,
            "size" : size,
            "armor class": armorclass,
            "str" :strenght,
            "int": int,
            "dex": dex,
            "cons": cons,
            "healt die": healtydie,
            "Attacks" : [attack],
            "damageBonus" : damagebonus,
            "attackBonus" : attackbonus,
            "items" : [],
            "weight" : weight, #çıkma olaslığı
            "cr": cr
        }
        try :
            MonsterInfos = f"**id**: {id}\n**Name**: {name}\n**Cr**: {cr}\n**Ac**: {armorclass}\n**Str**: {strenght}\n**Dex**: {dex}\n**Int**: {int}\n**Cons**: {cons}\n**Can Zarı**: {healtydie}\n**Hasar Bonusu**: {damagebonus}\n**Saldırı Bonusu**: {attackbonus}" 
            self.bot.db._insertMonster(data)
            logEmbed = discord.Embed(title="Yaratık", description = "Yaratık Oluşturuldu", color=0xff0a0a)
            logEmbed.set_author(name = f"{ctx.author.nick}")
            logEmbed.add_field(name= "Yaratığın Özellikleri", value= MonsterInfos)

            
            await self.bot.LogChannel.send(embed = logEmbed)
            await ctx.respond("Oluşturuldu")
        except Exception as e :
            print(e)

    
    @slash_command(name = "skill", description = "Yaratığa skill eklersin.")
    async def addattack(self,
    ctx,
    id: Option(int, "Yaratığın idsini giriniz", Required = True), 
    attackname: Option(str, "Eklemek istediğiniz skilli giriniz", Required = True), 
    damagedice: Option(str,"Hasar zarını giriniz", Required = True)):
        await ctx.defer()
        Monster  = self.bot.db.Monsters.find_one(FindCondition(id),{"name":1,"Attacks":1})
       
        
        if type(Monster) == NoneType:
            await ctx.respond("Yaratık bulunamadı ya da idyi yanlış girdiniz",  ephemeral = True)
            return
        
        MonsterName = Monster["name"]
    
        Attack  = {'Name' : attackname, 'Damage Dice' : damagedice}
    
        update = {"$addToSet" : {'Attacks': Attack }}
        
        try :
            self.bot.db._uptadeMonster({"_id" : id}, update)
            await self.bot.LogChannel.send(f"{self.bot.Voldi.mention} {ctx.author.mention} tarafından {attackname} skilli eklendi -> İsim:**{MonsterName}** id: **{id}**")
            await ctx.respond("Eklendi")
        except Exception as e :
            print(e)



    @slash_command(name = "weapon", description = "evrene weapon ekle")
    async def weapon(self,
    ctx,
    name: Option(str, "İtemin ismi", Required = True),
    tip: Option(str, "menzilli? yakın?", Required = True, choices = ["Menzilli", "Yakın" ]),
    size: Option(str, "weapoun büyüklüğü", choices = ["Küçük", "Orta", "Büyük"], Required = True), 
    weight: Option(int,"itemin nadirliği. 1-100",min_value=1, max_value=100, Required = True), 
    damagedice: Option(str, "itemin hasar zarı", Required = True),
    cost: Option(int, "İtemin fiyatı", Required = True),
    rareness: Option(int,"İtemin nadirliği: 1 en nadir 5 sıradan",  min_value = 1, max_value = 5,Required = True)
   
    ):
        await ctx.defer()
    
        while True:
            id = random.randint(1,3000)
            item  = self.bot.db.Items.find_one({"_id" : id})
            if type(item) == NoneType:
                break
        
       
        itemdata = {
            "_id": id,
            "part": "Weapon",
            "name": name,
            "type": tip,
            "size": size,
            "cost" : cost,
            "damageDice": damagedice,
            "weight" : weight,
            "rareness": rareness
        }
        try :
            self.bot.db._insertItem(itemdata)
            await self.bot.LogChannel.send(f"{self.bot.Voldi.mention} {ctx.author.mention} Tarafından oluşturuldu;\n id : **{id}**\n İsim: **{name}**")
            await ctx.respond("Oluşturuldu")
        except Exception as e:
            print(e)
      
    @slash_command(name = "armor", description = "evrene armor ekle")#Sagu ile konuş
    async def defans(self,ctx, 
    name: Option(str, "Armorun ismi", Required = True), 
    weight: Option(int, "Nadirlik", Required = True,min_value=1, max_value=100),
    part: Option(str,"Hangi bölge", choices = ["Kask","Body","Foot"],Required = True),
    buffac: Option(int, "Armor classa katkısı?", Required = True),
    cost: Option(int, "İtemin fiyatı", Required = True),
    rareness: Option(int,"İtemin nadirliği: 1 en nadir 5 sıradan",  min_value = 1, max_value = 5,Required = True)):#item özellikleri : özellik
        await ctx.defer()
  
        while True:
            id = random.randint(1,3000)
          
            item  = self.bot.db.Items.find_one({"_id" : id})
            if type(item) == NoneType:
                break

       
        item = {
            "_id" : id,
            "name" : name,
            "part":  part,
            "buffac" : buffac,
            "cost" : cost,
            "weight" : weight,
            "rareness" : rareness
        }
        try :
            self.bot.db._insertItem(item)
            await self.bot.LogChannel.send(f"{self.bot.Voldi.mention} {ctx.author.mention} Tarafından eklendi;\n id : **{id}**\n İsim: **{name}**")
            await ctx.respond("Oluşturuldu")

        except Exception as e:
            print(e)


    @slash_command(name = "yemek", description = "evrene yemek ekle")
    async def food(self,
    ctx,
    name:Option(str, "aksesuarın ismi",Required = True),
    giderilecekaçlık:Option(int,"Azaltacağı açlık miktarını belirler", Required = True),
    cost: Option(int,"Yemeğin fiyatı",min_value = 1,Required = True),
    weight: Option(int, "Nadirlik", Required = True,min_value=1, max_value=100),
    rareness: Option(int,"İtemin nadirliği: 1 en nadir 5 sıradan", Required = True, min_value = 1, max_value = 5),
    incenerji: Option(int,"Eğer enerji yükseltecekse bir değer girin", min_value = 0,default = 0,Required = False),
    inchp: Option(int,"Eğer can yükseltecekse bir değer girin",min_value = 0, default = 0,Required = False)):
        await ctx.defer()
            
        while True:
            id = random.randint(1,3000)
            item  = self.bot.db.Items.find_one({"_id" : id})
            if type(item) == NoneType:
                break

        item = {
            "_id": id,
            "name": name,
            "part": "Food",
            "incstarvation": giderilecekaçlık,
            "incenergy":  incenerji,
            "inchp": inchp,
            "cost":cost,
            "rareness" :  rareness,
            "weight" : weight

        }
        self.bot.db._insertItem(item)
        await self.bot.LogChannel.send(f"{self.bot.Voldi.mention} {ctx.author.mention} Tarafından eklendi;\n id : **{id}**\n İsim: **{name}**")
        await ctx.respond("Oluşturuldu")


    
    @slash_command(name = "aksesuar", description = "evrene aksesuar ekle")
    async def aksesuar(self,
    ctx, 
    name:Option(str, "aksesuarın ismi",Required = True),
    buffxp: Option(int,"Ac buffı varsa değer gir", Required = False) = 0,
    buffgold: Option(int, "Hp buffı varsa değer gir", Required = True) = 0,
    luckofitem: Option(int,"damage buffı varsa bir değer girin", Required = False) =0):
       pass

    @slash_command(name = "envitemekle", description = "kullanıcıya item ekle")
    async def additemTouser(self,
    ctx,
    member:discord.Member, 
    itemid: Option(int, "eklemek istediğiniz itemin idsini giriniz", Required = True),
    adet: Option(int,"İtemin adedini giriniz",default = 1, Required =False)):
            await ctx.defer()
            HaveAddedItem = Inventory(self.bot.db,member.id, itemid, adet)
            result = HaveAddedItem.addItem()
            if result == True:
                await ctx.respond(f"{member.mention} kullanıcısına item başarı ile eklendi.")
                await self.bot.LogChannel.send(f"{self.bot.Voldi.mention}{ctx.author.mention} Tarafından kullanıcıya item eklendi;\n Kullanıcı İsmi : **{member.nick}**\nid: **{itemid}**")
            else:
                await ctx.respond("Bir hata oluştu tekrar deneyin")
            
    @slash_command(name = "kayıtlarısil",description = "Tüm kullanıcıların kaydını siler" )
    async def deleteallrecords(self,ctx):
        if ctx.author.id != self.bot.ownerID:
            await ctx.respond("Bu komutu sadece Viski kullanabilir!")
            return
        
        self.bot.db.User_Information.delete_many({})
        self.bot.db.userBattle.delete_many({})
        self.bot.db.Lonca.delete_many({})
        self.bot.db.UserEnv.delete_many({})
        self.bot.db.Settings.delete_many({})
        await ctx.respond("Tüm kayıtlar silindi")


    @slash_command(name = "envitemsil", description = "Kullanıcının itemini silersiniz")
    async def deleteitemfromuser(self,
    ctx,member: Option(discord.Member,"İtem silmek istediğiniz kullanıcı"),
    itemid: Option(int,"İtemin idsini giriniz", Required = True),
    adet: Option(int,"İtemin adedini giriniz",default = 1, Required =False)):
            await ctx.defer()
            HaveRemovedItem = Inventory(self.bot.db,member.id,itemid,adet)
            result = HaveRemovedItem.removeItem()
            if result == True:
                await ctx.respond(f"{ctx.author.mention} tarafından {member.mention} envanterinden  {adet}x item başarı ile silindi")
                await self.bot.LogChannel.send(f"{self.bot.Voldi.mention}{ctx.author.mention} Tarafından silindi;\n Kullanıcı İsmi : **{member.nick}**\n  id: **{itemid}**....{adet}x")
            else:
                await ctx.respond("Bir hata oluştu tekrar deneyin")

     

                    
                     
    
    
    @slash_command(name = "konumanpcekle", description = "Kanala yaratık eklersin")
    async def addnpctochannel(self,ctx,
    id: Option(int, "Canavarın idsi",Required = True),
    channel: Option(discord.TextChannel, "Eklemek istediğiniz rp kanalı", Required  = True)):
        await ctx.defer()
        monster = self.bot.db.Monsters.find_one(FindCondition(id),{"name":1})
        ChannelInfo = self.bot.db.Rp_Channels.find_one(FindCondition(channel.id),{"Monsters":1,"name":1})

        
        if type(monster) == NoneType or type(ChannelInfo) == NoneType:
            await ctx.respond("Yanlış bilgi girdiniz")
            return
        
        NameOfmonster        = monster["name"]
        MonsterDict          = {"id": id,"Name": NameOfmonster}
        if MonsterDict in ChannelInfo["Monsters"]:
            await ctx.respond("Bu kanala zaten yaratık eklendi. başka bir yaratık dene.")
            return
        updateChannelMonster = {"$push": {"Monsters" : MonsterDict}}
        
        self.bot.db.Rp_Channels.update_one(FindCondition(channel.id), updateChannelMonster)
        await self.bot.LogChannel.send(f"{self.bot.Voldi.mention}, {ctx.author.mention} Tarafından kanala yaratık eklendi;\n Kanal  ismi: **{ChannelInfo['name']}**\nEklenen yaratık  id: **{id}** ve isim: **{NameOfmonster}**")
        await ctx.respond("Eklendi")

    @slash_command(name = "npcyeitemekle", description = "yaratığın düşüreceği itemi eklersin")
    async def additemtoNpc(self,ctx,
    id: Option(int, "Canavarın idsi", Required = True),
    itemid: Option(int, "İtemin idsi", Required = True)):
        await ctx.defer()
        monster = self.bot.db.Monsters.find_one(FindCondition(id),{"name":1,"items":1})

        item = self.bot.db.Items.find_one(FindCondition(itemid))
        if  type(monster) == NoneType or type(item) == NoneType:
            await ctx.respond("Yanlış bilgi girdiniz")
            return

        NameOftheItem      = item["name"]
        ItemDict           = {"id": itemid,"Name":NameOftheItem}
        if ItemDict in monster["items"]:
            await ctx.respond("Bu item zaten yaratığa eklendi. Başka bir item dene.")
            return
        updateMonsterItems = {"$push" : {"items" : ItemDict}}
        
        self.bot.db.Monsters.update_one(FindCondition(id), updateMonsterItems)
        await self.bot.LogChannel.send(f"{self.bot.Voldi.mention}, {ctx.author.mention} Tarafından yaratığa item eklendi;\n yaratık id: **{id}** ve isim: **{monster['name']}\nEklenen item id: **{itemid}** ve isim: **{NameOftheItem}**")
        await ctx.send("Eklendi")

    
    @slash_command(name = "yaratıksil", description = "evrenden yaratık silersin")
    async def deletemonster(self,ctx,
    id: Option(int, "Canavarın idsi", Required = True)):
        await ctx.defer()
        try :
        
            name = self.bot.db.Monsters.find_one(FindCondition(id),{"name":1})
            yaratık = {"$pull" : {"Monsters" : {"id": id, "Name" : name['name']}}}
           
            find = {"Monsters" : {"$in": [{"id": id, "Name" : name['name']}]}}
            
            channels = self.bot.db.Rp_Channels.find(find)
            
            for i in channels:
                channelId = i['_id']         
                self.bot.db.Rp_Channels.update_one(FindCondition(channelId),yaratık)
              
            self.bot.db.Monsters.delete_one(FindCondition(id))
            await ctx.repsond("Yaratık silindi")
        
        except Exception as e:
            await ctx.respond("yaratık silinemedi",e)


def setup(bot):
    bot.add_cog(Moderation(bot))