from tkinter.ttk import Progressbar
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO
import requests
import math
import os
import time
import json

gitMainPath = "https://raw.githubusercontent.com/pedrohpf/Filter-Data-Test/main/"
data = requests.get(gitMainPath + "db.json").json()

with open("settings.json") as file:
	settings = json.load(file)
	settingsTypes = list(data["settings"].keys())
	settingsType = settingsTypes[settings["selected"]]

filterLevels = data["filterLevels"]
champColumns = data["settings"][settingsType]["champColumns"]
windowSize = data["settings"][settingsType]["windowSize"]
champProfilesResizeArr = data["settings"][settingsType]["champProfilesResize"]
champProfilesResize = (champProfilesResizeArr[0], champProfilesResizeArr[1])
champProfilesExt = data["settings"][settingsType]["champProfilesExt"]
champProfilesFolder = data["settings"][settingsType]["champProfilesFolder"]

filters = data["filters"]
teamAttributes = data["teamAttributes"]
champs = data["champs"]
synergies = data["synergies"]

nameFilters = [""]
champNames = list(champs.keys())
filterTypes = list(filters.keys())
teamAttributesTypes = list(teamAttributes.keys())

champProfiles = {}
levelBars = {}
synergyChampLabels = []
chosenChampNames = []
chosenChampLabels = []
champLabels = {}
os.makedirs(champProfilesFolder, exist_ok=True)
for i in range(len(champNames)):
	path = champProfilesFolder + champNames[i] + champProfilesExt
	if not os.path.exists(path):
		champProfile = requests.get(gitMainPath + path).content
		with open(path, "wb") as handler:
			handler.write(champProfile)

#####################################################################################################################

def createChamp(root, row, column, champProfile = None, champName = None):
	champLabel = Label(root, image=champProfile)
	champLabel.grid(row = row, column = column)
	champLabel.champProfile = champProfile
	champLabel.champName = champName
	return champLabel

def showChamp(champLabel, champProfile, champName):
	champLabel.grid()
	champLabel.configure(image=champProfile)
	champLabel.champName = champName

def hideChamp(champLabel, fullClear = True):
	champLabel.grid_remove()
	if fullClear:
		champLabel.configure(image=None)
		champLabel.champName = None

def placeChamp(champLabel, row, column):
	champLabel.grid(row = row, column = column)

def updateSynergies():
	for i in range(len(synergyChampLabels)):
		for j in range(len(synergyChampLabels[i])):
			hideChamp(synergyChampLabels[i][j])

	if len(chosenChampNames)>0:
		synergyGoodVs = synergies[chosenChampNames[-1]]["goodvs"][0:5]
		synergyBadVs = synergies[chosenChampNames[-1]]["goodvs"][:-6:-1]
		synergyGoodWith = synergies[chosenChampNames[-1]]["goodwith"][0:5]

		showChamp(synergyChampLabels[0][0], champLabels[chosenChampNames[-1]].champProfile, champLabels[chosenChampNames[-1]].champName)
		for i in range(len(synergyGoodVs)):
			showChamp(synergyChampLabels[1][i], champLabels[synergyGoodVs[i]].champProfile, champLabels[synergyGoodVs[i]].champName)
		for i in range(len(synergyBadVs)):
			showChamp(synergyChampLabels[2][i], champLabels[synergyBadVs[i]].champProfile, champLabels[synergyBadVs[i]].champName)
		for i in range(len(synergyGoodWith)):
			showChamp(synergyChampLabels[3][i], champLabels[synergyGoodWith[i]].champProfile, champLabels[synergyGoodWith[i]].champName)

def clickChamp(event):
	clickedChampProfile = event.widget.champProfile
	clickedChampName = event.widget.champName

	if clickedChampName in chosenChampNames:
		for i in range(len(chosenChampLabels)):
			hideChamp(chosenChampLabels[i])
		chosenChampNames.remove(clickedChampName)

		for i in range(len(chosenChampNames)):
			showChamp(chosenChampLabels[i], champLabels[chosenChampNames[i]].champProfile, champLabels[chosenChampNames[i]].champName)

		for attribute in levelBars:
			levelBars[attribute]["value"] -= (champs[clickedChampName][attribute]/teamAttributes[attribute])*100

		updateSynergies()
	elif len(chosenChampNames)<5:
		showChamp(chosenChampLabels[len(chosenChampNames)], clickedChampProfile, clickedChampName)
		chosenChampNames.append(clickedChampName)

		for attribute in levelBars:
			levelBars[attribute]["value"] += (champs[clickedChampName][attribute]/teamAttributes[attribute])*100

		updateSynergies()

def clickChosenChamp(event):
	clickedChampName = event.widget.champName

	for i in range(len(chosenChampLabels)):
		hideChamp(chosenChampLabels[i])
	chosenChampNames.remove(clickedChampName)

	for i in range(len(chosenChampNames)):
		showChamp(chosenChampLabels[i], champLabels[chosenChampNames[i]].champProfile, champLabels[chosenChampNames[i]].champName)

	for attribute in levelBars:
		levelBars[attribute]["value"] -= (champs[clickedChampName][attribute]/teamAttributes[attribute])*100

	updateSynergies()

#####################################################################################################################

def getFilteredChamps():
	filteredChamps = []
	for champ in champs.keys():
		filteredChamps.append(champ)

	for champ in champs:
		if nameFilters[0] not in champ:
			filteredChamps.remove(champ)
		else:
			for filterElem in filters:
				if filters[filterElem]>champs[champ][filterElem]:
					filteredChamps.remove(champ)
					break

	return filteredChamps

def setFilter(filterKey, filterValue):
	if filterKey not in filters or filterValue<0 or filterValue>2: return
	filters[filterKey] = filterValue

def updateFilteredChamps():
	for i in range(len(champNames)):
		placeChamp(champLabels[champNames[i]], int(i/champColumns), i%champColumns)
		hideChamp(champLabels[champNames[i]], fullClear = False)
	filteredChamps = getFilteredChamps()
	for i in range(len(filteredChamps)):
		placeChamp(champLabels[filteredChamps[i]], int(i/champColumns), i%champColumns)
		showChamp(champLabels[filteredChamps[i]], champLabels[filteredChamps[i]].champProfile, champLabels[filteredChamps[i]].champName)

def filterNameChange(searchInput):
	nameFilters[0] = searchInput.get().replace(" ", "")
	updateFilteredChamps()

#####################################################################################################################

def displayRoot():
	root = Tk()
	root.title("Champion Filter")
	root.geometry(windowSize)

	root.grid_columnconfigure(0, weight = 1, uniform="column")
	root.grid_columnconfigure(1, weight = 2, uniform="column")
	root.grid_columnconfigure(2, weight = 1, uniform="column")
	root.grid_rowconfigure(0, weight = 1, uniform="row")

	return root

def displaySections(root):
	leftFrame = Frame(root)
	leftFrame.grid(row=0, column=0, sticky="nsew")
	leftFrame.grid_columnconfigure(0, weight = 1, uniform="column")
	leftFrame.grid_columnconfigure(1, weight = 1, uniform="column")
	leftFrame.grid_columnconfigure(2, weight = 1, uniform="column")
	for i in range(len(filterTypes)):
		leftFrame.grid_rowconfigure(i, weight = 1, uniform="row")

	middleFrame = Frame(root)
	middleFrame.grid(row=0, column=1, sticky="nsew")
	middleFrame.grid_columnconfigure(0, weight = 1, uniform="column")
	middleFrame.grid_rowconfigure(0, weight = 1, uniform="row")
	middleFrame.grid_rowconfigure(1, weight = 35, uniform="row")

	rightFrame = Frame(root)
	rightFrame.grid(row=0, column=2, sticky="nsew")
	rightFrame.grid_columnconfigure(0, weight = 1, uniform="column")
	rightFrame.grid_rowconfigure(0, weight = 3, uniform="row")
	rightFrame.grid_rowconfigure(1, weight = 6, uniform="row")
	rightFrame.grid_rowconfigure(2, weight = 1, uniform="row")
	rightFrame.grid_rowconfigure(3, weight = 10, uniform="row")

	return leftFrame, middleFrame, rightFrame

def displayFilter(root, i):
	filterLevelDescription = StringVar()
	filterLevelDescription.set(filterLevels[0])

	def filterLevelChange(scaleValue):
		setFilter(filterTypes[i], int(scaleValue))
		filterLevelDescription.set(filterLevels[int(scaleValue)])
		updateFilteredChamps()

	filterTypeLabel = Label(root, text=filterTypes[i])
	filterTypeLabel.grid(row = i, column = 0)

	filterLevelScale = Scale(root,  from_ = 0,
									to = len(filterLevels)-1,
									width = 30,
									length = 150,
									showvalue = 0,
									orient = HORIZONTAL,
									command = filterLevelChange)
	filterLevelScale.grid(row = i, column = 1)

	filterLevelLabel = Label(root, textvariable=filterLevelDescription)
	filterLevelLabel.grid(row = i, column = 2)

def displayFilters(root):
	for i in range(len(filterTypes)):
		displayFilter(root, i)

def displaySearch(root):
	searchFrame = Frame(root)
	searchFrame.grid(row=0, column=0, sticky="nsew")
	searchFrame.grid_columnconfigure(0, weight = 1, uniform="column")
	searchFrame.grid_columnconfigure(1, weight = 10, uniform="column")
	searchFrame.grid_columnconfigure(2, weight = 1, uniform="column")
	searchFrame.grid_rowconfigure(0, weight = 1, uniform="row")

	searchInput = StringVar()

	searchLabel = Label(searchFrame, text="Search:")
	searchLabel.grid(row = 0, column = 0, sticky="nsew")
	searchBar = Entry(searchFrame, textvariable = searchInput)
	searchBar.bind("<KeyRelease>", lambda event: filterNameChange(searchInput))
	searchBar.grid(row = 0, column = 1, sticky="nsew")

def displayChamps(root):
	champsFrame = Frame(root)
	champsFrame.grid(row=1, column=0, sticky="nsew")
	for i in range(champColumns):
		champsFrame.grid_columnconfigure(i, weight = 1, uniform="column")
	for i in range(math.ceil(len(champNames)/champColumns)):
		champsFrame.grid_rowconfigure(i, weight = 1, uniform="row")

	for i in range(len(champNames)):
		champLabel = createChamp(champsFrame, int(i/champColumns), i%champColumns, champProfile = champProfiles[champNames[i]], champName = champNames[i])
		champLabel.bind("<Button-1>", lambda event: clickChamp(event))
		champLabels[champNames[i]] = champLabel

def displayTeams(root):
	teamFrame = Frame(root)
	teamFrame.grid(row=0, column=0, sticky="nsew")
	teamFrame.grid_columnconfigure(0, weight = 1, uniform="column")
	teamFrame.grid_columnconfigure(1, weight = 1, uniform="column")
	teamFrame.grid_columnconfigure(2, weight = 1, uniform="column")
	teamFrame.grid_columnconfigure(3, weight = 1, uniform="column")
	teamFrame.grid_columnconfigure(4, weight = 1, uniform="column")
	teamFrame.grid_rowconfigure(0, weight = 1, uniform="row")

	for i in range(5):
		chosenChampLabel = createChamp(teamFrame, 0, i)
		chosenChampLabel.bind("<Button-1>", lambda event: clickChosenChamp(event))
		chosenChampLabels.append(chosenChampLabel)

def displayLevels(root):
	levelsFrame = Frame(root)
	levelsFrame.grid(row=1, column=0, sticky="nsew")
	levelsFrame.grid_columnconfigure(0, weight = 10, uniform="column")
	levelsFrame.grid_columnconfigure(1, weight = 13, uniform="column")
	levelsFrame.grid_columnconfigure(2, weight = 13, uniform="column")
	levelsFrame.grid_columnconfigure(3, weight = 10, uniform="column")
	for i in range(len(teamAttributesTypes)):
		levelsFrame.grid_rowconfigure(i, weight = 1, uniform="row")

	for i in range(len(teamAttributesTypes)):
		filterTypeLabel = Label(levelsFrame, text=teamAttributesTypes[i])
		filterTypeLabel.grid(row = i, column = 1)

		levelBar = Progressbar(levelsFrame, orient = HORIZONTAL, length = 100, mode = 'determinate')
		levelBar.grid(row = i, column = 2)
		levelBars[teamAttributesTypes[i]] = levelBar

def displaySynergies(root):
	synergiesFrame = Frame(root)
	synergiesFrame.grid(row=3, column=0, sticky="nsew")
	synergiesFrame.grid_columnconfigure(0, weight = 1, uniform="column")
	synergiesFrame.grid_columnconfigure(1, weight = 1, uniform="column")
	synergiesFrame.grid_columnconfigure(2, weight = 1, uniform="column")
	for i in range(8):
		synergiesFrame.grid_rowconfigure(i, weight = 1, uniform="row")

	goodVsLabel = Label(synergiesFrame, text="Good Vs")
	goodVsLabel.grid(row = 1, column = 0, sticky="nsew")
	badVsLabel = Label(synergiesFrame, text="Bad Vs")
	badVsLabel.grid(row = 1, column = 1, sticky="nsew")
	goodWithLabel = Label(synergiesFrame, text="Good With")
	goodWithLabel.grid(row = 1, column = 2, sticky="nsew")

	synergyChampLabelSelected = createChamp(synergiesFrame, 0, 1)
	synergyChampLabelSelected.bind("<Button-1>", lambda event: clickChosenChamp(event))
	synergyChampLabels.append([synergyChampLabelSelected])
	for i in range(3): #selected champ | good vs | bad vs | good with
		synergyChampLabelsType = []
		for j in range(5):
			synergyChampLabelsType.append(createChamp(synergiesFrame, j+2, i))
		synergyChampLabels.append(synergyChampLabelsType)

def loadChampProfiles():
	for i in range(len(champNames)):
		path = champProfilesFolder + champNames[i] + champProfilesExt
		image = Image.open(path).resize(champProfilesResize)
		champProfiles[champNames[i]] = ImageTk.PhotoImage(image)

def display():
	start = time.perf_counter()
	root = displayRoot()

	leftFrame, middleFrame, rightFrame = displaySections(root)
	loadChampProfiles()

	displayFilters(leftFrame)

	displaySearch(middleFrame)
	displayChamps(middleFrame)

	displayTeams(rightFrame)
	displayLevels(rightFrame)
	displaySynergies(rightFrame)
	end = time.perf_counter()
	print(end - start)

	root.mainloop()

display()
