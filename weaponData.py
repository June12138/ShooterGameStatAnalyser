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
        #武器名称
        self.name = self.weaponRecord[fieldNames.get("name")].item()
        # 获取每发攻击子弹数量
        self.bulletsPerShot = self.weaponRecord[fieldNames.get("bulletsPerShot")].iloc[0]
        #根据射速记录模式设置fireInterval
        fireRateMode = unitSettings.get("fireRate")
        if fireRateMode == "s":
            # 秒间隔模式
            self.fireInterval = self.weaponRecord[fieldNames.get("fireRate")].iloc[0]
        elif fireRateMode == "ms":
            # 毫秒间隔模式
            self.fireInterval = self.weaponRecord[fieldNames.get("fireRate")].iloc[0] / 1000
        elif fireRateMode == "RPM":
            # RPM模式
            self.fireInterval = 60 / self.weaponRecord[fieldNames.get("fireRate")].iloc[0]
        # 获取伤害分段
        self.damageSeg = []
        temp1 = str(self.weaponRecord[fieldNames.get("damageSegmentation")].item()).split(sheetSettings.get('separator'))
        self.damageSeg.append(float(temp1[0]))
        for i in temp1:
            if (i != 'nan'): self.damageSeg.append(float(i))
        # 获取伤害距离分段
        temp2 = []
        # 为了让damageDistanceSegmentation成为可以选填，做个保护
        try:
            temp2 = str(self.weaponRecord[fieldNames.get("damageDistanceSegmentation")].item()).split(sheetSettings.get('separator'))
        except:
            pass
        self.posSeg = [0]
        if (temp2):
            for i in temp2:
                if (i != 'nan'): self.posSeg.append(float(i))
        self.posSeg.append(int(graphSettings.get("maxDistance")))
        # 获取基础伤害
        self.baseDamage = 0
            # 因为基础伤害是选填项，做个保护
        try:
            # 表里找得到就用表里的
            self.baseDamage = self.weaponRecord[fieldNames.get("baseDamage")].iloc[0]
        except:
            # 否则直接用零距离上的伤害
            self.baseDamage = self.getDamage(0, ignoreBulletsPerShot= True)
    def getDamage(self, distance, debug = False, ignoreBulletsPerShot = False):
        # 获取子弹数量
        bulletsPerShot = 1
        # 如果不忽略子弹数量，则获取子弹数量
        if not ignoreBulletsPerShot: bulletsPerShot = self.bulletsPerShot
        # 打印debug信息
        if debug:
            print(self.damageSeg)
            print(self.posSeg)
        # 遍历距离段
        damage = 0
        for i in range(0, len(self.posSeg)):
            # 如果距离小于等于当前距离段，则返回对应的伤害值
            if distance <= int(self.posSeg[i]):
                # 如果伤害衰减是按实际伤害记录，则直接返回伤害值乘以子弹数量
                if (unitSettings.get("damageSegmentationMode") == "actual"):
                    damage = float(self.damageSeg[i]) * bulletsPerShot
                # 如果伤害衰减是按乘数记录，则返回基础伤害乘以伤害衰减乘以子弹数量
                elif (unitSettings.get("damageSegmentationMode") == "multiplier"):
                    damage = self.baseDamage * float(self.damageSeg[i]) * bulletsPerShot
                break
        return round(damage, 1)
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
        data = pd.DataFrame(columns=['distance', 'STK', 'TTK', 'fireInterval', 'damage', 'fireRate', 'DPS', 'baseDamage'])
        for i in range(0,len(self.posSeg)):
            data.loc[i] = {'distance': self.posSeg[i], 
                           'STK': round(self.getSTK(self.posSeg[i], health = health),2), 
                           'TTK': round(self.getTTK(self.posSeg[i], health = health),2), 
                           'fireInterval': str(round(self.fireInterval,2)) + " (s)",
                           'damage': str(self.getDamage(self.posSeg[i])) + " ({damage} * {bulletsPerShot})".format(damage = self.getDamage(self.posSeg[i], ignoreBulletsPerShot=True), bulletsPerShot = self.bulletsPerShot), 
                           'fireRate': str(round(1/self.fireInterval*60, 0)) + " (RPM)",
                           'DPS': round(self.getDPS(self.posSeg[i]),2),
                           'baseDamage': str(self.baseDamage * self.bulletsPerShot) + ' (' + str(self.baseDamage) + ' * ' + str(self.bulletsPerShot) + ') '
                        }
        return data
# 创建一个包含所有武器数据的数组
weapons = []
for i in range(0, len(gunWeapon)):
    weapon = gunWeapon.loc[i]
    currentData = WeaponData(weapon[gunWeapon.idField])
    weapons.append(currentData)
def getWeaponByName(name):
    for i in weapons:
        if i.name == name:
            return i