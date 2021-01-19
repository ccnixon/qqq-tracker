import os
from lib.db import DB
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

sg = SendGridAPIClient(
    os.getenv('SENDGRID_API_KEY'))

db = DB()
class Notifier:
    def send_notifications(self, metric: str, ticker: str) -> None:
        subscriptions = db.get_subscriptions(ticker)
        
        if len(subscriptions) == 0:
            return
        
        subscriptions = subscriptions.pop()
        
        if metric in subscriptions:
          emails = subscriptions[metric]  
          for email in emails:
            message = Mail(
                from_email='chrisnxn@gmail.com',
                to_emails=email,
                subject='Market Tracker Alert',
                html_content=f'<strong>{ticker} has seen a {metric} increase of 3x it\'s  60 min average.</strong>')
            sg.send(message)
