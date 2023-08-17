#aş sat işlemleri, banka işlemleri burada



import discord
from discord.ext import commands
from datetime import datetime
from types import NoneType
from Cog.modules.utils import*
from discord.commands import slash_command
from Cog.modules.processInventory import Inventory as buyItem
from discord.commands import Option
import json
class economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.application_command()

    
    @slash_command(name = "para", description = "paranıza ya da başkasının parasına bakarsınız")
    @commands.cooldown(1, 50, commands.cooldowns.BucketType.user)
    async def money(self,ctx, 
    member: Option(discord.Member,"Parasına bakmak istediğiniz kişiyi giriniz, kendi paran için boş bırak") = None):
        await ctx.defer()
        existOrnot = False
        if member == None:
            member = ctx.author
        
        user = {
            "_id": member.id
            }
        try :
            userInfo = self.bot.db.User_Information.find(user)
        
            for element in userInfo:
                
                usermoney = element["Money"]
                existOrnot = True
            
            if existOrnot == False:
                await ctx.respond("Kullanıcı bulunamadı", ephemeral = True)
            await ctx.respond(f"`Para = {usermoney} gold` {member.mention}")
        
        except Exception as e:
            print(e)
           
    


    @slash_command(name = "goldgönder", description = "bir kullanıcıya gold gönder ")
    @commands.cooldown(1, 50, commands.cooldowns.BucketType.user)
    async def sendmoney(self,ctx, 
    member: Option(discord.Member, "Para göndereceğiniz kişi", Required = True) , 
    money : Option(int, "Göndereceğiniz Para miktarı", min_value = 1,Required = True) ):
        await ctx.defer()
        if member.id == ctx.author.id:
            await ctx.respond("kendinize para gönderemezsiniz", ephemeral = True)
        
        
     
        userInfo = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id))  
    
        if type(userInfo) != NoneType:
      
            user1 = {
            "_id": ctx.author.id
            }
            user2 = {
                "_id": member.id
            }
            userInfo1 = self.bot.db.User_Information.find_one(user1)
            userInfo2 = self.bot.db.User_Information.find_one(user2)
          
            usermoney1 = userInfo1["Money"]
            usermoney2 = userInfo2["Money"]

            if usermoney1 - money < 0 :
                await ctx.respond("`Yeterli paranız yok.`",ephemeral  =True)
                return
            
            uptadeUser1 = {
                "$set": {
                "Money" : usermoney1-money 
                }
            }
            uptadeUser2 = {
                "$set" : {
                "Money" : usermoney2 + money 
                }
            }
            try : 
                self.bot.db._uptadeUser(user1,uptadeUser1)
                self.bot.db._uptadeUser(user2,uptadeUser2)
                await ctx.respond(f"{ctx.author.mention} => {money} Gold => {member.mention}. İşlem tamamlandı")
                
            except Exception as e :
                return               
            
        
        else :
            await ctx.respond("`Kullanıcı kayıtlı değil`", ephemeral = True)
    

    @slash_command(name = "market", description = "marketi açarsınız")
    @commands.cooldown(1, 150, commands.cooldowns.BucketType.user)
    async def market(self,ctx):
        await ctx.defer()
        ItemText:str = ""
        for index,item in enumerate(self.bot.SelectedItems):
            ItemText += f"{index+1} -> **{item['Name']}**............{item['Cost']} gold \n"
        
        embed=discord.Embed(
                title=":moneybag: **Tüccar**:moneybag: ".format(ctx.author.nick),
                timestamp=datetime.utcnow(), 
                color= discord.Color.random())
        
        embed.add_field(name = "**İtemler ve fiyatları:**", value = ItemText)
        embed.add_field(name = ":sparkles:  **Satın almak için**", value="**/al Eşyanın Numarası**", inline= False)
        await ctx.respond(embed = embed)

    @slash_command(name = "al", description = "marketten eşya alırsınız")
    @commands.cooldown(1, 50, commands.cooldowns.BucketType.user)
    async def buy(self,ctx,number: Option(int,"markette ki item numarasını giriniz", min_value = 1,Required = True)):
        if number > self.bot.configuration['Total Selected Item']:
            await ctx.respond("Bu item mağazada yok", ephemeral = True)
            return
        
        Item = self.bot.SelectedItems[number-1]
        InventoryData  = self.bot.db.UserEnv.find_one(FindCondition(ctx.author.id),{"Items":1})
        Inventory = InventoryData['Items']
        InventorySizeInfo = self.bot.db.Settings.find_one(FindCondition(ctx.author.id)) 
        if len(Inventory) == InventorySizeInfo['Size Inventory']:
            await ctx.respond("Envanteriniz dolu", ephemeral = True)
            return
        MoneyInfo  = self.bot.db.User_Information.find_one(FindCondition(ctx.author.id),{'Money':1})
        Money = MoneyInfo['Money']
        if Money - Item['Cost'] < 0:
            await ctx.respond("Yeterli goldunuz yok", ephemeral = True)
            return
        moneyData = {"$inc" : {"Money": - Item['Cost']}}
        HaveAddedItem = buyItem(self.bot.db,ctx.author.id,Item["id"])
        result = HaveAddedItem.addItem()
        if result == True:
            self.bot.db.User_Information.update_one(FindCondition(ctx.author.id), moneyData)
            await ctx.respond(f"{ctx.author.mention} {Item['Name']} itemini satın aldı.")

        else :
            await ctx.respond("Bir hata oluştu")


    #itemin fiyatının yüksekliğine göre zar atılsın
    @slash_command(name = "sat", description = "Bölgenizde ki satıcıya item satarsınız")
    @commands.cooldown(1, 50, commands.cooldowns.BucketType.user)#güncellenmesi için 30 dakika bekle
    async def selltonpc(self,ctx,
    itemnumber: Option(int,"Envanterinizde ki itemin numarası", Required = True),
    gold: Option(int,"Satmak istediğiniz fiyatı yazınız", Required = True),
    adet: Option(int,"Kaç adet satacaksınız", default = 1,Required = False)):
        def updatedata():#2den fazlaysa biri çıkar
            sellItem = buyItem(self.bot.db,ctx.author.id, Inventory[itemnumber-1]["id"],adet)
            result =sellItem.removeItem()
            if result == True:
                moneyData  = {"$inc" : {"Money" : gold}}
                self.bot.db.User_Information.update_one(FindCondition(authorid),moneyData)
                return True
            else:
                return False
          
            

        #await ctx.defer()
        authorid = ctx.author.id
        userInfo = self.bot.db.User_Information.find_one(FindCondition(authorid),{"int":1,"Current Location id":1,"Travel Status":1,"Money":1})
        userInventory = self.bot.db.UserEnv.find_one(FindCondition(authorid),{"Items":1})
        Inventory = userInventory["Items"]
        InvSize = len(Inventory)
        if itemnumber < 1 and itemnumber >= InvSize:
            await ctx.respond("**Npc**: Sende olmayan itemi neden satmaya çalışıyorsun?")
            return
        if Inventory[itemnumber-1]["Using"] == True:
            await ctx.respond("Bu itemi şuan kullanıyorsun satamazsın", ephemeral = True)
            return
        
        if userInfo["Current Location id"] == self.bot.configuration['npc location']:#zindan
            with open('.\Cog\jsons\dpc.json', "r", encoding='utf-8') as npcFile:
                NpcData = json.load(npcFile)
            newDict = NpcData[ "halfBloodSeller"]
            UserIntDice = roll("1d20") + bonus(userInfo["int"])
            NpcIntDice = roll("1d20") + bonus(newDict["intelligence"])
            sentenceIndex = roll("1d3")
            itemCost = self.bot.db.Items.find_one({"_id": Inventory[itemnumber-1]["id"]}, {"cost":1})
            totalItemCost = itemCost["cost"]*adet 
            profit = gold - totalItemCost
            
            if profit > 0 :
                profit = (profit / totalItemCost)*100

            
            if totalItemCost >= gold:
                await ctx.respond("**npc**: Seninle alış-veriş güzeldi ahahaha", ephemeral = True)
                updatedata()
                return
            
            
            if UserIntDice >= NpcIntDice:
                IntProfit = UserIntDice - NpcIntDice
                if (IntProfit /NpcIntDice )*100 >= profit :
                    result = updatedata()
                    if result == True:
                        await ctx.respond(f"**Npc:** {newDict['rpsensentenceSuccess'][sentenceIndex]}", ephemeral= True)
                    else :
                        await ctx.respond("Bir hata oluştu", ephemeral = True)
            else:
                await ctx.respond(f"**Npc:** {newDict['rpsentencenotSucsess'][sentenceIndex]}", ephemeral = True)

        else :
            await ctx.respond("Npc bu bölgede yok", ephemeral = True) 

    @slash_command(name = "sandık", description = "marketten eşya alırsınız")
    @commands.cooldown(1, 50, commands.cooldowns.BucketType.user)
    async def chest(self,ctx):
        await ctx.respond("Çok yakında...", ephemeral = True)
def setup(bot):
    bot.add_cog(economy(bot))