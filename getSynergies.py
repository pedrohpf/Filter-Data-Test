from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from champs import *
import re
import time

champNames = list(champs.keys())

chromeService = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=chromeService)

synergies = {}
for champName in champNames:
	goodvsUrl = "https://u.gg/lol/champions/" + champName + "/matchups?patch=12_4&rank=overall"
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
		goodvs[i] = goodvs[i].lower()

	goodwithUrl = "https://u.gg/lol/champions/" + champName + "/duos?patch=12_4&rank=overall"
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
		goodwith[i] = goodwith[i].lower()

	synergies[champName] = {"goodvs": goodvs, "goodwith": goodwith}

browser.close()
print(synergies)