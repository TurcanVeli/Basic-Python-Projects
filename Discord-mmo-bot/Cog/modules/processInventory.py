from discord import Object
from types import NoneType
from Cog.modules.utils import*

class Inventory:
    def __init__(self,db:object ,id:int, itemid:int,adet:int = 1) -> None:
        self.id = id #user id
        self.itemid =  itemid
        self.adet = adet
        self.db = db

    def addItem(self) -> bool:
        having = 1
           
        addedItem = self.db.Items.find_one({"_id": self.itemid})
        if type(addedItem) == NoneType:
            return False
        
        self.itemname = addedItem['name']
        UserEnv = self.db.UserEnv.find_one(FindCondition(self.id))
        if type(UserEnv) == NoneType:
            return False
        
        envanter = UserEnv["Items"]
        for index,i in enumerate(envanter):
            if i["id"] == self.itemid:
                
                
                data = {
                    "$inc" : {
                        f"Items.{index}.Having" : self.adet
                    }
                }
                try:
                    self.db.UserEnv.update_one(FindCondition(self.id),data)
                except Exception as e:
                    print(e)
                    return False

                return True
        
        toinsert = {"id": self.itemid, "Name": self.itemname, "Having" : self.adet,"Using": False }
        data = {"$addToSet" : {'Items': toinsert }}
        try:
            self.db._uptadeUserEnv(FindCondition(self.id),data)
        except Exception as e:
            print(e)
            return False
        
        return True        
    
    def removeItem(self)-> bool:
        deletedItem  = self.db.Items.find_one(FindCondition(self.itemid))
        if type(deletedItem) == NoneType:
            return False
        part = deletedItem["part"]
        UserEnv = self.db.UserEnv.find_one(FindCondition(self.id))
        if type(UserEnv) == NoneType:
            return False
        Envanter = UserEnv["Items"]
        for index,i in enumerate(Envanter):
            if i["id"] == self.itemid:
                having = i["Having"] - self.adet
                if having < 0:
                    return False
                if having == 0:
                    
                    if i["Using"] == True:
                        data = {
                        "$pull" : {"Items" : {"id": self.itemid}},
                        "$set" : {f"{part}" : {"id":0,"Name":"Boş"}}
                        }
                        
                        if part == "Weapon":
                            battleUpdate = {"$set": 
                            {
                                "Damage" : "Yok"
                            }
                            }
                        elif part in ["Kask", "Body", "foot"]:
                            
                            battleUpdate = {"$inc": 
                            {
                                "Armor Class" : -deletedItem["buffac"]
                            }
                            }
                        
                        elif part == "Food":
                            pass

                        elif part == "Aksesuar":
                            pass 

                        try:
                            self.db.userBattle.update_one(FindCondition(self.id),battleUpdate)
                        except Exception as e:
                            return False
                    else:
                        data = {
                        "$pull" : {"Items" : {"id": self.itemid}}}
                    
                    try:
                        self.db.UserEnv.update_one(FindCondition(self.id),data)
                    except Exception as e:
                        return False
                    
                    return True
                else:
                    
                    data = {
                        "$inc" : {
                            f"Items.{index}.Having" : -self.adet
                    }
                    }
                    try:                        
                        self.db.UserEnv.update_one(FindCondition(self.id),data)
                    except Exception as e:
                        return False
                    return True
        return False
