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
                expiry = request['filtered']['data'][0]['expiryDate']
                ce_data = [data['CE'] for data in request['filtered']['data'] if "CE" in data]
                pe_data = [data['PE'] for data in request['filtered']['data'] if "PE" in data]

            ce_df = pd.DataFrame(ce_data)
            ce_df = ce_df.drop(['expiryDate', 'underlying', 'identifier', 'bidQty', 'bidprice', 'askQty', 'askPrice', 'changeinOpenInterest', 'change', 'underlyingValue'], axis = 1) 
            ce_df = ce_df[['totalBuyQuantity', 'totalSellQuantity', 'totalTradedVolume', 'openInterest', 'pchangeinOpenInterest', 'lastPrice', 'pChange', 'impliedVolatility', 'strikePrice']]
            ce_df = ce_df.rename(columns={'totalBuyQuantity':'BuyQ', 'totalSellQuantity':'SellQ', 'totalTradedVolume':'TotalVol', 'pchangeinOpenInterest':'pOI', 'openInterest':'OI', 'lastPrice':'LTP', 'pChange':'pLTP', 'impliedVolatility':'IV'})

            pe_df = pd.DataFrame(pe_data)
            pe_df= pe_df.drop(['expiryDate', 'underlying', 'identifier', 'bidQty', 'bidprice', 'askQty', 'askPrice', 'underlyingValue', 'changeinOpenInterest', 'change'], axis = 1)
            pe_df = pe_df[['strikePrice', 'impliedVolatility', 'pChange', 'lastPrice', 'pchangeinOpenInterest', 'openInterest', 'totalTradedVolume', 'totalBuyQuantity', 'totalSellQuantity']]            
            pe_df = pe_df.rename(columns={'totalBuyQuantity':'BuyQ', 'totalSellQuantity':'SellQ', 'totalTradedVolume':'TotalVol', 'pchangeinOpenInterest':'pOI', 'openInterest':'OI', 'lastPrice':'LTP', 'pChange':'pLTP', 'impliedVolatility':'IV'})

            df = pd.merge(ce_df, pe_df, on='strikePrice', suffixes=('_c', '_p'), how='outer', sort=True).fillna(0)
            df = df.astype({'BuyQ_c':'uint64', 'SellQ_c':'uint64', 'TotalVol_c':'uint64', 'OI_c':'uint64', 'BuyQ_p':'uint64', 'SellQ_p':'uint64', 'TotalVol_p':'uint64', 'OI_p':'uint64'})
            df = df.astype({'pOI_c':'float', 'pLTP_c':'float', 'IV_c':'float', 'pOI_p':'float', 'pLTP_p':'float', 'IV_p':'float'}).round({'pOI_c':1, 'pLTP_c':1, 'IV_c':1, 'pOI_p':1, 'pLTP_p':1, 'IV_p':1})
            df = df.astype({'LTP_c':'float', 'LTP_p':'float', 'strikePrice':'float'})
            
            def MaxPain_c(expiryPrice):
                sum = 0
                for index in df.index:
                    if (expiryPrice - df['strikePrice'][index]) >= 0:
                        sum = sum + (expiryPrice - df['strikePrice'][index]) * df['OI_c'][index]  
                return sum

            def MaxPain_p(expiryPrice):
                sum = 0
                for index in df.index:
                    if (df['strikePrice'][index] - expiryPrice) >= 0:
                        sum = sum + (df['strikePrice'][index] - expiryPrice) * df['OI_p'][index]  
                return sum
                                      
            df['MaxPain_c'] = df['strikePrice'].apply(lambda row: MaxPain_c(row))
            df['MaxPain_p'] = df['strikePrice'].apply(lambda row: MaxPain_p(row))
            df['MaxPain'] = df['MaxPain_c'] + df['MaxPain_p']  # df['MaxPain'] = df.apply(lambda row: row['MaxPain_c'] + row['MaxPain_p'], axis = 1)
            # df = df.drop(['MaxPain_c', 'MaxPain_p'], axis=1)
            maxpain = df.loc[df['MaxPain'].idxmin()]['strikePrice']
                        
            pcr_oi = df['OI_p'].sum()/df['OI_c'].sum()
            pcr_vol = df['TotalVol_p'].sum()/df['TotalVol_c'].sum()

            timestamp = request["records"]["timestamp"]
            underlyingValue = request["records"]["underlyingValue"]

            return df, round(pcr_oi, 2), round(pcr_vol, 2), maxpain, timestamp, underlyingValue, expiry
        except Exception as err:
            print( "get_oc_data: ", err)

    def get_output(self, type='indices', symbol='NIFTY', expiry=None):
        df, pcr_oi, pcr_vol, maxpain, timestamp, underlyingValue, exp = self.get_oc_data(type=type, symbol=symbol, expiry=expiry)   

        def color_pcolumn(val):            
            """
            Takes a scalar and returns a string with
            the css property `'color: red'` for negative
            strings, black otherwise.
            """
            color = 'red' if val < 0 else 'green'
            return 'color: %s' % color

        # def color_background(val):
        #     return 'background-color':'yellow'
        
        def highlight_min(data, color='#df66e8'):
            '''
            highlight the minimum in a Series or DataFrame
            '''
            attr = 'background-color: {}'.format(color)
            if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
                is_min = data == data.min()
                return [attr if v else '' for v in is_min]
            else:  # from .apply(axis=None)
                is_min = data == data.min().min()
                return pd.DataFrame(np.where(is_min, attr, ''),
                                    index=data.index, columns=data.columns)

        atm_index = df['strikePrice'].sub(underlyingValue).abs().idxmin()
        
        df = df.iloc[atm_index-15:atm_index+15,:]

        df = df.drop(['MaxPain_c', 'MaxPain_p', 'IV_c', 'IV_p'], axis=1)
        df_style = df.style    

        # def hover(hover_color="blue"):
        #     return dict(selector="tr:hover",
        #                 props=[("background-color", "%s" % hover_color)])

        styles = [
            # hover(),
            dict(selector="th", props=[("font-size", "100%"), ("text-align", "center"), ('background-color', 'grey')]),
            dict(selector="caption", props=[("caption-side", "top"), ("font-size", "120%"), ("font-family", "roboto"), ("text-align", "center")])
        ]
        temp = str(symbol) + "<br />Expiry - " + str(exp) + "<br /><br />" + "UnderlyingValue - " + \
            str(underlyingValue)+ "&nbsp;&nbsp;&nbsp;&nbsp;PCR_OI - " + str(pcr_oi) + \
                "&nbsp;&nbsp;&nbsp;&nbsp;PCR_Vol - " + str(pcr_vol) + "<br /><br />Last updated - " + str(timestamp)
        df_style = (df_style.set_table_styles(styles).set_caption(temp))


        df_style = df_style.bar(subset=['OI_c'], color='#eb6e6e')
        df_style = df_style.bar(subset=['OI_p'], color='#4fc95b')
        df_style = df_style.bar(subset=['MaxPain'], color='#df66e8')
        df_style = df_style.bar(subset=['TotalVol_c', 'TotalVol_p'], color='#26abad')
        # df_style = df_style.bar(subset=['pOI_c', 'pOI_p'], align='mid', color=['#eb6e6e', '#4fc95b'])
        df_style = df_style.set_properties(**{'width':'80px', 'color':'black', 'font-family':'roboto', 'text-align':'center', 'font-weight':'400'})
        df_style = df_style.set_properties(**{'background-color':'#f7f7f7'})
        df_style = df_style.set_properties(**{'background-color':'#ddd5de'}, subset=['strikePrice'])
        df_style = df_style.applymap(lambda x: 'background-color:#f5f4cb', subset=pd.IndexSlice[:atm_index,['BuyQ_c', 'SellQ_c', 'TotalVol_c', 'OI_c', 'pOI_c', 'LTP_c', 'pLTP_c']])
        df_style = df_style.applymap(lambda x: 'background-color:#f5f4cb', subset=pd.IndexSlice[atm_index:,['BuyQ_p', 'SellQ_p', 'TotalVol_p', 'OI_p', 'pOI_p', 'LTP_p', 'pLTP_p']])
        df_style = df_style.apply(highlight_min, subset=['MaxPain'])
        df_style = df_style.set_properties(**{'width':'300px'}, subset=['OI_c', 'OI_p'])
        df_style = df_style.set_properties(**{'width':'200px'}, subset=['TotalVol_c', 'TotalVol_p'])
        df_style = df_style.applymap(color_pcolumn, subset=pd.IndexSlice[:,['pOI_c', 'pOI_p', 'pLTP_c', 'pLTP_p']])

        df_style = df_style.hide_index()
        # df_style = df_style.set_precision(2)
        df_style = df_style.format({'pOI_c':'{:.1f}', 'pLTP_c':'{:.1f}',  \
            'pOI_p':'{:.1f}', 'pLTP_p':'{:.1f}', 'LTP_c':'{:.2f}', 'LTP_p':'{:.2f}', \
                'strikePrice':'{:.2f}', 'MaxPain':'{:.0f}'})   
        html = df_style.render()  
        
        with open("index.html","w") as f:
            f.write(html)

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
    symbol='NIFTY'
    type1 = 'indices'  #equities/indices
    expiry = '31-Dec-2020'
    nse.get_output(symbol=symbol, type=type1, expiry=expiry)


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

    # df.style.format({'A': '{:.16f}', 'D': '{:.5f}'})

    