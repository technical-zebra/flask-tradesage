from flask import Flask, request, jsonify
import os
import pandas as pd
import yfinance as yf

app = Flask(__name__)

secret = os.environ.get('API_KEY') # 
mode =  os.environ.get('MODE') #
port = os.environ.get('PORT')

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/stock_data')
def stock_data():
    # Extract parameters from the GET request
    api_key = request.args.get('api_key',type=str)
    data_type = request.args.get('type',type=str)
    symbol = request.args.get('symbol',type=str)
    interval = request.args.get('interval',type=str)
    period = request.args.get('period',type=str)
    start_date = request.args.get('start',type=str)
    end_date = request.args.get('end',type=str)
    data = None
    # Validate API key (assuming a simple comparison for demonstration)
    if mode == "debug": print(api_key, secret)
    if api_key != secret:
        return jsonify({'error': 'Invalid API key'}), 403

    # Validate data type
    if data_type not in ['stock', 'forex']:
        return jsonify({'error': 'Invalid data type'}), 400
    
    # Check if either (start_date and end_date) or (interval and period) is provided, but not both
    if (start_date and end_date) and (interval or period):
        return jsonify({'error': 'Provide either start_date and end_date OR interval and period, but not both'}), 400

    # If neither set of parameters is provided, return an error
    if not ((start_date and end_date) or (interval and period)):
        return jsonify({'error': 'You must provide either start_date and end_date OR interval and period'}), 400

    if (interval and period):
        #Validate interval
        valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        if interval not in valid_intervals:
            return jsonify({'error': 'Invalid interval'}), 400

        #Validate period
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        if period and period not in valid_periods:
            return jsonify({'error': 'Invalid period'}), 400
    else:
        #Validate start and end dates
        if not period and (not start_date or not end_date):
            return jsonify({'error': 'Start and end dates are required if period is not provided'}), 400

    # Fetch data based on type
    
    try:

        if data_type == 'forex':
            # Implement forex data fetching logic
            symbol = f"{symbol.upper()}=X"

        if start_date and end_date:
            # Fetch data using start_date and end_date
            if mode == "debug": print("using start_date and end_date")
            data = yf.download(tickers=symbol, start=start_date, end=end_date)
        else:
            # Fetch data using interval and period
            if mode == "debug": print("using interval and period")
            data = yf.download(tickers=symbol, interval=interval, period=period)

        
        data.reset_index(inplace=True)
        if 'Date' in data.columns:
            data['Datetime'] = data['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            data.drop(columns=['Date'], inplace=True)
        else:
            data['Datetime'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        data = data.to_json(orient='records')
        if mode == "debug": print(data)

        
        return data
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if mode == "debug": app.run(host='0.0.0.0', port=8080)
    else: app.run(host='0.0.0.0',port=port)
