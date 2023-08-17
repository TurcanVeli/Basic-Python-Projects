
import random


def do_bar(max:int,currentPoint:int,dash:int):
  dashConvert = int(max/dash)            
  currentDashes = int(currentPoint/dashConvert)            
  remainingHealth = dash - currentDashes       

  healthDisplay = '-' * currentDashes                
  remainingDisplay = ' ' * remainingHealth             
  percent = str(int((currentPoint/max)*100)) + "%"     
  bar = "|" + healthDisplay + remainingDisplay + "|"
  percent = "         " + percent
  return bar,percent       

def bonus(stat:int) -> int :
    if stat == 8:
        return -1
    stat -= 8
    stat = int(stat/2)-1
    return stat

def roll(dice:str) -> int: # 2d6 or 4d5 
    rolling = []
    g = dice.split('d')
    if "+" in dice:
        a = g[1].split("+")
        g.pop()
        for i in a:
            g.append(i)
    else :
        g.append("0")
    
    try:
        for x in range(int(g[0])):
            rolling.append(random.randint(1,int(g[1])))
    except Exception as e:
        print(e)
        return False
    result = sum(rolling) + int(g[2])    
    return result

    





def FindCondition(id:int) -> dict:
    return {"_id" : id}



async def order(tuples:list,count:int) -> list:#tuples is a list that contains tuples
    size = len(tuples)
  
    for index, i in enumerate(tuples):
        if index+1 < size:
         
            if i[2] > tuples[index+1][2]:
                tuples.insert(index,tuples[index+1])
                tuples.pop(index+2)
    count -= 1
    if count == 0:    
       
        return tuples
    return await order(tuples,count)