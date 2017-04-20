class TradeAllocator(object):
    def __init__(self, account_matrix, trade_list):
        self.account_matrix = account_matrix
        self.trade_list = trade_list
        self.account_trade_matrix = self.construct_account_trade_matrix(self.account_matrix, self.trade_list)

    def construct_account_trade_matrix(self, account_matrix, trade_list):
        del trade_list['dollar_trades']
        del trade_list['price']
        account_trade_matrix = pd.concat([account_matrix, trade_list], axis=1).assign(scores=0)
        return account_trade_matrix.fillna(0)

    def score_trades(self):
        m = self.account_trade_matrix
        m = m.apply(self.sum_scores, axis=1)
        print(m)


    def sum_scores(self, score):
        if score['shares'] < 0:
            score['scores']+= 1
            k = score.drop(['shares','scores'])
            if k.iloc[0] == 0 and k.iloc[1] != 0 or k.iloc[0] != 0 and k.iloc[1] == 0:
                score['scores'] += 1
        return score


    def determine_trades(self, trade_account_matrix):
        trade_account_matrix['sells'] = trade_account_matrix['dollar_trades'].apply(lambda x: 0 if x > 0 else x)

        return trade_account_matrix

