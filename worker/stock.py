import statistics
from worker.notifier import Notifier


class Data:
    history = []
    std_dev = 0


class Stock:
    _ticker: str
    _volume: Data
    _prices: Data
    _notifier: Notifier

    def __init__(self, ticker) -> None:
        self._ticker = ticker
        self._volume = Data()
        self._prices = Data()
        self._notifier = Notifier()

    def get_volume(self) -> Data:
        return self._volume

    def get_prices(self) -> Data:
        return self._prices

    def std_dev_vol(self) -> float:
        return self._volume.std_dev

    def std_dev_price(self) -> float:
        return self._prices.std_dev

    def check_for_average_deviation(self, current_price, current_volume) -> None:
        prices = self._prices.history
        volume = self._prices.volume

        # Only check for average deviation if we have at least an hour of price data.
        if (len(prices) < 60):
            return

        avg_price = statistics.median(prices)
        avg_volume = statistics.median(volume)

        if (current_price >= (3*avg_price)):
            self._notifier.send_price_alert(avg_price, current_price)
        if (avg_volume >= (3*current_volume)):
            self._notifier.send_vol_alert(avg_volume, current_volume)

    def update(self, price, volume):
        vol = self.get_volume()
        prices = self.get_prices()
        vol.history.append(volume)
        prices.history.append(price)
        if (len(prices.history) > 1 & len(vol.history) > 1):
            vol.std_dev = statistics.stdev(vol.history)
            prices.std_dev = statistics.stdev(prices.history)

        # Only keep the last 24h worth of history in memory
        if (len(prices.history) > 1440):
            prices.history.pop(0)
            vol.history.pop(0)
