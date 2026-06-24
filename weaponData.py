import pandas as pd
from dataTable import *
import xml.etree.ElementTree as et
import plotly.graph_objects as go
from hashColor import hashColor

# ============================================================
# Module-level state (initialized by init_data())
# ============================================================
settings = None
sheetSettings = None
fieldNames = None
unitSettings = None
gunWeapon = None
weapons = []
graphSettings = None
generalSettings = None
skipRows = []

# Settings derived for plotting (cached for performance)
health = 100
interpolation = "hv"
xAxis = "distance"
yAxis = "TTK"


def _load_settings():
    """Load settings from settings.xml into module globals."""
    global settings, sheetSettings, fieldNames, unitSettings, graphSettings, generalSettings, skipRows
    global health, interpolation, xAxis, yAxis

    settings = et.parse("settings.xml").getroot()
    sheetSettings = settings.find("sheet")
    fieldNames = settings.find("fieldNames")
    unitSettings = settings.find("units")
    graphSettings = settings.find("graphSettings")
    generalSettings = settings.find("general")

    skipRows = []
    for i in sheetSettings.get("skipRows").split(','):
        skipRows.append(int(i))

    health = int(generalSettings.get("health"))
    interpolation = generalSettings.get("interpolation")
    xAxis = graphSettings.get("xAxis")
    yAxis = graphSettings.get("yAxis")


def _load_weapons():
    """Read Excel sheet and rebuild the weapons list."""
    global gunWeapon, weapons

    gunWeapon = ExTable(
        sheetSettings.get("path"),
        sheetSettings.get("sheetName"),
        idField=fieldNames.get('idField'),
        skipRows=skipRows
    )

    weapons = []
    for i in range(0, len(gunWeapon)):
        weapon = gunWeapon.loc[i]
        currentData = WeaponData(weapon[gunWeapon.idField])
        weapons.append(currentData)


def init_data():
    """Initialize (or re-initialize) all data from disk."""
    _load_settings()
    _load_weapons()


def reload_data():
    """Reload all data from disk at runtime. Safe to call at any time."""
    init_data()


# ============================================================
# Original helper functions
# ============================================================

def getIDByName(name):
    return int(gunWeapon[gunWeapon[fieldNames.get("name")] == name][gunWeapon.idField].item())


def getWeaponByName(name):
    for i in weapons:
        if i.name == name:
            return i


# ============================================================
# WeaponData class (unchanged from original)
# ============================================================

class WeaponData:
    def __init__(self, id):
        self.id = id
        self.weaponRecord = gunWeapon.getRowByID(id)
        # weapon name
        self.name = self.weaponRecord[fieldNames.get("name")].item()
        # bullets per shot
        self.bulletsPerShot = self.weaponRecord[fieldNames.get("bulletsPerShot")].iloc[0]
        # fire interval
        fireRateMode = unitSettings.get("fireRate")
        if fireRateMode == "s":
            self.fireInterval = self.weaponRecord[fieldNames.get("fireRate")].iloc[0]
        elif fireRateMode == "ms":
            self.fireInterval = self.weaponRecord[fieldNames.get("fireRate")].iloc[0] / 1000
        elif fireRateMode == "RPM":
            self.fireInterval = 60 / self.weaponRecord[fieldNames.get("fireRate")].iloc[0]
        # damage segmentation
        self.damageSeg = []
        temp1 = str(self.weaponRecord[fieldNames.get("damageSegmentation")].item()).split(sheetSettings.get('separator'))
        for i in temp1:
            if (i != 'nan'):
                self.damageSeg.append(float(i))
        self.damageSeg.append(float(temp1[len(temp1) - 1]))
        # damage distance segmentation
        temp2 = []
        try:
            temp2 = str(self.weaponRecord[fieldNames.get("damageDistanceSegmentation")].item()).split(
                sheetSettings.get('separator'))
        except:
            pass
        self.posSeg = [0]
        if temp2:
            for i in temp2:
                if i != 'nan':
                    self.posSeg.append(float(i))
        self.posSeg.append(int(graphSettings.get("maxDistance")))
        # base damage
        self.baseDamage = 0
        try:
            self.baseDamage = self.weaponRecord[fieldNames.get("baseDamage")].iloc[0]
        except:
            self.baseDamage = self.getDamage(0, ignoreBulletsPerShot=True)

    def getDamage(self, distance, debug=False, ignoreBulletsPerShot=False):
        bulletsPerShot = 1
        if not ignoreBulletsPerShot:
            bulletsPerShot = self.bulletsPerShot
        if debug:
            print(self.damageSeg)
            print(self.posSeg)
        damage = 0
        for i in range(0, len(self.posSeg)):
            if distance <= float(self.posSeg[i]):
                if unitSettings.get("damageSegmentationMode") == "actual":
                    damage = float(self.damageSeg[i]) * bulletsPerShot
                elif unitSettings.get("damageSegmentationMode") == "multiplier":
                    damage = self.baseDamage * float(self.damageSeg[i]) * bulletsPerShot
                break
        return round(damage, 1)

    def getDPS(self, distance):
        damage = self.getDamage(distance)
        DPS = damage / self.fireInterval
        return DPS

    def getSTK(self, distance, health=100, debug=False):
        damage = self.getDamage(distance, debug=debug)
        STK = health // damage
        if STK * damage < health:
            STK += 1
        if debug:
            print("damage:", damage, "STK:", STK, "fire interval:", self.fireInterval)
        return STK

    def getTTK(self, distance, health=100, debug=False):
        damage = self.getDamage(distance, debug=debug)
        STK = self.getSTK(distance, health=health, debug=debug)
        if debug:
            print("damage:", damage, "STK", STK, "fire interval:", self.fireInterval)
        return (STK - 1) * self.fireInterval

    def getKillData(self, health=100):
        data = pd.DataFrame(columns=['distance', 'STK', 'TTK', 'fireInterval', 'damage', 'fireRate', 'DPS',
                                     'baseDamage'])
        for i in range(0, len(self.posSeg)):
            data.loc[i] = {
                'distance': self.posSeg[i],
                'STK': round(self.getSTK(self.posSeg[i], health=health), 2),
                'TTK': round(self.getTTK(self.posSeg[i], health=health), 2),
                'fireInterval': str(round(self.fireInterval, 2)) + " (s)",
                'damage': str(self.getDamage(self.posSeg[i])) +
                          " ({damage} * {bulletsPerShot})".format(
                              damage=self.getDamage(self.posSeg[i], ignoreBulletsPerShot=True),
                              bulletsPerShot=self.bulletsPerShot),
                'fireRate': str(round(1 / self.fireInterval * 60, 0)) + " (RPM)",
                'DPS': round(self.getDPS(self.posSeg[i]), 2),
                'baseDamage': str(self.baseDamage * self.bulletsPerShot) +
                              ' (' + str(self.baseDamage) + ' * ' + str(self.bulletsPerShot) + ') '
            }
        return data


# ============================================================
# Plotting utility functions (migrated from main.ipynb)
# ============================================================

def getTitleByWeapon(weapon):
    return weapon.name + " (ID: {})".format(str(weapon.id))


def traceWeapon(weaponToTrace, hide=False):
    hoverFields = graphSettings.get("hoverFields").split(',')
    try:
        id_val = int(weaponToTrace)
    except ValueError:
        id_val = getIDByName(weaponToTrace)
    weapon = WeaponData(id_val)
    killData = weapon.getKillData(health)
    x = killData[xAxis].tolist()
    y = killData[yAxis].tolist()

    hoverText = []
    for i in x:
        text = ''
        for j in hoverFields:
            text += j + ': ' + str(killData[killData[xAxis] == i][j].iloc[0]) + '<br>'
        hoverText.append(text)

    trace = go.Scatter(
        x=x, y=y,
        line_shape=interpolation,
        name=getTitleByWeapon(weapon),
        line=dict(color=hashColor(weapon.name)),
        hovertemplate=
        '<br><b>' + yAxis + ': %{y}</b><br>' +
        '<b>' + xAxis + ': %{x}</b><br>' +
        '%{text}',
        text=hoverText,
        visible=not hide
    )
    return trace


def traceAll(hide=False):
    output = []
    for i in weapons:
        output.append(traceWeapon(i.id, hide=hide))
    return output


def plotAll(figure, hide=False):
    figure.add_traces(traceAll(hide=hide))


def updateLayout(figure):
    figure.update_layout(
        hovermode='x unified',
        xaxis_title=xAxis,
        yaxis_title=yAxis,
        width=float(generalSettings.get("sizeX")),
        height=float(generalSettings.get("sizeY")),
    )


def getMasterFigure(hide=False):
    fig = go.Figure()
    plotAll(fig, hide=hide)
    updateLayout(fig)
    return fig


# ============================================================
# Initialize data on first import
# ============================================================
init_data()
