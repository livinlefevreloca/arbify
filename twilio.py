from twilio.rest import Client
import pandas as pd


class MessageSender:
    def __init__(self):
        self.acct = 'AC95644ad59890073a461615280ee51d75'
        self.token = 'ccdb3c50264d7c19d7a15c8c3706d467'
        self.client = Client(self.acct, self.token)
        self.out_numbers = ['+12053825273', '+14148976612', '+18608173523']

    def read_arbs(self, csv):
        self.df = pd.read_csv(csv)
        self.cols = self.df.columns

    def send_message(self):
        assert self.df is not None, "Must read arbs before sending a message"

        for row in self.df.values:
            elems = [list(x) for x in zip(self.cols, row)]
            elems = elems[:-1]
            elems[-1][-1] = round(elems[-1][-1], 2)
            elems[-2][-1] = round(elems[-2][-1], 2)
            elems[-3][-1] = round(elems[-3][-1], 2)
            body = ''
            for tup in elems:
                body += '{}: {}\n'.format(*tup)

            for num in self.out_numbers:
                self.client.messages.create(to=num, from_='+14142468344', body=body)

        self.df = None
        self.cols = None
