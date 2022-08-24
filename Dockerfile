FROM python:3

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY portfolio_manager/TradeManager TradeManager
RUN pip insstal
COPY portfolio_manager/test test
COPY __init__.py .