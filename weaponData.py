import pandas as pd
from dataTable import *
import xml.etree.ElementTree as et

# 加载表单相关设置
settings = et.parse("settings.xml").getroot()
sheetSettings = settings.find("sheet")
skipRows = []
for i in sheetSettings.get("skipRows").split(','):
    skipRows.append(int(i))
# 加载表头名称相关设置
fieldNames = settings.find("fieldNames")
# 加载武器表单
gunWeapon = MyTable(sheetSettings.get("path"), sheetSettings.get("sheetName"), idField=fieldNames.get('idField'), skipRows=skipRows)

def getIDByName(name):
    return int(gunWeapon[gunWeapon[fieldNames.get("name")] == name][gunWeapon.idField].item())
class WeaponData:
    def __init__(self, id):
        self.id = id
        self.weaponRecord = gunWeapon.getRowByID(id)
        self.name = self.weaponRecord[fieldNames.get("name")].item()
        self.fireInterval = self.weaponRecord[fieldNames.get("fireInterval")].iloc[0]
        # 获取伤害分段
        self.damageSeg = []
        temp1 = self.weaponRecord[fieldNames.get("damageSegmentation")].item().split(sheetSettings.get('separator'))
        self.damageSeg.append(float(temp1[0]))
        for i in temp1:
            self.damageSeg.append(float(i))
        # 获取伤害距离分段
        temp2 = self.weaponRecord[fieldNames.get("damageDistanceSegmentation")].item().split(sheetSettings.get('separator'))
        self.posSeg = [0]
        for i in temp2:
            self.posSeg.append(float(i))
    def getDamage(self, distance, debug = False, ignoreBulletsPerShot = False):
        bulletsPerShot = 1
        if not ignoreBulletsPerShot: bulletsPerShot = self.weaponRecord[fieldNames.get("bulletsPerShot")].iloc[0]
        # 打印debug信息
        if debug:
            print(self.damageSeg)
            print(self.posSeg)
        for i in range(0, len(self.posSeg)):
            if distance <= int(self.posSeg[i]):
                return float(self.damageSeg[i]) * bulletsPerShot
        return 0
    def getSTK(self, distance, health = 100, debug = False):
        damage = self.getDamage(distance, debug = debug)
        STK = health//damage
        if STK * damage < health: STK += 1
        if (debug): print("damage:",damage,"STK:",STK,"fire interval:",self.fireInterval)
        return STK
    def getTTK(self, distance, health = 100, debug = False):
        damage = self.getDamage(distance, debug = debug)
        STK = self.getSTK(distance, health = health, debug = debug)
        if (debug): print("damage:",damage,"STK",STK,"fire interval:",self.fireInterval)
        # 因为第一枪不用等, STK--
        return (STK - 1) * self.fireInterval
    def getKillData(self, health = 100):
        data = pd.DataFrame(columns=['distance', 'STK', 'TTK', 'fireInterval', 'damage', 'fireRate'])
        for i in range(0,len(self.posSeg)):
            data.loc[i] = {'distance': self.posSeg[i], 
                           'STK': self.getSTK(self.posSeg[i], health = health), 
                           'TTK': self.getTTK(self.posSeg[i], health = health), 
                           'fireInterval': self.fireInterval,
                           'damage': str(self.getDamage(self.posSeg[i])) + " ({damage} * {bulletsPerShot})".format(damage = self.getDamage(self.posSeg[i]) / self.weaponRecord[fieldNames.get("bulletsPerShot")].iloc[0] , bulletsPerShot = self.weaponRecord[fieldNames.get("bulletsPerShot")].iloc[0]), 
                           'fireRate': round(1/self.fireInterval*60, 0)
                        }
        return data