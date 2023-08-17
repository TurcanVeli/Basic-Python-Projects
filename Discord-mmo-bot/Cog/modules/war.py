
from ast import Str
from decimal import DivisionByZero
from types import NoneType
from Cog.modules.utils import*
from random import randint
import json
from random import choices
from Cog.modules.processInventory import Inventory as Inv
from datetime import datetime
from Cog.modules.skills import Skill
class Player():
    def __init__(self, db:object, id:int) -> None:
        self.id = id
        self.db = db
        self.ResultText = ['','','']
        self.settings = self.db.Settings.find_one(FindCondition(self.id))
        self.attackRoll    = 0
        self.Damage  = 0
        self.CritickDamage  = 0
        self.CritickMultiplier = 2
        self.PasifSkillTurn = 0
        self.EffectsEndTurn = 0
        self.DamageBonus = 0
        self.EnemyCanAttack = True
        self.Critick = False #kritik vuruldu mu
        self.IsWin = False
        self.UnSuccessfullAttack = False #SBaşarısız saldırıda True olur
        self.HitDirectly = False
        self.advantageAttack = False
        self.disadvantageAttack = False
        
        with open('Cog\jsons\configuration.json',encoding='utf-8') as f:
            self.configuration  = json.load(f)

        with open('Cog\jsons\player.json',encoding='utf-8') as f:
            self.player  = json.load(f)
    
    def Load_userInformation(self):
        self.Inventory = self.db.UserEnv.find_one(FindCondition(self.id)) 
        userINFO = self.db.User_Information.find_one(FindCondition(self.id))
        self.UserName = userINFO['Name']
        self.UserStr  = userINFO['Str']
        self.UserDex = userINFO['Dex']
        self.UserInt = userINFO['int']
        self.UserCons = userINFO['Cons']
        self.Uzmanlık = userINFO['Uzmanlık']
        self.proficiency = userINFO['proficiency']
        self.UserLocaitonID = userINFO["Current Location id"]
        self.Rp_Danger_Level = self.db.Rp_Channels.find_one(FindCondition(self.UserLocaitonID),{'danger level':1})
        self.Rp_Danger_Level = self.Rp_Danger_Level['danger level']
        self.UserloncaID = userINFO['Lonca'][0] 
        self.Temploncamembers:list = []
        if self.UserloncaID != 0:
            Lonca    = self.db.Lonca.find_one(FindCondition(self.UserloncaID)) 
            self.Temploncamembers = [memberid for memberid in Lonca['Members'] if memberid != self.id]#tempetature list of members
        userBattleState        = self.db.userBattle.find_one(FindCondition(self.id))
        self.HP          = userBattleState['Hp']
        self.maxHP       = userBattleState['MaxHp']
        self.energyofUser      = userBattleState['Enerji']
        self.XpofUSer          = userBattleState['Exp']
        self.MaxXpofUSer       = userBattleState['MaxExp']
        self.Starvation        = userBattleState['starvation']
        self.levelOfUser       = userBattleState['Level']
        self.skillofUSer       = userBattleState['skill']
        self.AC  = userBattleState['Armor Class']
        self.damageDiceofUser  = userBattleState['Damage']
        self.ClassOfUser       = userBattleState['Sınıf']
        UserSettings     = self.db.Settings.find_one(FindCondition(self.id), {'Skill Turn':1,'War Duration':1})
        self.SkillTurn  = UserSettings['Skill Turn']
        self.warDuration = UserSettings['War Duration']
        self.skill  = Skill(self.ClassOfUser,self.levelOfUser,self.skillofUSer)
        self.SkillType = self.skill.check_SkillType()
        self.bs = self.skill.BS()
        atwarData  = {'$set' : {"AtWar" : True}}
        self.db.User_Information.update_one(FindCondition(self.id),atwarData)
      

   
    
    def locationMembers(self,id) -> int:
            location = self.db.User_Information.find_one(FindCondition(id),{'Current Location id':1})
            return location['Current Location id']
    
    def checkBuffofLoncaMembers(self) -> str:
        loncaMembers: list = []#They will join the war
        for id in self.Temploncamembers:
            if self.locationMembers(id) == self.UserLocaitonID:
               
                loncaMembers.append(id)
                memberBattleState    = self.db.userBattle.find_one(FindCondition(id))
                energyOfmember       = memberBattleState['Enerji']
                if energyOfmember <= 20:
                    continue
                
                memberDamageDice  =  memberBattleState['Damage']
              
                if memberDamageDice == "Yok":
                    continue
                
                else :
                    try: 
                        self.DamageBonus += int(roll(memberDamageDice)/4)
                    except Exception as e:
                        continue
                
        self.countOfloncamembers = len(loncaMembers)
        if self.countOfloncamembers == 0:
            return "0"
        else :
            return f"{self.countOfloncamembers}"
    

    def UsingItems(self):
        userInventory   = self.db.UserEnv.find_one(FindCondition(self.id))
        self.CurrentWeapon    = userInventory['Weapon']['Name']
        self.CurrentWeaponType    = Str
        self.CurrentWeaponID  = userInventory['Weapon']['id']
        if self.CurrentWeaponID == 0:
            self.CurrentWeapon = "Yumrukları"
            self.CurrentWeaponType = "Boş"
        else:
            self.WeaponType      = self.db.Items.find_one(FindCondition(self.CurrentWeaponID),{"type":1})
            self.CurrentWeaponType  = self.WeaponType["type"]
        
        
          
    
    def checkEnergy(self) -> bool:#enerjisi ya da canı yetmiyor
        if self.energyofUser <= self.settings['War Energy'] or self.HP <= 0 :#settings
            return False
        return True
    
    def checkStarvationDebuff(self, constrain: int = 15):
        if self.Starvation <= constrain:
            self.Damage  = -int(self.Damage/2)
            

 
    def Effects(self,enemy:object,CurrentTurn:int):
        if self.EffectsEndTurn == CurrentTurn:
            if self.skillofUSer == "Yıkıcı Saldırı":
                enemy.AC += self.reducedAc
                
                
                return f"{self.skillofUSer} Etkisi geçti"
                
            
            elif self.skillofUSer == "Savun":
                self.AC = self.AC -(5 + self.skillLevel)
           
                return f"{self.skillofUSer} Etkisi geçti"
        

        elif self.EffectsEndTurn > CurrentTurn:
            if self.skillofUSer == "Kanama":
                value = 5 + self.skillLevel
                enemy.HP -= int(enemy.HP*(value/100))
                return "Düşmanın Kanaması var her tur canı azalıyor."
            
            elif self.skillofUSer == "Sersemlet":
                enemy.disadvantageAttack = True
                return "Düşman bu turda sersemletildi." 
            
            elif self.skillofUSer == "Taktik Deha":
                self.advantageAttack = True
                self.EnemyCanAttack = False 
                return "Avantajlısın ve düşman bu tur saldıramıyor."

            else:
                return "Skillin Etkisi devam ediyor"

        
        else:
            return "Şuan kullanılan bir skill yok"


    


    def UseSkillAktif(self,enemy:object, CurrentTurn:int):
        self.skillLevel = self.skill.check_SkillLevel()
        if self.ClassOfUser == "Barbarian":
            if self.skillofUSer == "Yıkıcı Saldırı":
                self.reducedAc = roll("1d6") 
                enemy.AC -= self.reducedAc
                ActiveReduceAcEffect = roll("1d3") #
                self.EffectsEndTurn += ActiveReduceAcEffect
                return  f"Yıkcı saldırı kullanıldı ve düşman acsi {ActiveReduceAcEffect} tur boyunca {self.reducedAc} azaldı."
        
        
        elif self.ClassOfUser == "Wizard":
            
            if self.skillofUSer == "Şimşek": #bs 5
                IntSaveRoll = 8 + bonus(self.UserInt) + self.skillLevel
                if roll('1d20') + bonus(enemy.UserCons) < IntSaveRoll:
                    enemy.disadvantageAttack = True
                    return "Şişmek saldısı yapıldı ve düşman dezavantajlı konuma düştü."
                return "Rakip şimşek saldırısını engelledi."
            
            elif self.skillofUSer == "Ruh Sömürme": #bs 8
                heal = self.levelOfUser*(roll('1d4')) + bonus(int)
                self.HP += heal
                enemy.HP -= int(heal/2)
                return f"Ruh sömürme saldırısı yapıldı ve {heal} can iyileştirildi. Düşmandan {int(heal/2)} can çalındı."
            
            elif self.skillofUSer == "Sersemlet":#Hasar ilk hasara ek olarak alınır
                IntSaveRoll = 8 + bonus(self.UserInt) + self.skillLevel*2
                enemyIntSaveRoll = roll('1d20') + bonus(enemy.UserInt)
                if IntSaveRoll > enemyIntSaveRoll: #Tutturamadı
                    rollhp = roll('5d12')
                    enemy.HP -= rollhp
                    ActivedizzyEffect = roll('1d10') #Sersemlemiş düşmanlar dezavantajlı saldırır
                    enemy.disadvantageAttack = True
                    self.EffectsEndTurn = CurrentTurn + ActivedizzyEffect
                    return f"Düşman {ActivedizzyEffect} tur boyunca sersemletildi ve {rollhp} kadar hasar yedi"


                else: #Tutturdu
                    enemy.HP    -= int(enemy.Damage/2)
                    ActivedizzyEffect = roll('1d3')
                    self.EffectsEndTurn = CurrentTurn + ActivedizzyEffect #düzet
                    return f"Düşman önceki tur hasarının yarısını yedi. {ActivedizzyEffect} tur boyunca sersemledi."
        
        elif self.ClassOfUser == "Ranger":
            if self.skillofUSer == "Kanama":
                EnemyDexSave = roll('1d20') + bonus(self.UserDex)
                UserDexSave = 8 + bonus(self.UserDex)
                if EnemyDexSave < UserDexSave:
                    value = 5 + self.skillLevel
                    ActiveBloodEffect = roll('1d6')
                    
                    enemy.HP -= int(enemy.HP*(value/100))
                    self.EffectsEndTurn = CurrentTurn + ActiveBloodEffect
                    return f"Düşman yaralandı ve {ActiveBloodEffect} tur boyunca her tur %{value} can kaybedecek"
                
                return "Düşman kanama saldırsından kurtuldu."
                                
                

    
    
    def UseSkillPasif(self,enemy:object, CurrentTurn: int):
        self.skillLevel = self.skill.check_SkillLevel()
        if self.ClassOfUser == "Barbarian":
            if self.skillofUSer == "Kan Çalan" and self.Critick ==True:
                rollHp = roll("2d20+5")
                enemy.HP -= rollHp
                self.Critick = False
                return f"Kan çalan saldırısı yapıldı ve Düşmanın {rollHp} canı gitti."
            
            elif self.skillofUSer == "İç Güdüsel Saldırı":
                if enemy.UnSuccessfullAttack and self.PasifSkillTurn == CurrentTurn:
                    enemy.UnSuccessfullAttack = False
                    self.HitDirectly = True
                    self.bs = 6
                    self.PasifSkillTurn = CurrentTurn + self.bs
                    return "HURRA düşman saldırmadı ve sen direk vuruyorsun."
            
            elif self.skillofUSer == "Amansız Öfke":
                if self.CommondRoll in [18,19,20]:
                    self.EnemyCanAttack = False
                    return "Amansız bir öfke bedenini ele geçirdi ve düşman korkudan saldıramıyor."
        
        elif self.ClassOfUser == "Wizard":
            if self.skillofUSer == "Yansıma Saldırısı" and enemy.Critick == True: #bs 10 
                enemy.CritickDamage = int(enemy.CritickDamage/2) #ikiye bölündü yarısını oyuncu yiyecek.
                enemy.HP -= int(enemy.CritickDamage/2) 
                return "Kritik hasar yedin ama yarısını rakibe yansıtmayı başardın."
            

        elif self.ClassOfUser == "Fighter":
            if self.skillofUSer == "Zayıflat":#bs 8
                if self.UnSuccessfullAttack == False and self.PasifSkillTurn == CurrentTurn:
                    enemy.disadvantageAttack = True
                    self.bs = self.skill.BS()
                    self.PasifSkillTurn = CurrentTurn + self.bs
                    return f"Düşman zayıflatıldı ve dezavantajlı saldırı yapacak"
            
            elif self.skillofUSer == "Savuştur":
                if roll('1d20') >= 15 and self.PasifSkillTurn == CurrentTurn:#15 düşer
                    self.EnemyCanAttack = False #Rakip saldıramaz
                    self.bs = 5
                    self.PasifSkillTurn = CurrentTurn + self.bs
                    return "Düşmanın saldırısı savuşturuldu."
            
            elif self.skillofUSer == "Savun":
                if self.UnSuccessfullAttack and self.PasifSkillTurn == CurrentTurn:
                    self.AC = self.AC + 5 + self.skillLevel
                    ActiveACeffect = self.skillLevel #acin aktif olduğu süre
                    self.bs = self.skill.BS()
                    self.PasifSkillTurn = CurrentTurn + self.bs
                    
                    self.EffectsEndTurn = CurrentTurn + ActiveACeffect
                    return f"Ac {ActiveACeffect} tur boyunca {5 + self.skillLevel} kadar arttı."
            
            elif self.skillofUSer == "Taktik Deha":
                if self.PasifSkillTurn == CurrentTurn:
                    self.advantageAttack = True
                    self.EnemyCanAttack = False
                    self.EffectsEndTurn = CurrentTurn + 2  
                    return f"Tam bir taktik deha. Avantajlı saldır ve düşmanın saldırmasına engel ol."                

        elif self.ClassOfUser == "Ranger":
            if self.skillofUSer == "körelt" and self.UnSuccessfullAttack == False and self.PasifSkillTurn == CurrentTurn:
                EnemyDexSave = roll('1d20') + bonus(enemy.UserDex)
                UserDex = 8 + bonus(self.UserDex) + self.skillofUSer
                ResultTxt = "Düşman, körelt saldırsını engelledi"
                if EnemyDexSave < UserDex:
                    enemy.disadvantageAttack = True
                    ResultTxt = "Körelt saldırısı başarılı. Düşman dezavantajlı saldıracak." 
                

                self.bs = self.skill.BS()
                self.PasifSkillTurn = CurrentTurn + self.bs
                return ResultTxt
            
            elif self.skillofUSer == "Dodge" and self.UnSuccessfullAttack== False and self.PasifSkillTurn == CurrentTurn:
                self.EnemyCanAttack = False
                self.bs = self.skill.BS()
                self.PasifSkillTurn = CurrentTurn + self.bs
                return "Rakip bir tur saldıramıyor."

            
            elif self.skillofUSer == "Avcı":
                self.CritickMultiplier = 3
                return "DAHA GÜÇLÜ KRİTİK.."

    

    def Common_Roll(self)-> int:
       
        Values = (roll('1d20'),roll('1d20'))
        if self.advantageAttack:
            return max(Values)
        elif self.disadvantageAttack:
            return min(Values)
        elif self.advantageAttack == False and self.disadvantageAttack == False:
            return roll('1d20')
        else :
            assert "İt can be real!! Advantage and disadvantage true"




    
    def Attack(self):
        if self.Uzmanlık == self.CurrentWeaponType:
            pass
        else :
            self.proficiency = 0    
        
        self.CommondRoll  = self.Common_Roll()

        self.disadvantageAttack = False
        self.advantageAttack = False
        if self.CurrentWeaponType  == "Yakın":
                self.attackRoll   = self.CommondRoll + bonus(self.UserStr)
                self.Damage = roll(self.damageDiceofUser) + bonus(self.UserStr) + self.proficiency + self.DamageBonus

        
        elif self.CurrentWeapon == "Yumrukları":
            self.attackRoll   = self.CommondRoll + bonus(self.UserStr)
            if bonus(self.UserStr) < 0:
                self.Damage =  1
            else :
                self.Damage =  bonus(self.UserStr) + self.DamageBonus

        else:
            self.attackRoll   = self.CommondRoll + bonus(self.UserDex)
            self.Damage = roll(self.damageDiceofUser) + bonus(self.UserDex) + self.proficiency + self.DamageBonus

        
    def CheckLevel(self,enemy:object) -> bool:
        if self.levelOfUser in [1,2,3]:
            return False

        if self.levelOfUser <= 10:
            if enemy.levelOfUser > 10:
                return False

            elif enemy.levelOfUser in [1,2,3]:
                return False

            else :
                return True
        if self.levelOfUser > 10:
            if enemy.levelOfUser <= 10:
                return False
            
            else :
                return True



    def CheckLoseLog(self) -> bool:
        self.LoseLog = self.db.Logs.find_one({"id": self.id, "Type" : 1})
        if type(self.LoseLog) != NoneType:
            return False
        
    def PvpShieldControl(self):
        self.ShieldLog = self.db.Logs.find_one({"id": self.id, "Type" : 2})
        if type(self.ShieldLog) == NoneType:
            return
        else:
            self.db.Logs.delete_one({"id": self.id, "Type" : 2})
    def HuntLog(self) -> bool:
        self.HuntLog = self.db.Logs.find_one({"id": self.id, "Type" : 0})
        if type(self.HuntLog) == NoneType:
            return False
        
        return self.HuntLog
    
    
    def WhenWarPvpFinish(self,enemy:object) -> str:
        atwarData = {'$set':  {"AtWar" : False}}
        self.db.User_Information.update_one(FindCondition(self.id),atwarData)
        self.db.User_Information.update_one(FindCondition(enemy.id),atwarData)

        EnemyMoneyD = self.db.User_Information.find_one(FindCondition(enemy.id),{"Money":1})
        self.ResultText[0] = f"**{self.UserName} savaşı kazandı. {enemy.UserName} bayıldı!!**"     
        EnemyMoney = EnemyMoneyD['Money']
        EnemyLoseMoney = int(EnemyMoney * ((self.player['PvpGoldLose'][str(enemy.levelOfUser)][str(self.Rp_Danger_Level)])/100))
        EarnMoney   = {'$inc' : {'Money' : EnemyLoseMoney}}
        reduceMoney = {'$inc' : {'Money' : -EnemyLoseMoney}}
        self.db.User_Information.update_one(FindCondition(self.id), EarnMoney)
        self.db.User_Information.update_one(FindCondition(enemy.id), reduceMoney)
        self.ResultText[1] = f"{EnemyLoseMoney} gold kazandı"
        
        if enemy.Inventory['Items'] == 0:
            self.ResultText[2] = "İtem kazanılmadı."
        
        else:
            if self.Rp_Danger_Level == 2:
                luckOFitem = 70
            else :
                luckOFitem = 45
            
            
            if randint(1,100) > luckOFitem:
                itemIndex     = randint(0,len(enemy.Inventory['Items'])-1)
                BATTLEItem    = enemy.Inventory['Items'][itemIndex]
                
                
                if len(self.Inventory['Items']) >= self.settings['Size Inventory']:
                    self.ResultText[1] = "Envanteriniz dolduğu için item kazanamadınız"
                
                else :
                    REMOVEITEM = Inv(self.db,enemy.id,BATTLEItem["id"])
                    WinItem = Inv(self.db,self.id,BATTLEItem["id"])
                    result1 = WinItem.addItem()
                    result = REMOVEITEM.removeItem()
                    if result == result1 == True :
                        self.ResultText[2] = f"{BATTLEItem['Name']} İtemini kazandınız."
            else :
                self.ResultText[2] = "İtem kazanılmadı."
        playerCount = {'$inc': {'Player Kill Count' : 1}}
        self.db.User_Information.update_one(FindCondition(self.id), playerCount)
                  
        return self.ResultText

    def WhenWarPvNFinish(self, enemy:object) -> list:
        atwarData = {'$set':  {"AtWar" : False}}
        self.db.User_Information.update_one(FindCondition(self.id),atwarData)
        self.ResultText[0] = "Kazandınız"
        self.BATTLEMoney = (enemy.monsterJson["cr"][str(enemy.cr)])+ self.levelOfUser*randint(30,100)
        self.WinXp       = (enemy.monsterJson["cr"][str(enemy.cr)] + self.levelOfUser*randint(30,100))
        self.ResultText[2] = f"{self.BATTLEMoney} gold kazandınız ve {self.WinXp} xp kazandınız"
        if len(self.Inventory['Items']) >= self.settings['Size Inventory']:
            self.ResultText[1] = "Envanteriniz dolduğu için item kazanamadınız"
        else :
            if randint(0,100) > 50:
           
                TakedItemID     = choices(enemy.DroppedItemsID, enemy.weightsOfDroppedItems)[0]
                AddItem = Inv(self.db,self.id,TakedItemID)
                result  = AddItem.addItem()
                if result == True:
                    itemname = AddItem.itemname    
                    self.ResultText[1]   = f"self.{itemname} itemi envanterinize eklendi"
                  
                
                else :
                    return 

            else:
                self.ResultText[1] = "İtem düşmedi"
        
        dataOFMoney   = {"$inc" : {'Money' : self.BATTLEMoney,"Npc Kill Count":1}}
        self.db.User_Information.update_one(FindCondition(self.id), dataOFMoney)
        TotalXp = self.WinXp + self.XpofUSer
       
        if TotalXp >= self.MaxXpofUSer:
           
            i = 1
            statsPoint = 0
            while True:
                
                if self.levelOfUser+i >= 21:
                    tempMaxXp = self.MaxXpofUSer+200000
                    statsPoint = 5
                    
                    break
                tempMaxXp = self.player["Levels"][str(self.levelOfUser+i)]
              
                statsPoint += self.player["Statpoint"][str(self.levelOfUser+i)]
              
                if self.levelOfUser+i > 20:
                    self.proficiency +=1

                else:
                   
                    self.proficiency = self.player["proficiency"][str(self.levelOfUser+i)]
                  
                
                self.maxHP += (10 + roll('1d10'))
               
                if TotalXp < tempMaxXp:
                  
                    break
             
                i+=1

            self.MaxXpofUSer = tempMaxXp
       
            self.levelOfUser += i
          
            if self.levelOfUser in [6,7,8,9,10]:
                
                level = 6
            elif self.levelOfUser in [11,12,13,14,15]:
                
                level = 11

            elif self.levelOfUser >= 16:
                
                level = 16
            else:
                
                level = 1
           
            newSkill = self.player['SkillsLevels'][self.ClassOfUser][str(level)]
        
            skillupdate = {'$set': {'skill': newSkill}}
          
            self.db.userBattle.update_one(FindCondition(self.id), skillupdate)
            
           
            statsPointData = {'$inc' : {'Stats Points' : statsPoint}, '$set': {'proficiency' : self.proficiency} }
           
            self.db.User_Information.update_one(FindCondition(self.id), statsPointData)
          
           
        dataofBattleUser = {"$set" : {'Exp' : TotalXp, "MaxExp": self.MaxXpofUSer, 'Level': self.levelOfUser,'MaxHp': self.maxHP}}
      
        self.db.userBattle.update_one(FindCondition(self.id), dataofBattleUser)
       
        return  self.ResultText



class Monsters():
    def __init__(self,db:object,id:int) -> None:
        self.db = db
        self.id = id #monster id
        self.Damage  = 0
        with open('Cog\jsons\monster.json',encoding='utf-8') as f:
            self.monsterJson  = json.load(f)
        self.ResultText = ['','','']
        self.Critick = False #kritik vuruldu mu
        self.CritickDamage  = 0
    

    def Load_MonsterInformation(self):
        monster              = self.db.Monsters.find_one(FindCondition(self.id))
        self.monsterName          = monster['name'] 
        self.HP      = roll(monster['healt die'])
        self.strBonusofMonster    = bonus(monster['str'])
        self.AC  = monster['armor class']
        self.UserDex = monster['dex']
        self.UserInt = monster['int']
        self.UserCons = monster['cons']
        self.attacksOfMonster     = monster['Attacks'] #dict
        self.droppedItems         = monster['items']
        self.cr                   = monster['cr']   #list
        self.maxHP         = self.HP
        self.weightsOfDroppedItems:list  = []
        self.DroppedItemsID:list         = []
        for item in self.droppedItems:
            itemInfo = self.db.Items.find_one(FindCondition(item["id"]))
            self.DroppedItemsID.append(item['id'])
            self.weightsOfDroppedItems.append(itemInfo['weight'])

        self.damageBonusofMonster = monster['damageBonus']
        self.attackBonusofMonster = monster['attackBonus']
        self.weightOfMonster      = monster['weight']
        self.UnSuccessfullAttack  = False
        self.disadvantageAttack   = False
        self.advantageAttack      = True
        self.Damage = 0
      

    def Common_Roll(self)-> int:
        Values = (roll('1d20'),roll('1d20'))
        if self.advantageAttack:
            return max(Values)
        elif self.disadvantageAttack:
            return min(Values)
        elif self.advantageAttack == False and self.disadvantageAttack == False:
            return roll('1d20')
    
    def attack(self):
        attakNumber = randint(0, len(self.attacksOfMonster)-1)
        self.Attack = self.attacksOfMonster[attakNumber]
        self.CommondRoll  = self.Common_Roll()
        self.disadvantageAttack = False
        self.AttackRoll   = self.CommondRoll + self.strBonusofMonster + self.attackBonusofMonster
        self.Damage       = roll(self.Attack['Damage Dice']) + self.strBonusofMonster + self.damageBonusofMonster


    def Win(self, Player:object):
        self.ResultText[0] = "Kaybettiniz"
        BATTLEMoney        = (self.monsterJson["cr"][str(self.cr)])+ Player.levelOfUser*randint(30,100)
        UserMoney = self.db.User_Information.find_one(FindCondition(Player.id), {"Money":1})
        UserMoney = UserMoney['Money']
        UserMoney -= BATTLEMoney
        if UserMoney < 0:
            UserMoney = 0
        
        dataOFMoney = {"$set" : {"Money" : UserMoney}}
        
        self.db.User_Information.update_one(FindCondition(Player.id), dataOFMoney)
        UserInventory = Player.Inventory['Items']
        if len(UserInventory) == 0:
                self.ResultText[1] = "Envanteriniz boş olduğu için item kaybetmediniz"
        else:#Settings
                if  randint(0,100) >= 70:
                    itemIndex     = randint(0,len(UserInventory)-1)
                    BATTLEItem    = UserInventory[itemIndex]
                    removeItem = Inv(self.db, Player.id, BATTLEItem['id'])
                    result = removeItem.removeItem()
                    if result == True:
                        self.ResultText[1] = f"{BATTLEItem['Name']} elinizden uçtu gitti"
                
                else:
                    self.ResultText[1] = "İtem kaybetmediniz"

                self.ResultText[2]     = f"{BATTLEMoney} gold kaybettiniz."
        
                lose_Time = datetime.now()
                DataLog     = {
                    "id" : Player.id,
                    "Type" : 1,
                    "Lose Time": lose_Time
                }
                self.db.Logs.insert_one(DataLog)
        return self.ResultText

        
                





