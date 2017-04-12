class TradeRequest(object):
    def __init__(self, trade_request):
        self.model = trade_request['model']
        self.account_instructions = self.trade_request['account_instructions']

