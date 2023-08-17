
import discord 
from discord.ext import commands
from Cog.modules.utils import*
from discord.commands import slash_command
from discord.commands import Option


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    @slash_command(name = "yolculuksüresi", description = "bir oyuncunun yolculuk süresini değiştirisin")
    async def traveltime(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    minutetime: Option(int, "Dakika cinsinden zaman", min_value = 1,Required  = True)):
        data = {
            '$set' : {
                "Travel Time": minutetime
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")    

    @slash_command(name = "savaşsüresi", description = "bir oyuncunun savaş süresini değiştirisin")
    @commands.cooldown(1, 300, commands.cooldowns.BucketType.user)
    async def warduration(self, ctx,
    secondtime: Option(int,"Saniye cinsinden zaman", min_value = 1, max_value = 10, Required = True)):
        member = ctx.author.id
        data = {
            '$set' : {
                "War Duration": secondtime
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member),data)
        await ctx.respond("Ayarlandı", ephemeral = True)
    
    @slash_command(name = "savaşsüresi", description = "bir oyuncunun savaş süresini değiştirisin")
    async def warduration(self, ctx,
    hourstime: Option(int,"Saniye cinsinden zaman", min_value = 1, max_value = 10, Required = True)):
        member = ctx.author.id
        data = {
            '$set' : {
                "PvpShield Duration": hourstime
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member),data)
        await ctx.respond("Ayarlandı", ephemeral = True)

    
    @slash_command(name = "avenerjisi", description = "bir oyuncunun  avlanırken harcadığı enerjiyi değiştirisin")
    async def huntenergy(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    energy: Option(int, "harcanacak enerji miktarı", min_value = 1, Required = True)):
        data = {
            '$set' : {
                "Hunt Energy": energy
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    
    
    @slash_command(name = "savaşenerjisi", description = "bir oyuncunun savaşırken harcadığı enerjiyi değiştirisin")
    async def warenergy(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    energy: Option(int, "harcanacak enerji miktarı", min_value = 1, Required = True)):
        data = {
            '$set' : {
                "War Energy": energy
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    
    @slash_command(name = "yolculukenerjisi", description = "bir oyuncunun yolculuk yaparken harcadığı enerjiyi değiştirisin")
    async def travelenergy(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    energy: Option(int, "harcanacak enerji miktarı", min_value = 1, Required = True)):
        data = {
            '$set' : {
                "Travel Energy": energy
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    @slash_command(name = "envanterbüyüklüğü", description = "bir oyuncunun envanterinin büyüklüğünü değiştirisin")
    async def sizeinventory(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    size: Option(int, "envanter büyüklüğü", min_value = 10, Required  = True)):
        data = {
            '$set' : {
                "Size Inventory": size
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")

    @slash_command(name = "altınçarpanı", description = "bir oyuncunun altın çarpanını değiştirisin")
    async def goldmultiplier(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    multiplier: Option(int, "Gold Çarpanı", min_value = 1, Required = True)):
        data = {
            '$set' : {
                "Gold Multiplier": multiplier
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    @slash_command(name = "xpçarpanı", description = "bir oyuncunun xp çarpanını değiştirisin")
    async def xpmultiplier(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    multiplier: Option(int, "Xp Çarpanı", min_value = 1, Required = True)):
        data = {
            '$set' : {
                "Xp Multiplier": multiplier
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    
    @slash_command(name = "baygınlıksüresi", description = "bir oyuncunun baygınlık süresini değiştirisin")
    async def loseduration(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    minutetime: Option(int, "Dakika cinsinden zaman", min_value = 1,Required  = True)):
        data = {
            '$set' : {
                "Lose Duration": minutetime
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    @slash_command(name = "avınsüresi", description = "bir oyuncunun avın süresini değiştirisin")
    async def huntduration(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    minutetime: Option(int, "Dakika cinsinden zaman", min_value = 1,Required  = True)):
        data = {
            '$set' : {
                "Hunt Duration": minutetime
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    @slash_command(name = "skillturu", description = "skilli kaçıncı turda kullanacağını belirlersin")
    @commands.cooldown(1, 150, commands.cooldowns.BucketType.user)
    async def skillturn(self, ctx,
    tur: Option(int, "Savaşta skillin kaçıncı turda kullanılacağını belirtirsin", min_value = 1,max_value = 100,Required = True)):
        member = ctx.author.id
        data = {
            '$set' : {
                "Skill Turn": tur
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member),data)
        await ctx.respond("Ayarlandı", ephemeral  =True)
    @slash_command(name = "loncabüyüklüğü", description = "bir oyuncunun oluşturacağı loncanın büyüklüğünü değiştirisin")
    async def loncasize(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    size: Option(int, "Lonca büyüklüğü", min_value = 3, Required  = True) ):
        data = {
            '$set' : {
                "LoncaSize": size
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    @slash_command(name = "candolmaçarpanı", description = "bir oyuncunun 10 saniyede kaç hp dolacağını değiştirisin")
    async def hpfilling(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    multiplier: Option(int,"10 Saniyede kaç tane dolacağı", min_value = 1,Required = True)):
        data = {
            '$set' : {
                "FillingHp": multiplier
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    @slash_command(name = "enerjidolmaçarpanı", description = "bir oyuncunun 10 saniyede kaç enerji dolacağını değiştirisin")
    async def energyfilling(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    multiplier: Option(int,"10 Saniyede kaç tane dolacağı", min_value = 1,Required = True)):
        data = {
            '$set' : {
                "FillingEnergy": multiplier
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")
    @slash_command(name = "maxenerjilimiti", description = "bir oyuncunun max enerji limitini  değiştirisin")
    async def maxenergylimit(self, ctx,
    member: Option(discord.Member,"Kayıtlı üye", Required = True),
    limit: Option(int,"Enerji limiti", min_value = 100, reuired  =True)):
        data = {
            '$set' : {
                "MaxEnergyLimit": limit
            }
        }
        self.bot.db.Settings.update_one(FindCondition(member.id),data)
        await ctx.respond("Ayarlandı")

def setup(bot):
    bot.add_cog(Settings(bot))