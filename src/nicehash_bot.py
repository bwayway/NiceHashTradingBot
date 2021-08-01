#Selenium Library (used for webpage navigation)
import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
#JSON library used for reading JSON files
import json
#Time library
import time
import datetime
from datetime import datetime
#Regex library
import re
#logging libraries
import logging
import traceback
#Exception Handling library
import sys
import os
#import custom email class
from email_setup import email

email_handler = None

#Reads the config json file and returns a dictionary
def read_config():

    #Open the config file
    f = open("./src/config/config.json")

    data = json.load(f)

    f.close()

    return data







#Gets the location and name of the log file
def setup_logging(config_data):

    log_folder = config_data['Logging'][0]['LogFileLocation']

    log_file_name = f"log_{datetime.now().strftime('%Y_%m_%d_%I%M%S')}.txt"

    full_log_name = os.path.join(log_folder,log_file_name)

    logging.basicConfig(filename=full_log_name, level=logging.INFO, filemode='w')






#Gets the appropriate driver for the browser. Firefox, Edge, Chrome available
def get_driver(config_data):


    settings = config_data["Settings"][0]

    driver_type = settings['Driver']


    #Assign the web driver based on what's in the Settings config.\
    #string.find() returns -1 if the substring is not found in the original string
    if driver_type.lower().find("fox") > -1:
        driver = webdriver.Firefox(executable_path='./drivers/geckodriver.exe')
    elif driver_type.lower().find("chrome") > -1:
        driver = webdriver.Chrome(executable_path='./drivers/chromedriver.exe')
    elif driver_type.lower().find("edge") > -1:
        driver = webdriver.Edge(executable_path='./drivers/msedgedriver.exe')


    #Open the webpage
    driver.get('https://www.nicehash.com/my/login')

    #Maximize the window size to ensure no elements are hidden
    driver.maximize_window()

    #Stop program from running for 3 seconds to let webpage load
    time.sleep(3)

    return driver




#Logs out of Nicehash
def log_out(driver):
    avatar_icon = driver.find_element_by_class_name("avatar")
    avatar_icon.click()
    logout_btn = driver.find_element_by_class_name('fa.fa-sign-out-alt')
    logout_btn.click()







#Write to the log and email
def write_to_log_and_email(message,error_level):
    if error_level == 1:
        logging.info(message)
    elif error_level == 2:
        logging.warning(message)
    elif error_level == 3:
        logging.error(message)
    elif error_level == 4:
        logging.critical(message)
    global email_handler
    email_handler.write_email_message(message)








#Calculate the percentage of BTC you want to exchange 
def calculate_token_amounts(token_dictionary,total_btc):
    #Dictionary of each token and the total amount of BTC of each to trade
    tokens_to_transfer = {}
    total_percentage = 0

    for token in token_dictionary[0]:
        if token_dictionary[0][token] > 0:
            amount = total_btc * (token_dictionary[0][token] * .01)
            if(amount >= .0001):
                tokens_to_transfer[token] = amount
            else:
                write_to_log_and_email(f'Could not exchange BTC for {token}. Nicehash requires a minimum of .0001 BTC to be traded. Increase {token} percentage, or perform trade manually.',2)
                write_to_log_and_email(f'Trying to trade {"{:f}".format(amount)} BTC ({token_dictionary[0][token]}%)',2 )
            total_percentage += token_dictionary[0][token]

    if(total_percentage > 100):
        raise ValueError("Total token exchange percentage cannot be above 100%. Please change exchange percentages")
    if (total_percentage <= 0):
        raise ValueError("Total token exchange percentage cannot be less than or equal to zero. Please change exchange percentages")   

    return tokens_to_transfer









#Navigates to each token trading page and trades with the amounts (based off percentage from config file) per token
def exchange_crypto(token_to_exchange_dictionary, driver):

    write_to_log_and_email('-------------------Trades----------------------',1 )

    for token in token_to_exchange_dictionary:

        #The amount of BTC to exchange
        amount_to_exchange = token_to_exchange_dictionary[token]

        #Click the "Show More" button to expand the entire list of tokens/coins
        show_more_button = driver.find_element_by_class_name('btn.primary.normal.outline')
        show_more_button.click()

        time.sleep(10)
        
        token_market_page = driver.find_element_by_xpath(f'//a[@href="/my/tradeview/{token}BTC"]')

        time.sleep(3)

        #Since the button is hidden until hovered over, we need to use the ActionChains library to hover over (perform()) and then click
        hover = ActionChains(driver).move_to_element(token_market_page)
        hover.click().perform()
        time.sleep(3)

        #Navigate the Exchange page
        order_form = driver.find_element_by_class_name("order-form")

        #Get to the "Market" tab of the order form
        market_tab = order_form.find_element_by_class_name("tab")
        market_tab.click()

        #Enter amount to trade
        btc_form = order_form.find_elements_by_class_name("form-control")
        btc_form[0].send_keys('{:f}'.format(amount_to_exchange))

        return_amount = btc_form[1].get_attribute('value')
        
        write_to_log_and_email(f"Exchanging {amount_to_exchange} BTC -> {return_amount} {token}", 1)

        #Click the "Place Buy Order" button
        place_order_button = order_form.find_element_by_class_name('place-order')
        place_order_button.click()

        time.sleep(3)

        try:
        #Click the acknowledgement checkbox, if present
            confirm_order_checkbox = driver.find_elements_by_class_name('mb16.checkbox')
            if len(confirm_order_checkbox) > 0:
                confirm_order_checkbox[0].find_element_by_tag_name('label').click()

            #Confirm and click the "Place Order" button
            confirm_order_btn = driver.find_element_by_class_name('btn.primary.success.normal.fluid')
            confirm_order_btn.click()

            time.sleep(3)

            errors = driver.find_elements_by_class_name('alert.alert-error')

            if(len(errors) > 0):
                write_to_log_and_email(errors[0].text, 4)
                raise Exception ("Make sure to check if you're using a VPN.")


        except:
            write_to_log_and_email("There was an issue with placing your order...", 3)
            write_to_log_and_email(traceback.format_exc(), 3)
            raise
        
        write_to_log_and_email('--------------------------------------------------',1 )
        #navigate back to the "Market" page
        driver.find_element_by_xpath('//a[@href="/my/markets"]').click()

        time.sleep(3)














#Navigates the nicehash website to automatically trade crypto
def start_process(config_data,driver):

    setup_logging(config_data)


    #Gets the Login Info from and percentage of token contributions from the config data
    login_info = config_data["Login"]
    token_percentages = config_data["Token Exchange Percentages"]
    settings = config_data["Settings"]

    #find and fill the username textbox
    email_box = driver.find_element_by_name("email")
    email_box.send_keys(login_info[0]['username'])

    #find and fill the password textbox
    password_box = driver.find_element_by_name("password")
    password_box.send_keys(login_info[0]['password'])

    write_to_log_and_email(f"Attempting to login with email: {login_info[0]['username']}...",1 )

    try:
        e = ''
        #Press the login button
        login_btn = driver.find_element_by_tag_name("button")
        login_btn.click()

        #check whether or not the login has invalid info
        if len(driver.find_elements_by_class_name("input-error-msg")) > 0:
            e = 'Login unsuccessful. Invalid email format. Please use a valid email address.'
            raise ValueError(e)
        if len(driver.find_elements_by_class_name("alert")) > 0:
            e = "Login unsuccessful. Invalid email or password"
            raise ValueError(e)
    except:
        write_to_log_and_email(e,3 )
        write_to_log_and_email(traceback.format_exc(),3)
        return 

    write_to_log_and_email("Login successful!", 1)
    #Let dashboard load
    time.sleep(3)


    #Get the total assets in BTC. note 'pt8' is the first class in the element (an HTML tag can use more than one class. They are seperated by spaces)
    #Use regex to get the decimal from the text
    total_btc_text = re.findall("\d+\.\d+",driver.find_element_by_class_name('text-medium').text)

    


    #Setting Country
    #For some reason, the country in the users settings is not updated until you manually save it. This is to fix that issue
    
    try:
        e = ''
        avatar_icon = driver.find_element_by_class_name("avatar")
        avatar_icon.click()

        

        my_settings_btn = driver.find_element_by_xpath('//a[@href="/my/settings/"]')
        my_settings_btn.click()

        #let the settings page load
        time.sleep(3)

        #there are multiple uses of the css class "selectbox" on this page. The country selectbox is the 2nd one so we parse all of them into a dictionary
        select_box_collection = driver.find_elements_by_class_name('selectbox')
        select_box_collection[1].click()

        #Within the country searchbox, we need to get the nested input form
        country_search_box = select_box_collection[1].find_elements_by_class_name('search')
        country_search_box = country_search_box[0].find_element_by_tag_name('input')
        country_search_box.send_keys(settings[0]['Country'])
        
        write_to_log_and_email(f'Setting country to: {settings[0]["Country"]}',1 )

        #Click the country from the drop down that appears
        confirm_country = select_box_collection[1].find_element_by_class_name("option.selected")
        confirm_country.click()



        #Click the "save changes" button
        save_changes_btn = driver.find_elements_by_class_name('col-sm-12')
        save_changes_btn = save_changes_btn[0].find_element_by_class_name('btn.primary.normal')
        save_changes_btn.click()

        write_to_log_and_email('Country saved successfully \n\n',1 )
    except:
        e = 'There was an issue setting country settings...'
        write_to_log_and_email(e,3 )
        write_to_log_and_email(traceback.format_exc(), 3)

    #Load the "Markets" Page
    markets_btn = driver.find_element_by_xpath('//a[@href="/my/markets"]')
    markets_btn.click()

    #Let the "Markets" page load
    time.sleep(3)

    #Count the tokens to exchange
    write_to_log_and_email(f'Total BTC available to trade: {total_btc_text[0]} \n',1 )

    total_btc = float(total_btc_text[0])
    tokens_to_exchange = calculate_token_amounts(token_percentages,total_btc)


    #loops through each tokens to exchange 
    exchange_crypto(tokens_to_exchange, driver)


    #Get the total in your wallet(s)
    wallet_btn = driver.find_element_by_xpath('//a[@href="/my/wallets/"]')
    wallet_btn.click()

    time.sleep(10)

    #switch to USD 
    usd_btn = driver.find_element_by_class_name('fa.fa-sort')
    usd_btn.click()

    total_balance = driver.find_element_by_class_name('pt8.pb16.balance.pointer').text


    write_to_log_and_email('-------------------Wallets-------------------',1 )
    wallets = driver.find_elements_by_css_selector('div.wallets')
    yourWallets = wallets[0].find_elements_by_class_name('wallet-row.pointer')
    for wallet in yourWallets:
        wallet_amount_name = wallet.find_element_by_class_name("currency").text
        wallet_amount_coin = wallet.find_element_by_class_name("col-available").text
        wallet_amount_usd = wallet.find_element_by_class_name('col-total').find_element_by_class_name('mt4.fs12.text-muted.fiat').text
            
        write_to_log_and_email(f'{wallet_amount_name}: {wallet_amount_coin} ({wallet_amount_usd})',1 )
    write_to_log_and_email(f'Total wallet: {total_balance}',1 )
    write_to_log_and_email('-------------------------------------------------', 1)


    #sign out
    log_out(driver)

    time.sleep(3)

    print("stop")












#Main Function
if __name__ == "__main__":

    #read Login info from config.json and return the dictionary
    try:
        config_data = read_config()
    except:
        e = traceback.format_exc()
        print(f'There was an error reading the config file: ')
        print(e)

    #Setup Email messages
    email_handler = email(config_data)

    #Get the appropriate driver
    driver = get_driver(config_data)

    #start
    try:
        start_process(config_data,driver)
    except:
        write_to_log_and_email("There was an error when running...",3 )
        write_to_log_and_email(traceback.format_exc(), 3 )
    finally:
        email_handler.send_email()
        log_out(driver)





