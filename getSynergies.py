from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import re
import time

gitMainPath = "https://raw.githubusercontent.com/pedrohpf/Filter-Data-Test/main/"
data = requests.get(gitMainPath + "db.json").json()
champs = data["champs"]

patch = "12_4"

chromeService = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=chromeService)

champNames = list(champs.keys())
synergies = {}
for champName in champNames:
	if champName == "renataglasc":
		champName = "renata"
		
	goodvsUrl = "https://u.gg/lol/champions/" + champName + "/matchups?patch=" + patch + "&rank=overall"
	browser.get(goodvsUrl)
	time.sleep(2) #Lazy way of waiting for full load
	goodvsHtml = browser.page_source
	goodvs = re.findall("(?<=\<strong\>)" + "[^\<]+" + "(?=\<\/strong\>)", goodvsHtml)
	for i in range(len(goodvs)):
		goodvs[i] = goodvs[i].replace(" ", "")
		goodvs[i] = goodvs[i].replace("'", "")
		goodvs[i] = goodvs[i].replace(".", "")
		goodvs[i] = goodvs[i].replace("&amp;", "")
		goodvs[i] = goodvs[i].replace("Willump", "")
		goodvs[i] = goodvs[i].replace("Renata", "RenataGlasc")
		goodvs[i] = goodvs[i].replace("RenataGlascGlasc", "RenataGlasc")
		goodvs[i] = goodvs[i].lower()

	goodwithUrl = "https://u.gg/lol/champions/" + champName + "/duos?patch=" + patch + "&rank=overall"
	browser.get(goodwithUrl)
	time.sleep(2)
	goodwithHtml = browser.page_source
	goodwith = re.findall("(?<=\<strong class=\"champion-name\"\>)" + "[^\<]+" + "(?=\<\/strong\>)", goodwithHtml)
	for i in range(len(goodwith)):
		goodwith[i] = goodwith[i].replace(" ", "")
		goodwith[i] = goodwith[i].replace("'", "")
		goodwith[i] = goodwith[i].replace(".", "")
		goodwith[i] = goodwith[i].replace("&amp;", "")
		goodwith[i] = goodwith[i].replace("Willump", "")
		goodwith[i] = goodwith[i].replace("Renata", "RenataGlasc")
		goodwith[i] = goodwith[i].replace("RenataGlascGlasc", "RenataGlasc")
		goodwith[i] = goodwith[i].lower()

	if champName == "renata":
		champName = "renataglasc"
	synergies[champName] = {"goodvs": goodvs, "goodwith": goodwith}

browser.close()
print(synergies)
