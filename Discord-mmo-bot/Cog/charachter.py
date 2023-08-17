

from cgitb import text
import time
from datetime import datetime, timedelta
from Cog.modules.processInventory import*
from types import NoneType
import discord
from discord.ext import commands
from Cog.modules.utils import*
from datetime import datetime
from discord.commands import slash_command
from discord.commands import Option
class ch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command(name = "profil", description = "Kendi profilin ya da başkasınınkine bak")
    async def profile(self,ctx, 
    member: Option(discord.Member,"Profiline bakmak istediğiniz kişiyi ekleyiniz. Kendiniz için boş bırakın", Required = False) = None):
        await ctx.defer()
        if member == None :
            member = ctx.author
        
        userInfo        = self.bot.db.User_Information.find_one({'_id' : member.id})
        userBattleState = self.bot.db.userBattle.find_one({'_id' : member.id})
 
        sınıf = userBattleState["Sınıf"]
        hp = userBattleState["Hp"]
        maxHp = userBattleState["MaxHp"]
        enerji = userBattleState["Enerji"]
        maxEnerji = userBattleState["MaxEnerji"]
        money = userInfo["Money"]
        proficiency = userInfo['proficiency']
        uzmanlık = userInfo['Uzmanlık']
        pvpShield = userInfo['Pvp Shield']
        if pvpShield == True:
            pvpShield = 'Aktif'
        else:
            pvpShield = 'Aktif Değil'
        level = userBattleState["Level"]
        exp = userBattleState["Exp"]
        maxExp = userBattleState["MaxExp"]
        starvation = userBattleState["starvation"]
        maxstarvation = userBattleState["Max starvation"]
        ac  = userBattleState['Armor Class']
        str = userInfo["Str"]
        dex =   userInfo["Dex"]
        intl = userInfo["int"]
        cons = userInfo["Cons"]
        location = userInfo["Current Location id"]
        unvan = userInfo["Title"]
        point = userInfo["Rp Point"]
        Guild = userInfo["Lonca"][1]
        skill = userBattleState["skill"]
        Stats_Points = userInfo["Stats Points"]


        location = discord.utils.get(ctx.guild.channels, id=location)
        embed=discord.Embed(
                title="**{} PROFİL KARTI**".format(member.nick),
                timestamp=datetime.utcnow(), 
                color= discord.Color.random())
        embed.set_author(name = member.nick)
        #embed.set_thumbnail(url= member.avatar_url)
        embed.add_field(name = "**ÜNVAN**" , value= unvan, inline= True)
        embed.add_field(name = "**LONCA:**", value= Guild, inline= False)
        embed.add_field(name = "**SINIF:**", value= sınıf, inline= False)
        embed.add_field(name = "**YETENEK:**", value= skill, inline= False)
        embed.add_field(name = "**UZMANLIK:**", value= uzmanlık, inline= False)
        embed.add_field(name = "**PVP KALKANI:**", value= pvpShield, inline= False)
        
        embed.add_field(name ="**STATLAR**", value= f"**Can:** {hp}/{maxHp} :heart: \n**Level:** {level}\n**Exp:** {exp}/{maxExp}\n**Enerji:** {enerji}/{maxEnerji},\n**Açlık:** {starvation}/{maxstarvation}\n**Armor Class:**{ac}\n**Ustalık:** {proficiency}\n**Str:** {str}\n**Dex:** {dex}\n**Cons:** {cons}\n**Int:** {intl}")
    
        embed.add_field(name = "**DİĞER BİLGİLER**",
            value= f"**Parası:** {money} :coin:\n**Güncel Konum:** {location}\n**Rp Puanı:** {point}\n**Stat Puanı**: {Stats_Points}")
            
        await ctx.respond(embed=embed)


    @slash_command(name = "statpuanıdağıt", description = "Elinizde ki puanlarla stat puanlarını dağıtın")
    async def statsPoint(self,ctx,
    strenght: Option(int, "str statınıza vermek istiyorsanız puan giriniz", Required = False) = 0,
    intelligence: Option(int, "int statınıza vermek istiyorsnaız puan giriniz", Required = False) = 0,
    constitution: Option(int, "cons statınıza vermek istiyorsnaız puan giriniz", Required = False) = 0,
    dexterity: Option(int, "dex statınıza vermek istiyorsnaız puan giriniz", Required = False) = 0):
        #await ctx.defer()
        Total_InputPoints = strenght + intelligence + constitution + dexterity
        
        userInfo  = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id),{"Stats Points":1,"Str":1\
            ,"Dex":1,"int":1,"Cons":1})
   
        Stats_Point  = userInfo["Stats Points"]
        str = userInfo["Str"]
        dex = userInfo["Dex"]
        intl = userInfo["int"]
        cons = userInfo["Cons"]
        
         
           

        if Stats_Point < Total_InputPoints:
            await ctx.respond("Stat puanınız yetmiyor", ephemeral = True)
            return
        
        userBattleState  = self.bot.db.userBattle.find_one(FindCondition(ctx.author.id),{"Armor Class":1,"MaxHp":1})
        
        ac  = userBattleState["Armor Class"]
        maxHp = userBattleState["MaxHp"]
        str += strenght
        dex += dexterity
        if cons == 8:
            ac += 1
        else:
            ac -= bonus(cons)
        cons += constitution
        ac += bonus(cons)
        intl += intelligence
        maxHp += constitution
        Stats_Point -= Total_InputPoints
        update = {
            "$set" : {
                "Str" : str,
                "Dex": dex,
                "Cons" : cons,
                "int" : intl,
                
                "Stats Points": Stats_Point
            }
        }
        battleState_Update = {
            "$set": {
                "Armor Class" : ac,
                "MaxHp": maxHp
            }
        }
        self.bot.db.userBattle.update_one(FindCondition(ctx.author.id), battleState_Update)
        self.bot.db. _uptadeUser(FindCondition(ctx.author.id), update)
        await ctx.respond("Stat puanlarınız eklendi", ephemeral = True)

        
    @slash_command(name = "envanter", description = "Envanterine bak")
    @commands.cooldown(1, 50, commands.cooldowns.BucketType.user)
    async def inventory(self,ctx):
        await ctx.defer()
        member = ctx.author     
        env = self.bot.db.UserEnv.find_one(FindCondition(ctx.author.id),{"Items" :1,"_id":0})  
        sizeofInventory  =self.bot.db.Settings.find_one(FindCondition(ctx.author.id), {'Size Inventory':1})
        sizeofInventory = sizeofInventory['Size Inventory']
        Inventory = env["Items"]  
        itemInfotext: str = "" 
        weapons: str = ""
        if len(Inventory) != 0:
            for j,i in enumerate(Inventory):
                itemInfo = self.bot.db.Items.find_one((FindCondition(i["id"])))
                
                if itemInfo['part'] == "Weapon":
                    itemInfotext = f"Hasar zarı: **{itemInfo['damageDice']}**"
                elif itemInfo['part'] == "Food":
                    itemInfotext = f"Doygunluk: **{itemInfo['incstarvation']}**\n -Enerji artışı: **{itemInfo['incenergy']}**\n -Can Artışı:  **{itemInfo['inchp']}** "
                elif itemInfo['part'] == "Aksesuar":
                    itemInfotext = f"Test"
                else:
                    itemInfotext = f"Ac: **{itemInfo['buffac']}**"

                weapons = weapons + f" {j+1}. **{i['Name']}** -> {itemInfotext}.............{i['Having']}x" + "\n"
        else :
            weapons = "Envanteriniz Boş"
        embed=discord.Embed(
                title=":crossed_swords: :shield:  **{} ENVANTERİ**".format(member.nick),
                timestamp=datetime.utcnow(), 
                color= discord.Color.random())
        
        embed.add_field(name = "**İtemler:**", value = weapons)
        embed.set_footer(text= f'{len(Inventory)}/{sizeofInventory}')
        
        await ctx.respond(embed=embed, ephemeral  = True)
   
    @slash_command(name = "kuşan", description = "Envanterinde ki bir eşyayı kuşan ya da yemek ye")
    async def use(self,ctx,
    itemnumber: Option(int, "Sahip olduğunuz itemin sıra numarasını giriniz"),
    adet:Option(int,"Yemek yiyorsanız, kaç adet yiyebileceğinizi giriniz", min_value = 1, default  = 1, Required = False)):
        
        inventory  = self.bot.db.UserEnv.find_one(FindCondition(ctx.author.id))
        env = inventory["Items"]#list
        size = len(env)
        if itemnumber > size or itemnumber <= 0:
            await ctx.respond("Yanlış bir numara girdiniz", ephemeral = True)
            return 
        
        NewItemEnv = env[itemnumber-1]
        newItemID = NewItemEnv["id"]
        newItemData = self.bot.db.Items.find_one(FindCondition(newItemID))
        partOfNewItem = newItemData["part"]
        stateOfbattle = self.bot.db.userBattle.find_one(FindCondition(ctx.author.id))
        if partOfNewItem == "Food":
            incStarvation = newItemData['incstarvation']
            incHp         = newItemData['inchp']
            incEnergy     = newItemData['incenergy']
            Hp            = stateOfbattle['Hp']
            maxHp         = stateOfbattle['MaxHp']
            Energy        = stateOfbattle['Enerji']
            maxEnergy     = stateOfbattle['MaxEnerji']
            Starvation    = stateOfbattle['starvation']
            
            Hp += (incHp*adet)
            if Hp > maxHp:
                Hp = maxHp
            Energy += (incEnergy*adet)
            if Energy > maxEnergy:
                Energy = maxEnergy

            Starvation += (incStarvation*adet)
            if Starvation > 100:
                Starvation = 100
            
    
            data = {'$set': {
                "starvation": Starvation,
                "Hp": Hp,
                "Enerji" : Energy
                }
                }
            
            self.bot.db.userBattle.update_one(FindCondition(ctx.author.id), data)
            removeFood = Inventory(self.bot.db,ctx.author.id,newItemID,adet)
            result =  removeFood.removeItem()
            if result == True:
                await ctx.respond(f"{NewItemEnv['Name']} yediniz. Afiyet olsun", ephemeral = True)
                return
            else :
                await ctx.respond("Bir hata oluştu.")
                return


        
        part = inventory[partOfNewItem]#Dict
        
        if len(part) != 0: 
            for j,i in enumerate(env):
                if i["id"] == part["id"]:
                    OldItemid = part["id"]
                    OldItemIndex = j
                    break
                else:
                    OldItemid = 0
                    OldItemIndex = -1   
        else :
            OldItemIndex = 0
            OldItemid = -1
    
    
    
            
        if NewItemEnv["Using"] == False:
                        
            ItemUpdate = {"id": newItemID, "Name": NewItemEnv["Name"]}
            
            
            
            damage = stateOfbattle["Damage"]
            Armor_Class  = stateOfbattle["Armor Class"]
                
            #for (a, b), (c, d) in izip(iter1, iter2)

            if OldItemid != 0:
                oldItem = self.bot.db.Items.find_one(FindCondition(OldItemid))

                
                
                data = {"$set" : {f'{partOfNewItem}': ItemUpdate }}
                if partOfNewItem in ["Body", "Kask", "Foot"]:
                    Armor_Class = Armor_Class + newItemData["buffac"] - oldItem["buffac"] 
                
                elif partOfNewItem == "Weapon":
                    damage = newItemData["damageDice"]
                
                elif partOfNewItem == "Aksesuar":
                    pass
               
                Envdata = {"$set" : {
                        f"Items.{itemnumber-1}.Using": True,
                        f"Items.{OldItemIndex}.Using": False,
                        }}
                
            elif OldItemid == 0:
                
                
                data = {"$set" : {f'{newItemData["part"]}': ItemUpdate }}
                if partOfNewItem in ["Body", "Kask", "Foot"]:
                    Armor_Class = Armor_Class + newItemData["buffac"]
                
                elif partOfNewItem == "Weapon":
                    damage = newItemData["damageDice"]
                
                elif partOfNewItem == "Aksesuar":
                    pass

                Envdata = {"$set" : {
                f"Items.{itemnumber-1}.Using": True
            }}
            
            

            
            self.bot.db.UserEnv.update_one(FindCondition(ctx.author.id),data)
            update  = {
                "$set" : {
                    "Damage": damage,
                    "Armor Class" : Armor_Class
                }
            }
            self.bot.db.userBattle.update_one({"_id": ctx.author.id}, update)
            
            self.bot.db.UserEnv.update_one(FindCondition(ctx.author.id),Envdata)
            await ctx.respond(f"{NewItemEnv['Name']} kuşanıldı", ephemeral = True)
            return
        else:
            await ctx.respond(f"{NewItemEnv['Name']} zaten kullanıyorsunuz", ephemeral = True)

                    

    
    
    @slash_command(name = "lonca", description = "herhangi bir loncanın bilgisine ulaş")
    @commands.cooldown(1, 100, commands.cooldowns.BucketType.user)
    async def lonca(self,
    ctx, 
    loncaname: Option(str,"Bilgisine ulaşmak istediğiniz Loncanın ismini giriniz")):
        await ctx.defer()
        LoncaInfo  = self.bot.db.Lonca.find_one({"Name" : loncaname})
        if type(LoncaInfo) == NoneType: 
            await ctx.respond("yanlış isim giriniz ya da böyle bir lonca yok", ephemeral  = True)
            return
       
        Founderid  = LoncaInfo["founderID"]
        members  = LoncaInfo["Members"] #id list
        Desciription = LoncaInfo["Desciription"]

        Founder =  await self.bot.fetch_user(Founderid)
      
        membersStr = ""
        if len(members) ==1:
            membersStr = "Üye yok"
        else:
            for index,member in enumerate(members):#düzelt
                if member == ctx.author.id:
                    continue
                i = await self.bot.fetch_user(member)
                
                membersStr = membersStr + f"{index+1}. {i.mention}" + "\n"
            
         
        
        embed=discord.Embed(title=f"Lonca: {loncaname}", description = " ", color=0xff0a0a)
        embed.add_field(name = "Kurucu", value = f"**{Founder.mention}**", inline= False)
        embed.add_field(name = "Açıklama", value = f"{Desciription}", inline= False)
        embed.add_field(name = "Üyeler", value =f"{membersStr}", inline= False )
        await ctx.respond(embed = embed)
        
    
    
    @slash_command(name = "rppuanım", description = "Rp puanına bak")
    @commands.cooldown(1, 100, commands.cooldowns.BucketType.user)
    async def point(self,ctx):
        await ctx.defer()
        totalUsers = len(self.bot.rpusers)
        
        self.bot.rpusers.reverse()
        rpPoint = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id),{"Rp Point":1})
        for index,user in enumerate(self.bot.rpusers):   
            if user[0] == ctx.author.id:
                await ctx.respond(f"**{index+1}/{totalUsers}.** `puanınız:` **{rpPoint['Rp Point']}** {ctx.author.mention}")
                return
      
    
    
    @slash_command(name = "savaşgeçmişi", description = "Savaş geçmiişine bak")
    @commands.cooldown(1, 100, commands.cooldowns.BucketType.user)
    async def battleHistory(self,ctx):
        await ctx.defer()
        member = ctx.author
        totaluSers = len(self.bot.Npckillorder)
      
        for index,user in enumerate(self.bot.Npckillorder):
            if user[0] == member.id:
                npckill = user[2]
                killorder = index+1
                break
        for index,user in enumerate(self.bot.PLayerkillorder):
            if user[0] == member.id:
                pvpkill = user[2]
                killorder2 = index+1
                break
        
        await ctx.send(member.mention)
        embed = discord.Embed(title= f"Öldürme Sayıları {member.nick}")
        embed.add_field(name= f"{killorder}/{totaluSers}. **Yaratık öldürme sayısı:** ", value= npckill, inline= False)
        embed.add_field(name= f"{killorder2}/{totaluSers}. **Pvp öldürme sayısı:** ", value= pvpkill, inline= False)
        await ctx.respond(embed = embed)        

    
    @slash_command(name = "canım", description = "canına bak")
    @commands.cooldown(1, 100, commands.cooldowns.BucketType.user)
    async def showingHP(self,ctx):
        
        await ctx.defer()
        member = ctx.author
        userInfo = self.bot.db.userBattle.find_one(FindCondition(member.id), {"Hp":1,"MaxHp":1,"_id":0})
        bar, percent = do_bar(userInfo['MaxHp'],userInfo['Hp'],20)
        
        await ctx.respond(f"`{bar}` :heart:\n    {percent}\n{member.mention}")
        
    @slash_command(name = "enerjim", description = "enerjine bak")
    @commands.cooldown(1, 100, commands.cooldowns.BucketType.user)
    async def showingenergy(self,ctx):
        await ctx.defer()
        member = ctx.author
        userInfo = self.bot.db.userBattle.find_one(FindCondition(member.id), {"Enerji":1,"MaxEnerji":1,"_id":0})
        bar, percent = do_bar(userInfo['MaxEnerji'],userInfo['Enerji'],20)
      
        await ctx.respond(f"`{bar}` :zap:\n    {percent}\n{member.mention}")
    
    @slash_command(name = "açlık", description = "açlığına bak")
    @commands.cooldown(1, 100, commands.cooldowns.BucketType.user)
    async def showingstaravtion(self,ctx):
        await ctx.defer()
        member = ctx.author
        userInfo = self.bot.db.userBattle.find_one(FindCondition(member.id), {"starvation":1,"_id":0})
        bar, percent = do_bar(100,userInfo['starvation'],20)
        await ctx.respond(f"`{bar}` :fork_and_knife:\n    {percent}\n{member.mention}")

    @slash_command(name = "xp", description = "Deneyim puanına bak")
    @commands.cooldown(1, 100, commands.cooldowns.BucketType.user)
    async def showingExp(self,ctx):
        await ctx.defer()
        member = ctx.author
        userInfo = self.bot.db.userBattle.find_one(FindCondition(member.id),{"Exp":1,"MaxExp":1,"_id":0})
        bar, percent = do_bar(userInfo['MaxExp'],userInfo['Exp'],20)
        await ctx.respond(f"`{bar}` :stars:\n    {percent}\n{member.mention}")
        

    @slash_command(name = "savaşprofili", description = "Kuşandığın itemlere bak ve armor clşass ve damagene")
    async def inuse(self,ctx):
        #await ctx.defer()
        userid = ctx.author.id
        ItemUsing = self.bot.db.UserEnv.find_one(FindCondition(userid))
        weapon = ItemUsing["Weapon"]
        kask = ItemUsing["Kask"]
        body = ItemUsing["Body"]
        foot = ItemUsing["Foot"]

        itemType = self.bot.db.Items.find_one(FindCondition(weapon["id"]), {"type":1})
        if type(itemType) == NoneType:
            typeOfItem = "Yok"
        else:
            typeOfItem = itemType['type']
      
        userBattleState = self.bot.db.userBattle.find_one(FindCondition(userid))
        damage  = userBattleState['Damage']
        ArmorClass = userBattleState['Armor Class']
        hp = userBattleState["Hp"]
        classOFuser = userBattleState['Sınıf']
        starvation = userBattleState['starvation']
        
  
        UserInfo  = self.bot.db.User_Information.find_one(FindCondition(userid))
        strenght = UserInfo['Str']
        if classOFuser in ["Barbarian","Ranger","Fighter"] and typeOfItem == "Yakın":
            proficiency = UserInfo['proficiency']
        elif classOFuser == "Wizard" and typeOfItem == "Menzilli":
            proficiency = UserInfo['proficiency']
        else :
            proficiency = 0
        embed=discord.Embed(
                title="   **{}**   ".format(ctx.author.nick),
                timestamp=datetime.utcnow(), 
                color= discord.Color.random())
        
        embed.add_field(name = "Kullandıkların", value = f"Silah: **{weapon['Name']}**\nKafa: **{kask['Name']}**\nGövde: **{body['Name']}**\nAyak: **{foot['Name']}**")
        embed.add_field(name = "Güçler", value=f"Can: **{hp}**\nDamage Zarı: **{damage} + ({bonus(strenght)} + {proficiency})**\nArmor Class: **{ArmorClass}**")
        if starvation <= 15:
            embed.add_field(name = "Zayıflık", value = "Açlığınız %15 in altında hasarın yarısını vurabilirsiniz")
        
        await ctx.respond(embed=embed, ephemeral = True)
    
    @slash_command(name = "nerdeyim", description = "Rpde hangi kanalda kaldığınızı öğrenin")
    @commands.cooldown(1, 100, commands.cooldowns.BucketType.user)
    async def location(self,ctx):
        #await ctx.defer()
        userLocation = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id),{"Current Location id":1})
        if userLocation["Current Location id"] != None:
            channel = await self.bot.fetch_channel(userLocation["Current Location id"])
            await ctx.respond(f"Şuanki konumunuz : {channel.mention}, {ctx.author.mention}", ephemeral = True)
        else :
            await ctx.respond(f"Herhangi bir kanalda rp yapmadınız.{ctx.author.mention}", ephemeral = True)
    
    @slash_command(name = "ara", description = "Bölgende kimleirn olduğunu gör")
    async def find(self,ctx):#yapılan x rpde bir atacak ve attığı belli bir süre logta kalacak
        UserInfo   = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id),{"Current Location id":1,"int":1,"Lonca":1})
        userEnergy = self.bot.db.userBattle.find_one(FindCondition(ctx.author.id),{"Enerji":1})
        huntenergy = self.bot.db.Settings.find_one(FindCondition(ctx.author.id),{"Hunt Energy":1})
        if userEnergy["Enerji"] <= huntenergy["Hunt Energy"]:
            await ctx.respond("Yeterli enerjiniz yok", ephemeral  = True)
            return
        huntInfo  = self.bot.db.Logs.find_one({"id" : ctx.author.id, "Type":0})
        if type(huntInfo) != NoneType:
            await ctx.respond("Şuan keşif yapamazsınız çünkü önceki keşfin süresi dolmadı", ephemeral  = True)
            return
        travelLog = self.bot.db.Travel.find_one(FindCondition(ctx.author.id))
        if type(travelLog) != NoneType:
            await ctx.respond("Şuan yoldasınız.", ephemeral = True)
            return
        
        LoseLogs = self.bot.db.Logs.find_one({"id" : ctx.author.id, "Type" : 1})
        if type(LoseLogs) != NoneType:
            await ctx.respond("Şuan baygınsınız. Keşif Avlanamazsınız", ephemeral = True)
            return
        await ctx.defer()
        location_id = UserInfo["Current Location id"]
        intelligence = UserInfo["int"]
        
        if location_id != ctx.channel.id:
            await ctx.respond("Bulunduğunuz rp kanalında keşif yapın", ephemeral = True)
            return
        
        resultHunterint = roll("1d20") + bonus(intelligence)
        CurrentChannel = self.bot.db.Rp_Channels.find_one(FindCondition(location_id), {"Monsters":1})
        OtherPlayers = self.bot.db.User_Information.find({"Current Location id":location_id},{"Dex":1,"Name":1,"Lonca":1,"AtWar":1,"Travel Status":1})
        players = []
        UserLoncaid = UserInfo['Lonca'][0]
        for player in OtherPlayers:
            dex = player['Dex']
            id = player['_id']
            if id == ctx.author.id:
                continue
            if UserLoncaid == player['Lonca'][0] and UserLoncaid != 0:
                continue
            if player['AtWar'] == True:
                continue
            if player['Travel Status'] == True:
                continue

            playersDex = roll("1d20") + bonus(dex)
            pvpShield = self.bot.db.Logs.find_one(FindCondition(player["_id"]))
            if type(pvpShield) != NoneType:
                continue
            
            if resultHunterint >= playersDex:
                playerlevel = self.bot.db.userBattle.find_one(FindCondition(player["_id"]),{'Level':1})
                players.append({"id": player['_id'],"Name": player['Name'],"Level": playerlevel['Level']})

        monstersInfos = []
        for Monster in CurrentChannel["Monsters"]:
            eachMonsterInfo  = self.bot.db.Monsters.find_one(FindCondition(Monster["id"]))
            
            if resultHunterint >= eachMonsterInfo["weight"]:
                monstersInfos.append({"id":Monster["id"], "Name": eachMonsterInfo["name"],"Size": eachMonsterInfo["size"], "Can zarı" : eachMonsterInfo["healt die"]})
        
        
        hunt_time = datetime.now()
        energyReduced  = {"$inc" : 
            {"Enerji" : -huntenergy["Hunt Energy"]}}
        self.bot.db.userBattle.update_one(FindCondition(ctx.author.id), energyReduced)
        targetM = ""
        targetP = ""
            
        
        HuntData = {
            "id" : ctx.author.id,
            "Type" : 0,
            "Cathed" :  monstersInfos,
            "CathedPLayers": players,
            "Location": ctx.channel.id,
            "hunt time": hunt_time
        }
        if len(monstersInfos) == 0:
            targetM = "Avlayacak yaratık bulamadınız"
        else:
            
            for j,i in enumerate(monstersInfos):
                targetM = targetM + f" **{j+1}**. **İsim**: {i['Name']}, **Size**: {i['Size']}, **Can zarı**: {i['Can zarı']}" + "\n"
        
        if len(players) == 0:
            targetP = "Avlayacak Kimseyi Bulamadınız"
        else:
            for j,i in enumerate(players):
                targetP = targetP + f" **{j+1}**. **İsim**: {i['Name']}, **Level**: {i['Level']}" + "\n"

        self.bot.db.Logs.insert_one(HuntData)
        embed=discord.Embed(
                title="**{} - Keşfettikleri - {}**".format(ctx.author.nick, ctx.channel.name),
                timestamp=datetime.utcnow(), 
                color= discord.Color.random())
        
        embed.add_field(name = "**Yaratıklar:**", value = targetM)
       
        embed.add_field(name="**Oyuncular:**", value = targetP, inline= False)
        
        embed.add_field(name = ":crossed_swords: **Yaratıklara Saldırmak için**", value="/saldır yaratığın numarası", inline= False)
        embed.add_field(name= ":crossed_swords:  **Oyunculara saldırmak için**", value="/Pvp oyuncunun numarası komutunu kullanın")
        await ctx.respond(embed = embed, ephemeral = True)
    
    @slash_command(name = "kaçdakikakaldı", description = "Yolculuğunuzun bitmesine kaç dakika kaldığını gösterir")
    async def hManyMinutesLeft(self,ctx):
        #await ctx.defer()
        userInfo = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id),{"Travel Status"})
     
        if userInfo["Travel Status"] == False:
            await ctx.respond("Yolculuğa çıkmadınız", ephemeral = True)
            return
        
        travelling_log = self.bot.db.Travel.find_one(FindCondition(ctx.author.id))
      
        Arrived_Time = travelling_log["Arrived Time"]
        TravvelingTo = travelling_log["Travelling To"]
        tochannel = discord.utils.get(ctx.guild.channels, id= TravvelingTo)
        nowTime = datetime.now()
       
     
        nowTime = datetime.now()
        d2_ts = time.mktime(nowTime.timetuple())       
        d1_ts = time.mktime(Arrived_Time.timetuple())
        diff = int(d2_ts-d1_ts) / 60       
        
        if diff >= 100 :
            await ctx.respond(f"{tochannel.name} vardınız", ephemeral = True)
            return
        await ctx.respond(f"{int(diff)} dakika sonra {tochannel.name} varıyorsunuz", ephemeral = True)


    @slash_command(name = "git", description = "Bulunduğunuz konumdan başka bir yere yolculuk etmenizi sağlar")
    @commands.cooldown(1, 50, commands.cooldowns.BucketType.user)
    async def travel(self,ctx, 
    tochannel: Option(discord.TextChannel, "Gideceğiniz kanalı seçiniz", Required = True)):
        UserInfo   = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id),{"Travel Status" :1,"Current Location id":1,"Enerji":1})
        userEnergyandLevel = self.bot.db.userBattle.find_one(FindCondition(ctx.author.id),{"Enerji":1, "Level":1})
        
        if UserInfo["Travel Status"] == True:
            await ctx.respond("Zaten yoldasınız", ephemeral = True)
            return
        LoseLog  = self.bot.db.Logs.find_one({"id" : ctx.author.id, "Type" : 1})
        Setting = self.bot.db.Settings.find_one(FindCondition(ctx.author.id),{"Travel Energy":1,"Travel Time":1})
        if userEnergyandLevel["Enerji"] <= Setting["Travel Energy"] :
            await ctx.respond("Yeterli Enerjiniz yok", ephemeral = True)
            return
        if type(LoseLog) != NoneType:
            await ctx.respond("Şuan baygınsınız hareket edemezsiniz", ephemeral = True)
            return
        

        currentChannel = ctx.channel
        tochannelInfo = self.bot.db.Rp_Channels.find_one(FindCondition(tochannel.id))
        if type(tochannelInfo) == NoneType:
            await ctx.respond("Lütfen bir rp kanalı giriniz", ephemeral = True)
            return

        CurrentChannelInfo = self.bot.db.Rp_Channels.find_one(FindCondition(currentChannel.id),{"Accesed Channels":1})
        if type(CurrentChannelInfo) == NoneType:
            await ctx.respond("Yanlış yerdesin", ephemeral  =True)
            return
            
        levelOFchannel = tochannelInfo['danger level']
        if levelOFchannel == 0:
            data = { "$set":
                {"Current Location id" : tochannel.id}
            }
            self.bot.db._uptadeUser(FindCondition(ctx.author.id),data)
            await ctx.respond("Varıldı.", ephemeral = True)
            return

        
        if (userEnergyandLevel['Level'] < self.bot.configuration['need level to travel'] and levelOFchannel == 3):
            await ctx.respond("Bu kanala gidemezsiniz çünkü leveliniz yetmiyor", ephemeral = True)
            return

        #await ctx.defer()
        


        accessedchannels = CurrentChannelInfo['Accesed Channels']
        for channel in accessedchannels:
            if channel["id"] == tochannel.id:
                if tochannel.id == UserInfo["Current Location id"]:
                    await ctx.respond("Şuan zaten gideceğiniz kanaldasınız?!", ephemeral = True)
                    return
                if tochannel.id == currentChannel.id or currentChannel.id != UserInfo["Current Location id"] :
                    await ctx.respond("Lütfen konumunuzdan bu komutu kullanın", ephemeral = True)
                    return
             
                addedTime = timedelta(minutes = Setting['Travel Time'])
                arrived_Time =  datetime.now() + addedTime
                 
             
                energy = userEnergyandLevel["Enerji"]
                
                energy-= Setting["Travel Energy"]
                if energy < 0: energy = 0

                uptade = {
                    "$set":
                    {
                        "Travel Status" : True
                    }
                }
                self.bot.db._uptadeUser(FindCondition(ctx.author.id),uptade)
                energyUpdate = {"$set" : {"Enerji" : energy}}
                self.bot.db.userBattle.update_one(FindCondition(ctx.author.id), energyUpdate)
                data = {
                    "_id" : ctx.author.id,
                    "Arrived Time": arrived_Time,
                    "Starting Channel": ctx.channel.id,
                    "Travelling To":  tochannel.id
                        
                }
            
                self.bot.db.Travel.insert_one(data)
                self.bot.db.Logs.delete_one({"_id" :ctx.author.id, "Type" : 0})#keşif logu silindi
                await ctx.respond(f"{tochannel.name}'a doğru yola çıkıldı. Tahmini varış süresi {Setting['Travel Time']} dakika", ephemeral = True)
   
                return

        await ctx.respond("Seçtiğiniz kanal gidiş yok. Haritaya bak", ephemeral = True)
        return


def setup(bot):
    bot.add_cog(ch(bot))