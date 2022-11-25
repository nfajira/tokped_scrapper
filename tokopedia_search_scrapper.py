import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime

def search_tokped(keyword) :
	driver = webdriver.Remote(command_executor=url,desired_capabilities={})
	driver.close()   # this prevents the dummy browser
	driver.session_id = session_id
	driver.get("https://www.tokopedia.com/search?st=product&q="+keyword)
	SCROLL_PAUSE_TIME = 0.1
	height=1080
	time.sleep(1)
	while True:
		# Scroll down to bottom
		last_height = driver.execute_script("return document.body.scrollHeight")
		driver.execute_script("window.scrollTo(0, "+str(height)+")")
		height=height+1080
		new_height = driver.execute_script("return document.body.scrollHeight")
		# Wait to load page
		time.sleep(SCROLL_PAUSE_TIME)
		if new_height==last_height:
			break
		last_height=new_height
	html = driver.page_source
	
	return html

def search_tokped_2(page, keyword) :
	driver = webdriver.Remote(command_executor=url,desired_capabilities={})
	driver.close()   # this prevents the dummy browser
	driver.session_id = session_id
	driver.get('https://www.tokopedia.com/search?page='+str(page)+'&q='+keyword+'&st=product')
	SCROLL_PAUSE_TIME = 0.1
	height=1080
	time.sleep(1)
	while True:
		# Scroll down to bottom
		last_height = driver.execute_script("return document.body.scrollHeight")
		driver.execute_script("window.scrollTo(0, "+str(height)+")")
		height=height+1080
		new_height = driver.execute_script("return document.body.scrollHeight")
		# Wait to load page
		time.sleep(SCROLL_PAUSE_TIME)
		if new_height==last_height:
			break
		last_height=new_height
	html = driver.page_source
	
	return html

def get_result_to_dic ():
	None


def check_result (keyword, pages):
	n=1
	toko_result = {}
	search_array =[]
	toko_array = []
	final_result = {}
	previous_word=""
	input_word = len(keyword)
	input_word_count = 1
	for word in keyword:
		
		html_word = word.replace(" ", "%20")
		for page_count in range(pages) :
			if page_count + 1 == 1:
				html = search_tokped(html_word)
			else:
				html = search_tokped_2((page_count+1),html_word)

			soup = BeautifulSoup(html,"html.parser")
			search = soup.find_all("a", class_="pcv3__info-content", href=True)
			print(len(search))

			for a in search :
				if a['href'].startswith('https://www.tokopedia.com/'):
					toko = re.findall('https:\/\/www.tokopedia.com\/.*(?=\/)', a['href'])
					price = re.findall('Rp.*(?=<)',str(a.find("div", class_="prd_link-product-price")))
					if len(price)==0:
						price = 0
						
					else:
						price = price[0]
						price = price.replace('Rp','')
						price = price.replace ('.','')
					rating = re.findall('Terjual.*\+(?=<)',str(a.find("div", class_="css-q9wnub")))
					if len(rating)==0:
						rating=0
					else :
						rating=rating[0]
						rating = rating.replace('Terjual ','')
						rating = rating.replace(' rb','000')
						rating = rating.replace('+', '')
					item_title = a['title']
					item_url = a['href']
					if len(keyword) > 1:
						if n ==1 :
							if toko[0] not in toko_result.keys():
								toko_result[toko[0]+'_'+word] = [word,item_title,price,rating,item_url]
							search_array.append([toko[0],word,item_title,price,rating,item_url])
							
						else:
							if toko[0]+'_'+previous_word in toko_result.keys():
								toko_result[toko[0]+'_'+word] = [word,item_title,price,rating,item_url]
								search_array.append([toko[0],word,item_title,price,rating,item_url])
								if input_word_count == input_word :
									final_result[toko[0]] = [word,item_title,price,rating,item_url]	
					else :
						search_array.append([toko[0],word,item_title,price,rating,item_url])
						final_result[toko[0]] = [word,item_title,price,rating,item_url]	
							
		n=n+1
		previous_word = word
		input_word_count = input_word_count + 1
	for key in final_result:
		for result in search_array:
			if result[0] == key:
				toko_array.append(result)
	return toko_array

start_time = datetime.datetime.now()

options = Options()
options.headless = False
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

url = driver.command_executor._url      
session_id = driver.session_id            

##Keyword Input
keyword=["xiaomi sound bar"]
pages = 30

tokos = check_result(keyword, pages)

# for toko in tokos:
# 	found_2 = check_result(search_tokped_2(toko, keyword2))
# 	if found_2 is not None :
# 		if len(found_2) != 0:
# 			print(toko,"is having product for keywords: ", keyword1, ", ", keyword2)
# 		else:
# 			print(toko, " is not having both product keywords")



df = pd.DataFrame(tokos) # convert dict to dataframe

df.to_csv('tokped.csv') # write dataframe to file

end_time = datetime.datetime.now()

duration = end_time - start_time

print ("Duration: ", duration )
