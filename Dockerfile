FROM python:3.4.10


COPY . ./portmgr
WORKDIR ./portmgr
#RUN pip install -r requirements.txt
RUN pip install -e .