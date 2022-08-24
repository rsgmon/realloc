FROM python:3

#COPY requirements.txt requirements.txt
#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt
COPY portfolio_manager portfolio_manager
RUN pip install -e .