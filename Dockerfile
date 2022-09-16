FROM python


COPY . ./portmgr
WORKDIR ./portmgr
#RUN pip install -r requirements.txt
RUN pip install -e .