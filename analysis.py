def calculate_sma(data, period=5):
    sma = data['4. close'].rolling(window=period).mean()
    return sma
