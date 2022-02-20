from tkinter.ttk import Progressbar
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO
import requests
import math

data = requests.get("https://raw.githubusercontent.com/pedrohpf/Filter-Data-Test/main/db.json").json()
filters = data["filters"]
teamAttributes = data["teamAttributes"]
champs = data["champs"]
synergies = data["synergies"]
nameFilters = [""]

#####################################################################################################################

def createChamp(root, champName, champProfile):
	champLabel = Label(root, image=champProfile)
	champLabel.image = champProfile
	champLabel.name = champName
	return champLabel

def placeChamp(champLabel, row, column):
	champLabel.grid(row = row, column = column)

def hideChamp(champLabel):
	champLabel.grid_remove()

def updateSynergies(synergyChampLabels, chosenChampNames):
	for champName in champs:
		for i in range(len(synergyChampLabels)):
			hideChamp(synergyChampLabels[i][champName])

	if len(chosenChampNames)>0:
		synergyGoodVs = synergies[chosenChampNames[-1]]["goodvs"][0:5]
		synergyBadVs = synergies[chosenChampNames[-1]]["goodvs"][:-6:-1]
		synergyGoodWith = synergies[chosenChampNames[-1]]["goodwith"][0:5]

		placeChamp(synergyChampLabels[0][chosenChampNames[-1]], 0, 1)
		for i in range(len(synergyGoodVs)):
			placeChamp(synergyChampLabels[1][synergyGoodVs[i]], i+2, 0)
		for i in range(len(synergyBadVs)):
			placeChamp(synergyChampLabels[2][synergyBadVs[i]], i+2, 1)
		for i in range(len(synergyGoodWith)):
			placeChamp(synergyChampLabels[3][synergyGoodWith[i]], i+2, 2)

def clickChamp(event, chosenChampNames, chosenChampLabels, synergyChampLabels, levelBars):
	if event.widget.name not in chosenChampNames and len(chosenChampNames)<5:
		placeChamp(chosenChampLabels[event.widget.name], 0, len(chosenChampNames))
		chosenChampNames.append(event.widget.name)

		for attribute in levelBars:
			levelBars[attribute]["value"] += (champs[event.widget.name][attribute]/teamAttributes[attribute])*100

		updateSynergies(synergyChampLabels, chosenChampNames)

def clickChosenChamp(event, chosenChampNames, chosenChampLabels, synergyChampLabels, levelBars):
	for champName in chosenChampNames:
		hideChamp(chosenChampLabels[champName])
	chosenChampNames.remove(event.widget.name)
	for i in range(len(chosenChampNames)):
		placeChamp(chosenChampLabels[chosenChampNames[i]], 0, i)

	for attribute in levelBars:
		levelBars[attribute]["value"] -= (champs[event.widget.name][attribute]/teamAttributes[attribute])*100

	updateSynergies(synergyChampLabels, chosenChampNames)

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

def updateFilteredChamps(champLabels, champColumns):
	for champName in champLabels:
		hideChamp(champLabels[champName])
	filteredChamps = getFilteredChamps()
	for i in range(len(filteredChamps)):
		placeChamp(champLabels[filteredChamps[i]], int(i/champColumns), i%champColumns)

def displayLevelBar(root, filterTypes, i):
	filterTypeLabel = Label(root, text=filterTypes[i])
	filterTypeLabel.grid(row = i, column = 1)

	levelBar = Progressbar(root, orient = HORIZONTAL, length = 100, mode = 'determinate')
	levelBar.grid(row = i, column = 2)

	return levelBar

def filterNameChange(searchInput, champLabels, champColumns):
	nameFilters[0] = searchInput.get().replace(" ", "")
	updateFilteredChamps(champLabels, champColumns)

def displaySynergies(root):
	goodVsLabel = Label(root, text="Good Vs")
	goodVsLabel.grid(row = 1, column = 0, sticky="nsew")
	badVsLabel = Label(root, text="Bad Vs")
	badVsLabel.grid(row = 1, column = 1, sticky="nsew")
	goodWithLabel = Label(root, text="Good With")
	goodWithLabel.grid(row = 1, column = 2, sticky="nsew")

def displaySearch(root, champLabels, champColumns):
	searchInput = StringVar()

	searchLabel = Label(root, text="Search:")
	searchLabel.grid(row = 0, column = 0, sticky="nsew")
	searchBar = Entry(root, textvariable = searchInput)
	searchBar.bind("<KeyRelease>", lambda event: filterNameChange(searchInput, champLabels, champColumns))
	searchBar.grid(row = 0, column = 1, sticky="nsew")

def displayFilter(root, champLabels, champColumns, filterTypes, filterLevels, i):
	filterTypeLabel = Label(root, text=filterTypes[i])

	filterLevelDescription = StringVar()

	def filterLevelChange(scaleValue):
		setFilter(filterTypes[i], int(scaleValue))
		filterLevelDescription.set(filterLevels[int(scaleValue)])
		updateFilteredChamps(champLabels, champColumns)
	filterLevelChange(0)

	filterLevelScale = Scale(root,  from_ = 0,
									to = len(filterLevels)-1,
									width = 30,
									length = 150,
									showvalue = 0,
									orient = HORIZONTAL,
									command = filterLevelChange)

	filterLevelLabel = Label(root, textvariable=filterLevelDescription)

	filterTypeLabel.grid(row = i, column = 0)
	filterLevelScale.grid(row = i, column = 1)
	filterLevelLabel.grid(row = i, column = 2)

#High need of cleaning up, but who's gonna do that?
def display(windowSize, champColumns):
	champNames = list(champs.keys())
	filterTypes = list(filters.keys())
	teamAttributesTypes = list(teamAttributes.keys())
	filterLevels = ["No Filter", "Medium Filter", "Max Filter"]

	root = Tk()
	root.title("Champion Filter")
	root.geometry(windowSize)

	root.grid_columnconfigure(0, weight = 1, uniform='column')
	root.grid_columnconfigure(1, weight = 2, uniform='column')
	root.grid_columnconfigure(2, weight = 1, uniform='column')
	root.grid_rowconfigure(0, weight = 1, uniform='row')

	leftFrame = Frame(root)
	leftFrame.grid(row=0, column=0, sticky="nsew")
	leftFrame.grid_columnconfigure(0, weight = 1, uniform='column')
	leftFrame.grid_columnconfigure(1, weight = 1, uniform='column')
	leftFrame.grid_columnconfigure(2, weight = 1, uniform='column')
	for i in range(len(filterTypes)):
		leftFrame.grid_rowconfigure(i, weight = 1, uniform='row')

	middleFrame = Frame(root)
	middleFrame.grid(row=0, column=1, sticky="nsew")
	middleFrame.grid_columnconfigure(0, weight = 1, uniform='column')
	middleFrame.grid_rowconfigure(0, weight = 1, uniform='row')
	middleFrame.grid_rowconfigure(1, weight = 35, uniform='row')

	rightFrame = Frame(root)
	rightFrame.grid(row=0, column=2, sticky="nsew")
	rightFrame.grid_columnconfigure(0, weight = 1, uniform='column')
	rightFrame.grid_rowconfigure(0, weight = 3, uniform='row')
	rightFrame.grid_rowconfigure(1, weight = 6, uniform='row')
	rightFrame.grid_rowconfigure(2, weight = 1, uniform='row')
	rightFrame.grid_rowconfigure(3, weight = 10, uniform='row')

	#Middle
	searchFrame = Frame(middleFrame)
	searchFrame.grid(row=0, column=0, sticky="nsew")
	searchFrame.grid_columnconfigure(0, weight = 1, uniform='column')
	searchFrame.grid_columnconfigure(1, weight = 10, uniform='column')
	searchFrame.grid_columnconfigure(2, weight = 1, uniform='column')
	searchFrame.grid_rowconfigure(0, weight = 1, uniform='row')

	champsFrame = Frame(middleFrame)
	champsFrame.grid(row=1, column=0, sticky="nsew")
	for i in range(champColumns):
		champsFrame.grid_columnconfigure(i, weight = 1, uniform='column')
	for i in range(math.ceil(len(champNames)/champColumns)):
		champsFrame.grid_rowconfigure(i, weight = 1, uniform='row')

	#Right
	teamFrame = Frame(rightFrame)
	teamFrame.grid(row=0, column=0, sticky="nsew")
	teamFrame.grid_columnconfigure(0, weight = 1, uniform='column')
	teamFrame.grid_columnconfigure(1, weight = 1, uniform='column')
	teamFrame.grid_columnconfigure(2, weight = 1, uniform='column')
	teamFrame.grid_columnconfigure(3, weight = 1, uniform='column')
	teamFrame.grid_columnconfigure(4, weight = 1, uniform='column')
	teamFrame.grid_rowconfigure(0, weight = 1, uniform='row')

	levelsFrame = Frame(rightFrame)
	levelsFrame.grid(row=1, column=0, sticky="nsew")
	levelsFrame.grid_columnconfigure(0, weight = 10, uniform='column')
	levelsFrame.grid_columnconfigure(1, weight = 13, uniform='column')
	levelsFrame.grid_columnconfigure(2, weight = 13, uniform='column')
	levelsFrame.grid_columnconfigure(3, weight = 10, uniform='column')
	for i in range(len(teamAttributesTypes)):
		levelsFrame.grid_rowconfigure(i, weight = 1, uniform='row')

	synergiesFrame = Frame(rightFrame)
	synergiesFrame.grid(row=3, column=0, sticky="nsew")
	synergiesFrame.grid_columnconfigure(0, weight = 1, uniform='column')
	synergiesFrame.grid_columnconfigure(1, weight = 1, uniform='column')
	synergiesFrame.grid_columnconfigure(2, weight = 1, uniform='column')
	for i in range(8):
		synergiesFrame.grid_rowconfigure(i, weight = 1, uniform='row')

	champProfiles = {}
	for i in range(len(champNames)):
		profileRequest = requests.get("https://github.com/pedrohpf/Filter-Data-Test/blob/main/champProfiles/" + champNames[i] + ".png")
		champProfiles[champNames[i]] = ImageTk.PhotoImage(Image.open(BytesIO(profileRequest.content)).resize((40, 40)))

	levelBars = {}
	for i in range(len(teamAttributesTypes)):
		levelBar = displayLevelBar(levelsFrame, teamAttributesTypes, i)
		levelBars[teamAttributesTypes[i]] = levelBar

	synergyChampLabels = []
	for i in range(4): #selected champ | good vs | bad vs | good with
		synergyChampLabelsType = {}
		for champName in champNames:
			synergyChampLabelType = createChamp(synergiesFrame, champName, champProfiles[champName])
			if i==0: synergyChampLabelType.bind("<Button-1>", lambda event: clickChosenChamp(event, chosenChampNames, chosenChampLabels, synergyChampLabels, levelBars))
			synergyChampLabelsType[champName] = synergyChampLabelType
		synergyChampLabels.append(synergyChampLabelsType)

	chosenChampNames = []
	chosenChampLabels = {}
	for champName in champNames:
		chosenChampLabel = createChamp(teamFrame, champName, champProfiles[champName])
		chosenChampLabel.bind("<Button-1>", lambda event: clickChosenChamp(event, chosenChampNames, chosenChampLabels, synergyChampLabels, levelBars))
		chosenChampLabels[champName] = chosenChampLabel

	champLabels = {}
	for champName in champNames:
		champLabel = createChamp(champsFrame, champName, champProfiles[champName])
		champLabel.bind("<Button-1>", lambda event: clickChamp(event, chosenChampNames, chosenChampLabels, synergyChampLabels, levelBars))
		champLabels[champName] = champLabel

	displaySynergies(synergiesFrame)
	displaySearch(searchFrame, champLabels, champColumns)
	for i in range(len(filterTypes)):
		displayFilter(leftFrame, champLabels, champColumns, filterTypes, filterLevels, i)

	root.mainloop()

display("1000x600", 10)