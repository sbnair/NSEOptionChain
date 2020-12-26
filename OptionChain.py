import requests
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

# pd.options.display.float_format = "{:,.2f}".format
# from matplotlib import pyplot as plt
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
        # self.request = None
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
                        
    def set_cookies(self): 
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
            print("set_cookies: ", err)

    def has_cookie_expired(self): 
        '''
        returns true if self.cookies has expired and false if not
        '''
        try:
            count = len([cookie.is_expired() for cookie in self.cookies if cookie.is_expired()]) #returns total number of expired cookies
            return True if count > 0 else False            
        except Exception as err:
                    print("has_cookie_expired: ", err)

    def is_market_open(self): 
        '''
        returns true if market is open and false if market is closed
        '''
        try:
            if not self.cookies or self.has_cookie_expired():
                self.set_cookies()
            with requests.Session() as s:
                request = s.get("https://www.nseindia.com/api/marketStatus", headers=self.headers, timeout=(5,27), cookies=self.cookies).json()
                for item in request["marketState"]:
                    if item["index"] == "NIFTY 50":
                        if item["marketStatus"] == "Open":
                            return True
                        else:
                            return False
        except Exception as err:
            print("is_market_open: ", err)

    def get_indices_contracts_names(self): 
        '''
        get contract names of all indices available in nse option chain and returns it as a list
        '''
        try:
            if not self.cookies or self.has_cookie_expired():
                self.set_cookies()
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
        get contract names of all equities available in nse option chain and returns it as a list
        '''
        try:
            if not self.cookies or self.has_cookie_expired():
                self.set_cookies()
            with requests.Session() as s:                
                request = s.get("https://www.nseindia.com/api/master-quote", headers=self.headers, timeout=(5,27), cookies=self.cookies).json()
                return list(request)                                
        except Exception as err:
            print("get_stocks_contracts_names: ", err)

    def get_nse_data(self, type='indices', symbol='NIFTY'): 
        '''
        fetches data for provided indices/equities and symbol and returns sets json object to self.request

        parameters:
            type => indices/equities 
            symbol=> valid symbol name in the type provided 
        '''
        try:
            if not self.cookies or self.has_cookie_expired():
                self.set_cookies()
            with requests.Session() as s:
                url = f'https://www.nseindia.com/api/option-chain-{type}?symbol={symbol}'
                request = s.get(url, headers=self.headers, timeout=(5, 27), cookies=self.cookies).json()
                # self.request = request
                return request
        except Exception as err:
            print("get_nse_data: ", err)

    def get_oc_data(self, type='indices', symbol='NIFTY', expiry=None):
        '''
        fetches data for provided expiry date from nse website using get_nse_data function and returns option chain data 

        return values:
            df => returns oc data in pandas dataframe
            pcr_oi => returns pcr based on oi in float rounded to 2
            pcr_vol => returns pcr based on volume in float rounded to 2
            maxpain => returns maxpain value in float
            timestamp => returns timestamp as str
            underlyingValue => returns underlying value in float

        '''
        try:
            request = self.get_nse_data(type=type, symbol=symbol)
            if expiry:
                ce_data = [data['CE'] for data in request['records']['data'] if "CE" in data and str(data['expiryDate']).lower() == str(expiry).lower()]
                pe_data = [data['PE'] for data in request['records']['data'] if "PE" in data and str(data['expiryDate']).lower() == str(expiry).lower()]
            else:
                ce_data = [data['CE'] for data in request['filtered']['data'] if "CE" in data]
                pe_data = [data['PE'] for data in request['filtered']['data'] if "PE" in data]

            ce_df = pd.DataFrame(ce_data)
            ce_df = ce_df.drop(['expiryDate', 'underlying', 'identifier', 'bidQty', 'bidprice', 'askQty', 'askPrice', 'changeinOpenInterest', 'change', 'underlyingValue'], axis = 1) 
            ce_df = ce_df[['totalBuyQuantity', 'totalSellQuantity', 'totalTradedVolume', 'pchangeinOpenInterest', 'openInterest', 'lastPrice', 'pChange', 'impliedVolatility', 'strikePrice']]
            ce_df = ce_df.rename(columns={'totalBuyQuantity':'BuyQuantity', 'totalSellQuantity':'SellQuantity', 'totalTradedVolume':'TotalVolume', 'pchangeinOpenInterest':'poi', 'openInterest':'oi', 'lastPrice':'ltp', 'pChange':'pltp', 'impliedVolatility':'iv'})

            pe_df = pd.DataFrame(pe_data)
            pe_df= pe_df.drop(['expiryDate', 'underlying', 'identifier', 'bidQty', 'bidprice', 'askQty', 'askPrice', 'underlyingValue', 'changeinOpenInterest', 'change'], axis = 1)
            pe_df = pe_df[['strikePrice', 'impliedVolatility', 'pChange', 'lastPrice', 'openInterest', 'pchangeinOpenInterest', 'totalTradedVolume', 'totalSellQuantity', 'totalBuyQuantity']]            
            pe_df = pe_df.rename(columns={'totalBuyQuantity':'BuyQuantity', 'totalSellQuantity':'SellQuantity', 'totalTradedVolume':'TotalVolume', 'pchangeinOpenInterest':'poi', 'openInterest':'oi', 'lastPrice':'ltp', 'pChange':'pltp', 'impliedVolatility':'iv'})

            df = pd.merge(ce_df, pe_df, on='strikePrice', suffixes=('_ce', '_pe'), how='outer', sort=True).fillna(0)
            df = df.astype({'BuyQuantity_ce':'uint64', 'SellQuantity_ce':'uint64', 'TotalVolume_ce':'uint64', 'oi_ce':'uint64', 'BuyQuantity_pe':'uint64', 'SellQuantity_pe':'uint64', 'TotalVolume_pe':'uint64', 'oi_pe':'uint64'})
            df = df.astype({'poi_ce':'float', 'pltp_ce':'float', 'iv_ce':'float', 'poi_pe':'float', 'pltp_pe':'float', 'iv_pe':'float'}).round({'poi_ce':1, 'pltp_ce':1, 'iv_ce':1, 'poi_pe':1, 'pltp_pe':1, 'iv_pe':1})
            df = df.astype({'ltp_ce':'float', 'ltp_pe':'float', 'strikePrice':'float'})
            
            def cumm_ce(expiryPrice):
                sum = 0
                for index in df.index:
                    if (expiryPrice - df['strikePrice'][index]) >= 0:
                        sum = sum + (expiryPrice - df['strikePrice'][index]) * df['oi_ce'][index]  
                return sum

            def cumm_pe(expiryPrice):
                sum = 0
                for index in df.index:
                    if (df['strikePrice'][index] - expiryPrice) >= 0:
                        sum = sum + (df['strikePrice'][index] - expiryPrice) * df['oi_pe'][index]  
                return sum
                                      
            df['cumm_ce'] = df['strikePrice'].apply(lambda row: cumm_ce(row))
            df['cumm_pe'] = df['strikePrice'].apply(lambda row: cumm_pe(row))
            df['cumm'] = df['cumm_ce'] + df['cumm_pe']  # df['cumm'] = df.apply(lambda row: row['cumm_ce'] + row['cumm_pe'], axis = 1)
            df = df.drop(['cumm_ce', 'cumm_pe'], axis=1)
            maxpain = df.loc[df['cumm'].idxmin()]['strikePrice']
            
            
            pcr_oi = df['oi_pe'].sum()/df['oi_ce'].sum()
            pcr_vol = df['TotalVolume_pe'].sum()/df['TotalVolume_ce'].sum()

            timestamp = request["records"]["timestamp"]
            underlyingValue = request["records"]["underlyingValue"]

            return df, round(pcr_oi, 2), round(pcr_vol, 2), maxpain, timestamp, underlyingValue
        except Exception as err:
            print( "get_oc_data: ", err)

    def save_data(self, data, path):
        '''
        takes json as input and saves it in provided path
        '''
        pass

    def write_to_html_file(self, df, title='', filename='out.html'):
        '''
        Write an entire dataframe to an HTML file with nice formatting.
        '''

        result = '''
        <html>
        <head>
        <style>

            h2 {
                text-align: center;
                font color: Georgia;
                color: #021897;
                font-size: 200%;
                text-decoration: underline;
                
            }
            table { 
                margin-left: auto;
                margin-right: auto;
            }
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            th, td {
                padding: 5px;
                text-align: center;
                
            }
            th {
            font-family: "Times New Roman", Times, serif;
                font-size: 110%;
            }
            td {
            font-family: "Times New Roman", Times, serif;
                font-size: 90%;
            }
            
            tr:nth-child(even) {
        background-color: #C2CAF6;
        }
        tr:nth-child(odd) {
        background-color: #fff;
        }
            th {
        background-color: #021897;
        color: white;
        
        }
        
            table tbody tr:hover {
                background-color: #82A2EF;
                font-size: 120%;
                color: white;
            }
            .wide {
                width: 90%; 
            }
        
        </style>
        </head>
        <body>
            '''
        result += '<h2> %s </h2>\n' % title
        result += df.to_html(classes='wide', escape=False, index=0)
        result += '''
        </body>
        </html>
        '''
        with open(filename, 'w') as f:
            f.write(result)


if __name__ == "__main__":
    nse = NSE()
    df, pcr_oi, pcr_vol, maxpain, timestamp, underlyingValue = nse.get_oc_data(expiry='31-Dec-2020') 
    
    print(df.head())
    print(pcr_oi, pcr_vol, maxpain, sep=' - ')
    print(type(underlyingValue))
 
    
    # df = df.style.set_precision(2)
#     df.style.format({
#     'A': '{:,.1f}'.format,
#     'B': '{:,.3f}'.format,
# })

    df_style = df.style.bar(subset=['oi_ce'], color='red')
    df_style = df_style.bar(subset=['cumm'], color='grey')
    html = df_style.set_precision(2).hide_index().render()  
    # html = html.set_properties( **{'width': '200px', 'background-color': 'yellow', 'color': 'black', 'border-color': 'black'}).render() 
    
    with open("index.html","w") as f:
        f.write(html)


    # with open('request.txt', 'w')as f:
    #     json.dump(request, f, indent=4, sort_keys=True)

    
    # df = df.loc[df['strikePrice'] > 13750]
    # # print(df)
    
   # with open('nifty.json', "w") as f:
    #     json.dump(request, f, indent=4, sort_keys=True)
                
                

                # if not Path(f'{self.dump_folder}\\{date.today()}.json').exists():
                #     pass
                # else:
                

# with open("test1.html", 'w') as f:
            #     f.write(df.to_html(index=False))