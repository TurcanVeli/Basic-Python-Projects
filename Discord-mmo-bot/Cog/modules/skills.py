import json


class Skill():
    def __init__(self, Class:str, Level:int, skill:str) -> None:
        self.ClassofUser = Class
        self.UserLevel = Level #User Level
        self.skill = skill#skill name
        self.skillLevel = 1
        with open('Cog\jsons\player.json',encoding = 'utf-8') as f:
            self.player  = json.load(f)
        self.SkillData = self.player['Class'][self.ClassofUser][self.skill]
        self.haveActiveTurn = False
        self.haveİyileşme_miktarı = False
        
       
        
    def check_SkillType(self) -> bool:#Aktif -> True, Pasif -> False
        TypeOfSkill = self.SkillData["Skill Türü"]
        if TypeOfSkill == "Aktif":
            return True
        else:
            return False
    
    def check_SkillLevel(self) -> int:#returns skill level.
        mod = self.UserLevel%5
        if mod == 0:
            mod = 5
        print("[*] Skill Seviye", mod)
        return mod #skill level

    def BS(self) -> int :#returns bs of skill
        skillBS = self.SkillData["Bekleme Süresi"]
        if skillBS != 0:
            skillBS -= (self.skillLevel-1)
            return skillBS
        else :
            return 0

