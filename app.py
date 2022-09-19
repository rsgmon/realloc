import json
from trade_generator.trade_manager import TradeManager

def handler(event, context):
    return json.dumps(TradeManager('json', event).trade_instructions.to_dict(orient='records'))