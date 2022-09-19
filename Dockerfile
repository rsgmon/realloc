FROM public.ecr.aws/lambda/python:3.9
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py ${LAMBDA_TASK_ROOT}
COPY trade_generator ${LAMBDA_TASK_ROOT}/trade_generator
CMD ["app.handler"]