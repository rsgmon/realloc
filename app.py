import json
from core.trade_manager import TradeManager

def handler(event, context):
    if 'body' in event:
        return json.dumps(TradeManager('json', event['body']).trade_instructions.to_dict(orient='records'))
    else:
        return json.dumps(TradeManager('json', event).trade_instructions.to_dict(orient='records'))