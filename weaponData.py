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
# 加载单位相关设置
unitSettings = settings.find("units")
# 加载武器表单
gunWeapon = MyTable(sheetSettings.get("path"), sheetSettings.get("sheetName"), idField=fieldNames.get('idField'), skipRows=skipRows)
# 加载绘制设置
graphSettings = settings.find("graphSettings")

def getIDByName(name):
    return int(gunWeapon[gunWeapon[fieldNames.get("name")] == name][gunWeapon.idField].item())
class WeaponData:
    def __init__(self, id):
        self.id = id
        self.weaponRecord = gunWeapon.getRowByID(id)
        self.name = self.weaponRecord[fieldNames.get("name")].item()
        #根据射速记录模式设置fireInterval
        fireRateMode = unitSettings.get("fireRate")
        if fireRateMode == "s":
            self.fireInterval = self.weaponRecord[fieldNames.get("fireRate")].iloc[0]
        elif fireRateMode == "ms":
            self.fireInterval = self.weaponRecord[fieldNames.get("fireRate")].iloc[0] / 1000
        elif fireRateMode == "RPM":
            self.fireInterval = 60 / self.weaponRecord[fieldNames.get("fireRate")].iloc[0]
        # 获取伤害分段
        self.damageSeg = []
        temp1 = self.weaponRecord[fieldNames.get("damageSegmentation")].item().split(sheetSettings.get('separator'))
        self.damageSeg.append(float(temp1[0]))
        for i in temp1:
            self.damageSeg.append(float(i))
        # 获取伤害距离分段
        temp2 = str(self.weaponRecord[fieldNames.get("damageDistanceSegmentation")].item()).split(sheetSettings.get('separator'))
        self.posSeg = [0]
        for i in temp2:
            self.posSeg.append(float(i))
        self.posSeg.append(int(graphSettings.get("maxDistance")))
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
    def getDPS(self, distance):
        damage = self.getDamage(distance)
        DPS = damage / self.fireInterval
        return DPS
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
        data = pd.DataFrame(columns=['distance', 'STK', 'TTK', 'fireInterval', 'damage', 'fireRate', 'DPS'])
        for i in range(0,len(self.posSeg)):
            data.loc[i] = {'distance': self.posSeg[i], 
                           'STK': round(self.getSTK(self.posSeg[i], health = health),2), 
                           'TTK': round(self.getTTK(self.posSeg[i], health = health),2), 
                           'fireInterval': round(self.fireInterval,2),
                           'damage': str(self.getDamage(self.posSeg[i])) + " ({damage} * {bulletsPerShot})".format(damage = self.getDamage(self.posSeg[i], ignoreBulletsPerShot=True), bulletsPerShot = self.weaponRecord[fieldNames.get("bulletsPerShot")].iloc[0]), 
                           'fireRate': round(1/self.fireInterval*60, 0),
                           'DPS': round(self.getDPS(self.posSeg[i]),2)
                        }
        return data