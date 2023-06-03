import tkinter as tk, configparser as cp, math, requests, os
from datetime import datetime
from tkinter import ttk
class RWConfigFile():
    def __init__(self, filename):
        self.filename = filename
        self.config = cp.ConfigParser()
    def ReadKey(self, sectionName, keyName):
        self.config.read(self.filename)
        try:
            value = self.config.get(sectionName, keyName)
            return value
        except cp.NoOptionError:
            return None
    def WriteKey(self, sectionName, keyName, value):
        self.config.read(self.filename)
        try:
            self.config.add_section(sectionName)
        except cp.DuplicateSectionError:
            pass
        self.config.set(sectionName, keyName, value)
        with open(self.filename, "w") as configFile:
            self.config.write(configFile)
Parser = RWConfigFile("config.ini")

allPrices = {"GBP" : [[96.37, 16400],
                     [48.18, 7300], 
                     [24.08, 3600],
                     [9.62, 1390],
                     [4.80, 675]],
             "USD" : [[119.99, 16400],
                     [59.99, 7300],
                     [29.99, 3600],
                     [11.99, 1390],
                     [5.99, 675]]}



regionalIndicator = Parser.ReadKey("SETTINGS", "region")
resultMode = Parser.ReadKey("SETTINGS", "priceFormat")
currentItem = ""
lastPrice = ""
def setRegion(region):
    global regionalIndicator
    regionalIndicator = region
    Parser.WriteKey("SETTINGS", "region", region)

def setResultMode(mode):
    global resultMode
    resultMode = mode
    Parser.WriteKey("SETTINGS", "priceFormat", mode)

def savePrice():
    global resultMode
    if resultLabel.cget("text") == "":
        return 0
    else:
        if itemNameInput.get() != "":
            name = itemNameInput.get()
        else:
            name = "Untitled"
        filename = "saves/" + name + "_" + str(datetime.today().strftime("%Y-%m-%d-%H-%M-%S"))
        if resultMode == "SIMPLE":
            resultMode = "COMPLEX" 
            file = open(filename.replace(" ", ""), "w+")
            file.write(lastPrice + regionalIndicator)
        else:
            file = open(filename.replace(" ", ""), "w+")
            file.write(lastPrice + regionalIndicator)

def refreshSaves():
    files = []
    if not itemNameInput.get():
        itemName = "Untitled"
    else:
        itemName = itemNameInput.get()
    print(itemName)
    for file in os.listdir("saves/"):
        if itemName in file:
            files.append(file)
    saveBox.config(values=files)

def calculatePrice(region, allPrices, resultMode):
    global lastPrice
    total = [[],
             []]
    itemPrice = itemPriceInput.get()
    cookiePrice = requests.get("https://api.hypixel.net/skyblock/bazaar").json()["products"]["BOOSTER_COOKIE"]["quick_status"]["sellPrice"]
    gemsNeeded = math.ceil(int(itemPrice) / int(cookiePrice)) * 325
    gemPrices = allPrices[region]

    while gemsNeeded > 0:
        gemsSubtracted = False
        for offer in gemPrices:
            if offer[1] <= gemsNeeded:
                total[0].append(offer[0])
                total[1].append(offer[1])
                gemsNeeded -= offer[1]
                gemsSubtracted = True
        if not gemsSubtracted and gemsNeeded > 0:
            total[0].append(gemPrices[4][0])
            total[1].append(gemPrices[4][1])
            gemsNeeded -= gemPrices[4][1]
    if resultMode == "SIMPLE":
        resultLabel.config(text="Total : " + str(format(sum(total[0]), ".2f")) + region)
    else:
        resultLabel.config(text= f"""Total:
        {total[1].count(16400)} Packages of 16400 gems at {gemPrices[0][0]} {region}
        {total[1].count(7300)} Packages of 7300 gems at {gemPrices[1][0]} {region}
        {total[1].count(3600)} Packages of 3600 gems at {gemPrices[2][0]} {region}
        {total[1].count(1390)} Packages of 1390 gems at {gemPrices[3][0]} {region}
        {total[1].count(675)} Packages of 675 gems at {gemPrices[4][0]} {region}
        Totalling: {format(sum(total[0]), ".2f")} {region}""")
    lastPrice = str(format(sum(total[0]), ".2f"))
window = tk.Tk()
window.geometry("400x400")
window.title("Hypixel Skyblock Pay To Win Calculator (v1.0)")
topMenu = tk.Menu(window)

regionMenu = tk.Menu(topMenu, tearoff=0)
regionMenu.add_command(label="GBP", command=lambda: setRegion("GBP"))
regionMenu.add_separator()
regionMenu.add_command(label="USD", command=lambda: setRegion("USD"))
regionMenu.add_separator()
topMenu.add_cascade(label="Region", menu=regionMenu)

resultModeMenu = tk.Menu(topMenu, tearoff=0)
resultModeMenu.add_command(label="Simple", command=lambda: setResultMode("SIMPLE"))
resultModeMenu.add_separator()
resultModeMenu.add_command(label="Complex", command=lambda: setResultMode("COMPLEX"))
resultModeMenu.add_separator()
topMenu.add_cascade(label="Result Mode", menu=resultModeMenu)

savePriceMenu = tk.Menu(topMenu, tearoff=0)
savePriceMenu.add_command(label="Coming Soon!", command=None)
savePriceMenu.add_separator()
topMenu.add_cascade(label="Saved Price Checks", menu=savePriceMenu)

window.config(menu=topMenu)

itemPriceLabel = tk.Label(text="Enter item price:")
itemPriceInput = tk.Entry()
itemPriceLabel.place(x=50, y=50)
itemPriceInput.place(x=225, y=50)

itemNameLabel = tk.Label(text="Enter item name (Optional):")
itemNameInput = tk.Entry()
itemNameLabel.place(x=50, y=25)
itemNameInput.place(x=225, y=25)


saveBox = ttk.Combobox(state="readonly", values = [])
saveBox.place(x=100, y=150)

resultLabel = tk.Label()
resultLabel.place(x=50, y=200)

calculateButton = tk.Button(text="Calculate", command=lambda: calculatePrice(regionalIndicator, allPrices, resultMode))
calculateButton.place(x = 50, y= 75)

saveButton = tk.Button(text="Save Price", command=lambda: savePrice())
saveButton.place(x = 150, y= 75)

calculateButton = tk.Button(text="Refresh Saves", command=lambda: refreshSaves())
calculateButton.place(x = 250, y= 75)


window.mainloop()
