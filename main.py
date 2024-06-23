import json
import openai
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf

openai.api_key=open('api_key','r').read()

def get_stock_price(ticker):
    return str(yf.Ticker(ticker).history(period='1y').iloc[-1].close)

def calculate_SMA(ticker,window):
    data=yf.Ticker(ticker).history(periods='1y').close
    return str(data.rolling(window=window).mean().iloc[-1])
    
def calculate_EMA(ticker,window):
    data=yf.Ticker(ticker).history(periods='1y').close
    return str(data.ewm(window=window).mean().iloc[-1])

def calculate_RSI (ticker):
    data=yf.Ticker(ticker).history(periods='1y').close
    delta=data.diff()
    up = delta.clip(lower=0)
    down= -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=14-1,adjust=False).mean()
    ema_down = down.ewm(com=14-1,adjust=False).mean()
    rs = ema_up/ema_down
    return str(100-(100/(1+rs)).iloc[-1])

def calculate_MACD(ticker,window):
    data=yf.Ticker(ticker).history(periods='1y').close
    short_EMA=data.ewm(span=12, adjust=False).mean()
    long_EMA=data.ewm(span=26, adjust=False).mean()

    MACD = short_EMA-long_EMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    MACD_histogram = MACD - signal

    return f'{MACD[-1]},{signal[-1]},{MACD_histogram[-1]}'


def plot_stock_price(ticker):
    data = yf.Ticker(ticker).history(period='1y').close
    plt.figure(figsize=(10, 5))
    plt.plot( *args :data.index,data.close)
    plt.title('{ticker} Stock Price Over Last Year')
    plt.xlabel('Date')
    plt.ylabel('Stock Price {$}')
    plt.grid(True)
    plt.savefig('stock.png')
    plot.close()



fuctions = [
    {
        'name' : 'get_stock_price',
        'description':'Gets the latest stock price given the ticker symbol of a company.',
        'parameters':{
            'type': 'object',
            'properties':{
                'ticker':{
                    'type':'string',
                    'decription': 'The stock symbol for a company(for example TATAPOWER for TATA).'
                }
            },
            'required':['tikcer']
             

        }
    },
    {
       'name' : 'calculate_SMA',
        'description':'Calculate the single moving average for a given ticker and a window',
        'parameters':{
            'type': 'object',
            'properties':{
                'ticker':{
                    'type':'string',
                    'decription': 'The stock symbol for a company(for example TATAPOWER for TATA).'
                },
                "window":{
                    'type':'string',
                    'decription':'The timeframe to consider when calculating the SMA'
                
                }
            },
            'required':["ticker","window"],
        },
    },
    {
        'name' : 'calculate_EMA',
        'description':'Calculate the expotential moving average for a given ticker and a window',
        'parameters':{
            'type': 'object',
            'properties':{
                'ticker':{
                    'type':'string',
                    'decription': 'The stock symbol for a company(for example TATAPOWER for TATA).'
                },
                "window":{
                    'type':'integer',
                    'decription':'The timeframe to consider when calculating the EMA'
                
                }
            },
            'required':["ticker","window"],
        },
    },
    {
      'name' : 'calculate_RSI',
        'description':'Calculate the RSI for a given ticker.',
        'parameters':{
            'type': 'object',
            'properties':{
                'ticker':{
                    'type':'string',
                    'decription': 'The stock symbol for a company(for example TATAPOWER for TATA).'
                },
                
            },
            
            'required':["ticker"],
        },  
    },
    {
        'name' : 'calculate_MACD',
        'description':'Calculate the MACD for a given ticker.',
        'parameters':{
            'type': 'object',
            'properties':{
                'ticker':{
                    'type':'string',
                    'decription': 'The stock symbol for a company(for example TATAPOWER for TATA).'
                },
                
            },
            
            'required':["ticker"],
        },  
    },
    {
        'name' : 'plot_stock_price',
        'description':'plot the stock price for the last year given the ticker of a company.',
        'parameters':{
            'type': 'object',
            'properties':{
                'ticker':{
                    'type':'string',
                    'decription': 'The stock symbol for a company(for example TATAPOWER for TATA).'
                }
                
            },
            
            'required':["ticker"],
        },  
    },
    

]

avilable_fuctions ={
    'get_stock_price':get_stock_price,
    'calculate_SMA':calculate_SMA,
    'calculate_EMA':calculate_EMA,
    'calculate_RSI':calculate_RSI,
    'calculate_MACD':calculate_MACD,
    'plot_stock_price':plot_stock_price
}

if 'messages' not in st.sesssion_state:
    st.session_state['messages']=[]
st.title('Stock Analysis Chatbot Assistant')
user_input = st.text_input('your input:')
if user_input:
    try:
        st.session_state['messages'].append({'role':'user','content':f'{user_input}'})

        response = openai.ChatCompletion.create(
            model='gpt 3.5=turbo-0613'
            messages=st.session_state['messages'],
            function_call='auto'
        )
        response_message = response['choices'][0]['message']

        if response_message.get('function_call'):
            function_name= response_message['function_call']['name']
            function_args = json.loads(response_message['function_call']['arguments'])
            if function_name in ['get_stock_price','calculate_RSI','calculate_MACD','plot_stock_price']:
                args_dict={'ticker':function_args.get('ticker')}
            elif function_name in ['calculate_EMA','calculate_SMA']:
                args_dict={'ticker':function_args.get('ticker'),'window':function_args.get('window')}

            function_to_call = available_functions[function_name]
            function_response = function_to_call(**args_dict)

            if function_name == 'plot_stock_price':
                st.image('stock.png')
            else:
                st.session_state['messages'].append(response_message)
                st.session_state['messages'].append(
                    {
                        'role':'function',
                        'name': function_name,
                        'content': function_response

                    }
                )
                second_response=openai.ChatCompletion.create(
                    model='gpt 3.5=turbo-0613'
                    messages=st.session_state['messages']
                )
                st.text(second_response['choices'][0]['messsage']['content'])
                st.session_state['messages'].append({'role':'assistant','content':second_response['choices'][0]['messsage']['content']})
        else:
            st.text(response_message['content'])
            st.session_state['messages'].append({'role':'assistant','content':response_message['content']})
    except:
        st.text('try again')
