FROM python
COPY app.py /
COPY requirements.txt /
COPY serviceAccount.json /
RUN pip install pip update 
RUN pip install -r requirements.txt
ENV ACCESS_TOKEN=5314433501:AAFq9GIDAJWyt4rE61b9C3Chg20ikXeT6As
ENV URL=https://testchatbot-comp7940.azurewebsites.net
CMD python app.py