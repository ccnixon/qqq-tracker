class Quote:
  ticker: str
  price: float
  volume: int
  timestamp: str
  def __init__(self, ticker: str, price: float, volume: int, timestamp: str) -> None:
      super().__init__()
      self.price = price
      self.ticker = ticker
      self.volume = volume
      self.timestamp = timestamp
