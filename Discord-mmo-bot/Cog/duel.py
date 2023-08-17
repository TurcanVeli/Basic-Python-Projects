

import asyncio
import discord 
from discord.ext import commands
from Cog.modules.utils import*
from discord.commands import slash_command
from discord.commands import Option
from datetime import datetime
from Cog.modules.war import Player, Monsters


''' 
Savaşlar frpye benzer olacak. frp can değerlerine ve attacklarına sahip olunacak ama skill kullanılmayacak. Sadece zar sistemi olacak.
'''
#Düelloda ki her şey burada, log embedi gönder
class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name = 'saldıryaratık', description = 'yakaladığınız yaratıklara saldırırsınız')
    async def pvn(self,ctx,
    numara: Option(int, 'Av Sırası', Required = True)
    ): 
        
        User = Player(self.bot.db, ctx.author.id)
        LoseLog = User.CheckLoseLog()
        
        if LoseLog == False:
            await ctx.respond("Baygınsınız", ephemeral = True)
        HuntLogControl = User.HuntLog()
        if HuntLogControl == False:
            await ctx.respond('Elinizdekiler kaçmış ya da kimseyi bulamazdınız', ephemeral  = True)
            return
        Cathed = HuntLogControl['Cathed']
        if  numara-1 >= len(Cathed):
            await ctx.respond('Yanlış numara girdiniz', ephemeral  = True)
            return
       
        await ctx.respond("Başlıyor", ephemeral = True)
      
        User.Load_userInformation()
        print("Buraya geldi")
        LoncaBuffText = User.checkBuffofLoncaMembers()
        print("Burayada geldi")
        ControlEnergy = User.checkEnergy() #false olursa yetmiyor
        if ControlEnergy == False:
            await ctx.respond("enerjiniz yetmiyor. Yüklendikten sonra tekrar deneyin", ephemeral = True)
            return
        User.UsingItems() #load items
      
        
        monsterDict          = Cathed[numara-1] 
        Monster = Monsters(self.bot.db,monsterDict['id'])
        Monster.Load_MonsterInformation()
        Desc = "Player Vs Npc"
        UserACtionText: str = "Başlıyor" 
        MonsterACtionText: str = "Başlıyor"
        ResultText: list = ["Yok","Yok","Yok","Yok"]
        SkillText = "Skill kullanılmadı"
        Turn = 0
      
        def AttackTable(Field = False):
                    Attackembed=discord.Embed(title="Savaş", description = Desc, color=0xff0a0a)
                    if Field == False:
                        Attackembed.set_author(name=f"{User.UserName}")
                        Attackembed.add_field(name=f"{User.UserName} -> **{LoncaBuffText}**",  value = f"{User.HP}/{User.maxHP}:heart:\n**Aksiyon**: {UserACtionText}\n**Skill**: {SkillText}", inline=False)
                        
                        Attackembed.add_field(name=f"{Monster.monsterName} ->",  value = f"{Monster.HP}/{Monster.maxHP}:heart:\n**Aksiyon**: {MonsterACtionText}", inline= False)
                    elif Field == True:
                        Attackembed.add_field(name = ResultText[0], value = f"{ResultText[1]}, {ResultText[2]}", inline= False) 
                   
                    
                    Attackembed.set_footer(text= f"Tur {Turn}")
                    return Attackembed

        AttackEmbed  =  await ctx.send(embed = AttackTable())

        while Monster.HP > 0 and User.HP > 0 :
         
            Turn += 1
            SkillText = User.Effects(Monster,Turn)
      
            if User.SkillType == True:     
                value =  Turn % User.bs 
                if value ==  User.SkillTurn:
                    SkillText = User.UseSkillAktif(Monster,Turn)
            else :  
                SkillText = User.UseSkillPasif(Monster,Turn)
                
            
            User.Attack()
            User.checkStarvationDebuff()
   
            
            if User.HitDirectly:
                Monster.HP -= User.Damage
                UserACtionText = f"Zayıflıktan yararlandı ve direk {User.CurrentWeapon} ile {User.Damage} hasar vurdu."
                User.HitDirectly = False
            else:
                if User.CommondRoll == 20:
                    User.CritickDamage = User.Damage*User.CritickMultiplier
                    Monster.HP -= User.CritickDamage
                    UserACtionText = f"KRİTİK...{User.CurrentWeapon} ile {User.CritickDamage} hasar vurdu."
                    User.Critick = True
                if User.CommondRoll == 1:
                    UserACtionText = "Vuramadı. Özgüveni zedelendi."
                
                if User.CommondRoll != 20 and User.CommondRoll !=1 and User.attackRoll  >= Monster.AC:
                    Monster.HP -= User.Damage
                    UserACtionText = f"{User.CurrentWeapon} ile {User.Damage} hasar vurdu."
                
                else:
                    UserACtionText = f"Kaçırdınız."



            if User.EnemyCanAttack:

                Monster.attack()
      
                if Monster.CommondRoll == 20:
                    Monster.CritickDamage = Monster.Damage*2 
                    User.HP -= Monster.Critick
                    MonsterACtionText  = f"Kritik... {Monster.Attack['Name']} saldırısı yaptı ve {Monster.CritickDamage} hasar vurdu."
               
                if Monster.CommondRoll == 1:
                    MonsterACtionText = "Vuramadı. Özgüveni zedelendi."
                    Monster.UnSuccessfullAttack = True
                
                if Monster.CommondRoll != 20 and Monster.CommondRoll !=1 and Monster.AttackRoll  >= User.AC:
                    User.HP -= Monster.Damage
                    MonsterACtionText  = f"{Monster.Attack['Name']} saldırısı yaptı ve {Monster.Damage} hasar vurdu."
                
                else:
                    MonsterACtionText = f"Yaratığın saldırsını engellediniz"
                    Monster.UnSuccessfullAttack = True
                
            else :
                MonsterACtionText = f"{User.skillofUSer} kullanıldı ve yaratık saldıramadı"

            
            if Monster.HP <= 0:
                Monster.HP = 0
                User.IsWin = True
            if User.HP < 0:
                User.HP = 0
            await asyncio.sleep(User.warDuration)   
            await AttackEmbed.edit(embed = AttackTable())

        #End of War
        User.energyofUser -= User.settings['War Energy']
        if User.energyofUser < 0:
            User.energyofUser = 0
        if User.HP > User.maxHP:
            User.HP = User.maxHP
        
        dataOfEnergyandHp = {"$set" : {"Enerji" : User.energyofUser,"Hp": User.HP}}
        
        self.bot.db.userBattle.update_one(FindCondition(User.id), dataOfEnergyandHp)
        self.bot.db.Logs.delete_one({"id" : User.id, "Type": 0})
        if User.IsWin:
            ResultText = User.WhenWarPvNFinish(Monster)
        else :
            ResultText = Monster.Win(User)


        await asyncio.sleep(1)
        await AttackEmbed.edit(embed = AttackTable(Field  = True))
        
        

        




        










    @slash_command(name = 'saldıroyuncu', description = 'yakaladığınız oyunculara saldırırsınız')
    async def pvp(self,ctx,
    numara: Option(int, 'Av Sırası', Required = True)):
        User = Player(self.bot.db, ctx.author.id)
        LoseLog = User.CheckLoseLog()
        
        if LoseLog == False:
            await ctx.respond("Baygınsınız", ephemeral = True)
        HuntLogControl = User.HuntLog()
        if HuntLogControl == False:
            await ctx.respond('Elinizdekiler kaçmış ya da kimseyi bulamazdınız', ephemeral  = True)
            return
        Cathed = HuntLogControl['CathedPLayers']
        if  numara-1 >= len(Cathed):
            await ctx.respond('Yanlış numara girdiniz', ephemeral  = True)
            return
       
        User.PvpShieldControl()
        User.Load_userInformation()

        LocationLevel = self.bot.db.Rp_Channels.find_one(FindCondition(User.UserLocaitonID), {'danger level':1})
        if LocationLevel['danger level'] < 2:
            await ctx.respond("Burada pvp açık değil daha tehlikeli alanlara gidiniz", ephemeral = True)
            return
      
        await ctx.respond("Başlıyor", ephemeral = True)
        #UserhaveLoncaBuff = User.checkBuffofLoncaMembers()
        UserLoncaBuffText = User.checkBuffofLoncaMembers()
        ControlEnergy = User.checkEnergy() #false olursa yetmiyor
        if ControlEnergy == False:
            await ctx.respond("enerjiniz yetmiyor. Yüklendikten sonra tekrar deneyin", ephemeral = True)
            return
        User.UsingItems() #load items



        EnemyDict     = Cathed[numara-1]
        Enemy = Player(self.bot.db,EnemyDict['id'])
        Enemy.Load_userInformation()
        
        EnemyLoncaBuffText = Enemy.checkBuffofLoncaMembers()

        if User.CheckLevel(Enemy) == False:
            await ctx.respond("Level kısıtlamasından dolayı saldıramazsınız", ephemeral = True)
            return

        #EnemyHaveLoncaBuff = Enemy.checkBuffofLoncaMembers() #Lonca buffı varsa True
     

        Enemy.UsingItems()


        Turn = 0
        UserActionText = "Başlıyor" 
        EnemyActionText = "Başlıyor" 
        ResultText = ['yok','yok','yok']
        UserSkillText  ="Skill kullanılmadı."
        enemySkillText = "Skill kullanılmadı."
        Desc = "PvP Savaşı"
        def WarEmbed(Field = False):
                Attackembed=discord.Embed(title="Savaş", description = Desc, color=0xff0a0a)
                Attackembed.set_author(name=f"{User.UserName}")
                if Field == False:
                    Attackembed.add_field(name=f"{User.UserName} Saldırı -> **{UserLoncaBuffText}** ", value = f"{User.HP}/{User.maxHP}:heart:\n**Aksiyon**: {UserActionText}\n**Skill**: {UserSkillText}", inline=False)
                    Attackembed.add_field(name=f"{Enemy.UserName}  Saldırı  -> **{EnemyLoncaBuffText}**",  value = f"{Enemy.HP}/{Enemy.maxHP}:heart:\n**Aksiyon**: {EnemyActionText}\n**Skill**: {enemySkillText}", inline= False)
     
                if Field == True:
                    Attackembed.add_field(name = ResultText[0], value = f"{ResultText[1]}, {ResultText[2]}", inline= False) 
                Attackembed.set_footer(text= f"Tur {Turn}.")
                return Attackembed

        
        AttackEmbed  =  await ctx.send(embed = WarEmbed())
        await asyncio.sleep(User.warDuration)

        
        #War
        while Enemy.HP > 0 and User.HP > 0 :
            User.EnemyCanAttack = True
            #ilk attack yapan.
            UserSkillText = User.Effects(Enemy,Turn)
            
            if Enemy.EnemyCanAttack:

                if User.skill.check_SkillType == True:
       
                    if Turn%User.bs == User.SkillTurn:
        
                        UserSkillText = User.UseSkillAktif(Enemy,Turn)
                else :
         
                    UserSkillText = User.UseSkillPasif(Enemy,Turn)
                User.Attack()
                User.checkStarvationDebuff()

                if User.HitDirectly:
                    Enemy.HP -= User.Damage
                    UserActionText = f"Zayıflıktan yararlandı ve direk {User.CurrentWeapon} ile {User.Damage} hasar vurdu."
                    User.HitDirectly = False
                
                
                else:
            
                    if User.CommondRoll == 20:
                        User.CritickDamage = User.Damage*User.CritickMultiplier
 
                        Enemy.HP -= User.CritickDamage
                        UserActionText = f"KRİTİK...{User.CurrentWeapon} ile {User.CritickDamage} hasar vurdu."
                        User.Critick = True
                    if User.CommondRoll == 1:
                        UserActionText = "Vuramadı. Özgüveni zedelendi."
                        User.UnSuccessfullAttack = True
                    if User.CommondRoll != 20 and User.CommondRoll !=1 and User.attackRoll  >= Enemy.AC:
                        Enemy.HP -= User.Damage
                        UserActionText = f"{User.CurrentWeapon} ile {User.Damage} hasar vurdu."
                    
                    
                    else:
                        UserActionText = f"Kaçırdınız."
                        User.UnSuccessfullAttack = True

            else :
                UserActionText = f"{Enemy.skillofUSer} kullanıldı ve saldıramadı"

            Enemy.EnemyCanAttack = True
      
            enemySkillText = Enemy.Effects(Enemy,Turn)
          
            if User.EnemyCanAttack:
                
                if Enemy.SkillType == True:
              
                    if Turn%Enemy.bs == Enemy.SkillTurn:
                     
                        enemySkillText = Enemy.UseSkillAktif(User,Turn)
                else :
                    enemySkillText = Enemy.UseSkillPasif(User,Turn)
                
                Enemy.Attack()
                Enemy.checkStarvationDebuff()
             
                if Enemy.HitDirectly:
              
                    User.HP -= Enemy.Damage
                    EnemyActionText = f"Zayıflıktan yararlandı ve {Enemy.CurrentWeapon} ile {Enemy.Damage} hasar vurdu."
                    Enemy.HitDirectly = False
                
                else:
                    
                    if Enemy.CommondRoll == 20:
                        Enemy.CritickDamage = Enemy.Damage*Enemy.CritickMultiplier 
                        User.HP -= Enemy.CritickDamage
                        EnemyActionText = f"KRİTİK...{Enemy.CurrentWeapon} ile {Enemy.CritickDamage} hasar vurdun."
                        User.Critick = True
                        
                    
                    if Enemy.CommondRoll == 1:
                        EnemyActionText = "Vuramadınız. Özgüveniniz zedelendi."
                        Enemy.UnSuccessfullAttack = True
                    
                    if Enemy.CommondRoll != 20 and Enemy.CommondRoll !=1 and Enemy.attackRoll  >= User.AC:
                        User.HP -= Enemy.Damage
                        EnemyActionText = f"{Enemy.CurrentWeapon} ile {Enemy.Damage} hasar vurdun."
                        
                    else:
                        EnemyActionText = f"Kaçırdınız."
                        Enemy.UnSuccessfullAttack = True
            
            else :
                EnemyActionText = f"{User.skillofUSer} kullanıldı ve saldıramadı"    
            
            
            if Enemy.HP <= 0:
                Enemy.HP = 0
                User.IsWin = True
            if User.HP < 0:
                User.HP = 0
            Turn+=1
            await asyncio.sleep(User.warDuration)
            await AttackEmbed.edit(embed =  WarEmbed())
       
        User.energyofUser -= User.settings['War Energy']
        if User.energyofUser < 0:
            User.energyofUser = 0
        if User.HP > User.maxHP:
            User.HP = User.maxHP
        if Enemy.HP > Enemy.maxHP:
            Enemy.HP = Enemy.maxHP
        
 


        dataofHp = {"$set" : {"Hp": Enemy.HP}}
        dataOfEnergyandHp = {"$set" : {"Enerji" : User.energyofUser,"Hp": User.HP}}
        self.bot.db.userBattle.update_one(FindCondition(Enemy.id), dataofHp)
        self.bot.db.userBattle.update_one(FindCondition(User.id), dataOfEnergyandHp)
        self.bot.db.Logs.delete_one({"id" : User.id, "Type": 0})
   
        Shield_time = datetime.now()
        PvpShield = {'$set': {"Pvp Shield": True}}
        if User.IsWin:
            ResultText = User.WhenWarPvpFinish(Enemy)

            PvpShieldLog = {
                "id":Enemy.id,
                "Type" : 2,
                "Shield Time": Shield_time,

            }
            self.bot.db.User_Information.update_one(FindCondition(Enemy.id),PvpShield)
        
        else :
            ResultText = Enemy.WhenWarPvpFinish(User)
          
            PvpShieldLog = {
                "id":User.id,
                "Type" : 2,
                "Shield Time": Shield_time,

            }
            self.bot.db.User_Information.update_one(FindCondition(User.id),PvpShield)
        
        self.bot.db.Logs.insert_one(PvpShieldLog)
        
        
        
        await AttackEmbed.edit(embed =  WarEmbed(Field=True))




def setup(bot):
    bot.add_cog(Battle(bot))
