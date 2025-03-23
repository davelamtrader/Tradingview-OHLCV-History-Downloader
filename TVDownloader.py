#!/usr/bin/env python
# coding: utf-8

# In[17]:



import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys


def downloadTV1seconddata(listofstocks):
    global driver
    chromedriverpath=r"C:\Users\deepa\Downloads\chromedriver_win32 (2)\chromedriver.exe"
    co = Options()
    co.add_argument("--log-level=3")    
    co.add_argument('headless')
    co.add_argument("--window-size=1920,1080")
    co.add_argument('--ignore-certificate-errors')
    co.add_argument('--allow-running-insecure-content')
    co.add_argument("--no-sandbox")
    co.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {"download.default_directory": r"\\DESKTOP-7EDG36U\homeshare-folder\TVDownloader"} 
    co.experimental_options["prefs"] = chrome_prefs
    driver = Chrome(executable_path=chromedriverpath,chrome_options=co)
    driver.get('https://in.tradingview.com/')
    driver.maximize_window()

    #############################Login###################################
    time.sleep(1)
    y=driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[2]/div[3]/button[1]')
    y.click()
    time.sleep(1)
    y=driver.find_elements_by_class_name('label-2IihgTnv')
    y[0].click()
    time.sleep(1)
    y=driver.find_elements_by_class_name('tv-social__title')
    y[2].click()
    time.sleep(1)
    y=driver.find_element_by_xpath('//*[contains(@id, "email-signin__user-name-input")]')
    y.send_keys('sleroy@videotron.ca')

    y=driver.find_element_by_xpath('//*[contains(@id,"email-signin__password-input")]')
    y.send_keys('azah1972')
    
    y.send_keys(Keys.TAB)
    time.sleep(1)
    y.send_keys(Keys.ENTER)
    time.sleep(1)
    print('Login done')
    ########################### open chart section########################
    y=driver.find_elements_by_class_name('tv-header__main-menu-item')
    y[0].click()

    ## this removes any popups 
    time.sleep(1)
    y=driver.find_elements_by_class_name('content-1UNGmyXO')
    if len(y)>0:
        for i in range (0,len(y)):
            y[i].click()
            time.sleep(1)
    print('chart opened')
    ##########chart time to 1 second   --y[0] is  for token  /y[1] is time frame  

    y = driver.find_elements_by_class_name('group-3uonVBsm')
    y[1].click()
    y = driver.find_elements_by_class_name('label-2IihgTnv')
    y[0].click()
    print('set to one second')
    for elem in listofstocks:

        #### #################this code will be changing the token you want to download for 

        time.sleep(1)
        y = driver.find_elements_by_class_name('group-3uonVBsm')
        y[0].click()
        time.sleep(1)

        y=driver.switch_to.active_element
        for i in range(1,11):
            y.send_keys(Keys.BACKSPACE)

        time.sleep(1)
        y.send_keys(elem)
        time.sleep(1)
        x=driver.find_elements_by_xpath('//*[contains(@class, "marketType")]')
        y=driver.find_elements_by_css_selector('[data-name=\"list-item-title\"]')
        z=driver.find_elements_by_xpath('//*[contains(@class, "exchangeName")]')


        for i in range(0,len(z)):
            if z[i].text=='NSE' and x[i].text=='index':
                y[i].click()
                break
        time.sleep(2)
        print('token changed')
        ## #################use goto button to move to desired start date and time        
        y=driver.find_element_by_css_selector('[data-name="go-to-date"]')
        y.click()
        time.sleep(1)
        y=driver.switch_to.active_element

        time.sleep(1)
        y.send_keys(Keys.TAB)

        y=driver.switch_to.active_element
        for i in range(1,6):
            y.send_keys(Keys.BACKSPACE)
        y.send_keys("03:45")
        y.send_keys(Keys.ENTER)
        time.sleep(1)
        y=driver.find_elements_by_class_name('content-1UNGmyXO')
        y[1].click()
        time.sleep(5)
        print('date time set')
        ################### download the report 

        y=driver.find_elements_by_class_name('buttonWrap-2WfzAPA-')
        y[0].click()
        time.sleep(1)
        y = driver.find_elements_by_class_name('label-2IihgTnv')
        y[4].click()
        time.sleep(1)
        y=driver.find_elements_by_css_selector('[aria-labelledby=\"time-format-select\"]')
        y[0].click()
        time.sleep(1)
        y=driver.find_elements_by_id('time-format-iso')
        y[0].click()
        time.sleep(1)
        y=driver.find_elements_by_css_selector('[name=\"submit\"]')
        y[0].click()
        time.sleep(5)
        print('downloaded')
        
downloadTV1seconddata(['BANKNIFTY','NIFTY'])
print('quitting driver')
driver.quit()


# In[13]:


y=driver.find_element_by_css_selector('[data-name="go-to-date"]')


# In[11]:


driver.save_screenshot('tes1t.png')


# In[10]:


y.click()


# In[ ]:




