import ccxt
import pandas as pd
import time
import logging

# Настройка логирования
logging.basicConfig(filename="trading_bot_test.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# API-ключи Huobi (не нужны для теста)
api_key = "YOUR_API_KEY"
api_secret = "YOUR_SECRET_KEY"

# Подключение к Huobi
exchange = ccxt.huobi({
    "apiKey": api_key,
    "secret": api_secret,
    "enableRateLimit": True
})

# Торговая пара и параметры
symbol = "BTC/USDT"
timeframe = "1m"  # Интервал свечей
order_size = 0.001  # Объём покупки/продажи

# Флаг для отслеживания состояния жёлтой линии
waiting_for_sell_signal = False  

# Функция получения данных и расчёта SMA
def get_indicators():
    candles = exchange.fetch_ohlcv(symbol, timeframe, limit=60)
    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["SMA_YELLOW"] = df["close"].rolling(window=7).mean()  # Жёлтая линия
    df["SMA_BLUE"] = df["close"].rolling(window=25).mean()  # Синяя линия
    df["SMA_PURPLE"] = df["close"].rolling(window=50).mean()  # Фиолетовая линия
    df["SMA_RED"] = df["close"].rolling(window=60).mean()  # Красная линия
    return df

# Флаг для отслеживания состояния жёлтой линии
waiting_for_sell_signal = False  

# Основной цикл бота (тестовый режим)
while True:
    df = get_indicators()
    last_row = df.iloc[-1]  # Последняя свеча

    yellow = last_row["SMA_YELLOW"]
    blue = last_row["SMA_BLUE"]
    purple = last_row["SMA_PURPLE"]
    red = last_row["SMA_RED"]
    current_price = last_row["close"]

    # Лог текущего состояния рынка
    log_message = f"Цена: {current_price} | YELLOW: {yellow}, BLUE: {blue}, PURPLE: {purple}, RED: {red}"
    print(log_message)
    logging.info(log_message)

    # Покупка, если жёлтая линия ниже всех остальных
    if yellow < blue and yellow < purple and yellow < red and not waiting_for_sell_signal:
        print(f"Жёлтая линия ниже всех -> ПОКУПКА (ТЕСТ) | Цена: {current_price}")
        logging.info(f"TEST BUY | Цена: {current_price}")
        waiting_for_sell_signal = True  # Ждём сигнала на продажу

    # Продажа только если жёлтая была ниже всех и затем пересекла вниз
    if waiting_for_sell_signal and yellow > blue and yellow > purple and yellow > red:
        print("Жёлтая линия пересекла вверх -> ЖДЁМ ОБРАТНОГО ПЕРЕСЕЧЕНИЯ")
        logging.info("Жёлтая линия выше всех -> Ожидание пересечения вниз")

    # Если жёлтая была выше всех и пересекла вниз – продаём
    if waiting_for_sell_signal and (yellow < blue or yellow < purple or yellow < red):
        print(f"Жёлтая снова ниже одной из линий -> ПРОДАЖА (ТЕСТ) | Цена: {current_price}")
        logging.info(f"TEST SELL | Цена: {current_price}")
        waiting_for_sell_signal = False  # Ждём нового сигнала на покупку

    time.sleep(10)  # Ждём 1 минуту перед следующей проверкой
