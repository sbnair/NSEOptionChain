import requests
import json
import pandas
from bs4 import BeautifulSoup
# from datetime import datetime
# from datetime import date
# from pathlib import Path
# import getpass
# import time

class NSE:
    def __init__(self):
        '''
        __init__ of NSE class
        '''
        self.cookies = None
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7'
            }
        

        # self.indices = []
        # self.stocks = []
        # self.last_timestamp = None
        # self.last_underlyingValue = None
        # self.url_indices = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        # self.url_stocks = "https://www.nseindia.com/api/option-chain-equities?symbol=ACC"
        # self.url_market_status = "https://www.nseindia.com/api/marketStatus"
        # self.url_oc = "https://www.nseindia.com/option-chain"
        # self.dump_folder = 'dump'
        # self.market_status = None
                        
    def get_cookies(self): 
        '''
        get new cookies from nse website and set it to self.cookies
        '''
        try:
            with requests.Session() as s:
                request = s.get("https://www.nseindia.com/option-chain", headers=self.headers, timeout=(5, 27))                
                if request.cookies:
                    self.cookies = request.cookies
                    # for cookie in request.cookies:
                    #     if cookie.expires: # checking the expires flag
                    #         print(datetime.fromtimestamp(cookie.expires)) 
                
                    # print(min([datetime.fromtimestamp(cookie.expires) for cookie in request.cookies if cookie.expires]))                    
        except Exception as err:
            print("get_cookies: ", err)

    def check_cookie_expired(self): 
        '''
        returns true if self.cookies has expired and false if not
        '''
        try:
            count = len([cookie.is_expired() for cookie in self.cookies if cookie.is_expired()]) #returns total number of expired cookies
            return True if count > 0 else False            
        except Exception as err:
                    print("check_cookie_expired: ", err)

    def check_market_status(self): 
        '''
        returns true if market is open and false if market is closed
        '''
        try:
            if not self.cookies or self.check_cookie_expired():
                self.get_cookies()
            with requests.Session() as s:
                request = s.get("https://www.nseindia.com/api/marketStatus", headers=self.headers, timeout=(5,27), cookies=self.cookies).json()
                for item in request["marketState"]:
                    if item["index"] == "NIFTY 50":
                        if item["marketStatus"] == "Closed":
                            return False
                        else:
                            return True
        except Exception as err:
            print("check_market_status: ", err)

    def get_indices_contracts_names(self): 
        '''
        get contract names of all indices available in nse option chain and returns it as a list
        '''
        try:
            if not self.cookies or self.check_cookie_expired():
                self.get_cookies()
            with requests.Session() as s:                
                request = s.get("https://www.nseindia.com/option-chain", headers=self.headers, timeout=(5,27), cookies=self.cookies)
                soup = BeautifulSoup(request.text, "html.parser")
                indices = soup.find("select", id="equity_optionchain_select")
                indices =  indices.text.strip().split("\n")
                return indices
        except Exception as err:
            print("get_indices_contracts_names: ", err)

    def get_stocks_contracts_names(self): 
        '''
        get contract names of all stocks available in nse option chain and returns it as a list
        '''
        try:
            if not self.cookies or self.check_cookie_expired():
                self.get_cookies()
            with requests.Session() as s:                
                request = s.get("https://www.nseindia.com/api/master-quote", headers=self.headers, timeout=(5,27), cookies=self.cookies).json()
                return list(request)                                
        except Exception as err:
            print("get_stocks_contracts_names: ", err)

    def get_data(self, type='indices', symbol='NIFTY'): 
        '''
        fetches data for provided indices/stocks and symbol and returns json object
        sets self

        parameters:
            type => indices or equities 
            symbol=> valid symbol name in the type provided 
        '''
        try:
            if not self.cookies or self.check_cookie_expired():
                self.get_cookies()
            with requests.Session() as s:
                url = f'https://www.nseindia.com/api/option-chain-{type}?symbol={symbol}'
                request = s.get(url, headers=self.headers, timeout=(5, 27), cookies=self.cookies).json()
                return request
        except Exception as err:
            print("get_data: ", err)

    def save_data(self, data, path):
        '''
        takes json as input and saves it in provided path
        '''
        pass


if __name__ == "__main__":
    var = NSE()
    

    
    

    # self.last_timestamp = request["records"]["timestamp"]
    # self.last_underlyingValue = request["records"]["underlyingValue"]


    # with open(f'{self.dump_folder}\\{date.today()}.json', "w") as f:
                #     json.dump(request, f, indent=4, sort_keys=True)
                
                # print(self.last_underlyingValue, "\n", self.last_timestamp)

                # if not Path(f'{self.dump_folder}\\{date.today()}.json').exists():
                #     pass
                # else:
                    
                    
                

                # if expiry:
                #     ce_values = [data['CE'] for data in request['records']['data'] if "CE" in data and str(data['expiryDate']).lower() == str(expiry).lower()]
                #     pe_values = [data['PE'] for data in request['records']['data'] if "PE" in data and str(data['expiryDate']).lower() == str(expiry).lower()]
                # else:
                #     ce_values = [data['CE'] for data in request['filtered']['data'] if "CE" in data]
                #     pe_values = [data['PE'] for data in request['filtered']['data'] if "PE" in data]
                
               
                # response = s.get(self.url_indices, headers=self.headers, timeout=(5, 27), cookies = self.cookies).json()
                # for data in response['records']['expiryDates']:
                #     print(data)                