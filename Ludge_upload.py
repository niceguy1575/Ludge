#!/usr/bin/python

# load library
import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, FR
import sys
import re
from bs4 import BeautifulSoup
import time
import random
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dateutil.relativedelta import relativedelta

# download file from url
def reqPage(url, headers, param=None, retries=3):
	resp = None

	try:
		resp = requests.get(url, params=param, headers=headers)
		resp.raise_for_status()
	except requests.exceptions.HTTPError as e:
		if 500 <= resp.status_code < 600 and retries > 0:
			print('Retries : {0}'.format(retries))
			return reqPage(url, param, retries - 1)
		else:
			return resp.status_code
	return resp

def getSoup(url, agent):
	headers = {'Referer': url,
			   'User-Agent': agent}
	#headers = { 
		#'User-Agent': agent,
		#'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
		#'Accept-Language' : 'en-US,en;q=0.5',
		#'Accept-Encoding' : 'gzip', 
		#'DNT' : '1', # Do Not Track Request Header 
		#'Connection' : 'close'
	#}


	req = reqPage(url, headers)
	req_txt = req.text
	soup = BeautifulSoup(req_txt, 'html.parser')
	
	return soup

class SendEmail:

	def __init__(self, senderEmailServer, senderEmail, senderPW):
		try: 
			# 587 -> outlook port number
			self.smtp = smtplib.SMTP(senderEmailServer, 587)
			self.smtp.ehlo() # say Hello
			self.smtp.starttls() # TLS 사용시 필요
			self.smtp.login(senderEmail, senderPW) 
		except Exception as e:
			print(e)
			self.smtp = smtplib.SMTP(senderEmailServer, 587)
			self.smtp.ehlo() # say Hello
			# self.smtp.starttls() # TLS 사용시 필요
			self.smtp.login(senderEmail, senderPW) 
			
	def MailSender(self, message, subject, senderEmail, targetEmail):
		
		# send with message
		#msg = MIMEText(message) 

		# send with HTML
		msg = MIMEMultipart('alternative')
		msg['Subject'] = subject
		msg['From'] = senderEmail
		msg['To'] = targetEmail
		
		# attach HTML
		msg.attach( MIMEText(message, 'html') )

		self.smtp.sendmail(senderEmail, targetEmail, msg.as_string()) 
		self.QuitSMTP()
		
	def QuitSMTP(self):
		self.smtp.quit()
		

def IsCartierOnline(url_list, user_agent_list, SenderMailServer, SenderEmail, SenderPW, TargetEmail):

	### 재고가 있으면 hidden 버튼이 안뜸
	## 쇼핑백 추가하기 확인
	print("1. make agent")
	user_agent = user_agent_list[random.randint(0, len(user_agent_list)-1)]
	print(user_agent)

	clockText_list = []
	print("2. get soup")
	for url in url_list:
		soup = getSoup(url, user_agent)
		print("Soup Complete!")

		canBuyBtn = soup.find_all("button", class_ = "product-add__button add-to-cart button button--primary button--fluid set--w-100")
		cantBuyBtn = soup.find_all("button", class_ = "product-add__button add-to-cart button button--primary button--fluid set--w-100 hidden")

		# clock name
		ClockName = soup.find_all("h1", class_ = "pdp__name heading-type fluid-type--deka-hecto text-line--normal")[0].get_text().replace('\n','')
		ClockModel = soup.find_all("div", class_ = "pdp-main__short-description cms-generic-copy text-line--medium")[0].get_text().replace('\n','')
		
		if len(canBuyBtn):
			clockText = """<a href='""" + url + """'> + """ + 'Buy Your Clock: ' + ClockModel + """  </a> """
			clockText_list.append(clockText)


	print("3. e-mail text")
	## do - alert
	Subject = "⏰ " + " 시계 알리미!:"
	Message_base = \
			"""<html>
					<head>
						<meta charset="utf-8">
					</head>
					<body>
						<h2> 까르띠에 시계 알리미 ⌚ </h2> 

			"""
	for ct in clockText_list:
		Message_base = Message_base + ct + "<br>"

	Message = Message_base + """
				</body>
			</html>
		"""
		
	print("4. send email")
	for te in TargetEmail:
		SMail = SendEmail(SenderMailServer, SenderEmail, SenderPW) # 수신 메일 설정 
		SMail.MailSender(Message, Subject, SenderEmail, te)
				
		print(ClockName + " " + ClockModel + " do - alert")
	else:
		## again after 30 minutes
		print(ClockName + " " + ClockModel + " do again - after 30 minutes")
		
		
if __name__ == '__main__':

	# set parameter
	targetUrl = ['https://www.cartier.com/ko-kr/%EC%8B%9C%EA%B3%84/%EC%97%AC%EC%84%B1%EC%9A%A9-%EC%8B%9C%EA%B3%84/%ED%83%B1%ED%81%AC-%EB%A8%B8%EC%8A%A4%ED%8A%B8-%EC%9B%8C%EC%B9%98-CRWSTA0042.html',
				'https://www.cartier.com/ko-kr/%EC%8B%9C%EA%B3%84/%EC%97%AC%EC%84%B1%EC%9A%A9-%EC%8B%9C%EA%B3%84/%ED%83%B1%ED%81%AC-%EB%A8%B8%EC%8A%A4%ED%8A%B8-%EC%9B%8C%EC%B9%98-CRWSTA0041.html',
				'https://www.cartier.com/ko-kr/%EC%8B%9C%EA%B3%84/%EC%97%AC%EC%84%B1%EC%9A%A9-%EC%8B%9C%EA%B3%84/%ED%83%B1%ED%81%AC-%ED%94%84%EB%9E%91%EC%84%B8%EC%A6%88-%EC%9B%8C%EC%B9%98-CRW51008Q3.html',
				'https://www.cartier.com/ko-kr/be-inspired/%EA%B7%B8%EB%A5%BC-%EC%9C%84%ED%95%9C-%EA%B8%B0%ED%94%84%ED%8A%B8/%ED%83%B1%ED%81%AC-%EB%A8%B8%EC%8A%A4%ED%8A%B8-%EC%9B%8C%EC%B9%98-CRWSTA0040.html',
				'https://www.cartier.com/ko-kr/%EC%8B%9C%EA%B3%84/%EC%97%AC%EC%84%B1%EC%9A%A9-%EC%8B%9C%EA%B3%84/%ED%83%B1%ED%81%AC-%EB%A8%B8%EC%8A%A4%ED%8A%B8-%EC%9B%8C%EC%B9%98-CRWSTA0051.html',
				'https://www.cartier.com/ko-kr/%EC%8B%9C%EA%B3%84/%EC%97%AC%EC%84%B1%EC%9A%A9-%EC%8B%9C%EA%B3%84/%ED%83%B1%ED%81%AC-%EB%A8%B8%EC%8A%A4%ED%8A%B8-%EC%9B%8C%EC%B9%98-CRWSTA0059.html',
				'https://www.cartier.com/ko-kr/%EC%8B%9C%EA%B3%84/%EC%97%AC%EC%84%B1%EC%9A%A9-%EC%8B%9C%EA%B3%84/%ED%83%B1%ED%81%AC-%EB%A8%B8%EC%8A%A4%ED%8A%B8-%EC%9B%8C%EC%B9%98-CRWSTA0061.html',
				'https://www.cartier.com/ko-kr/%EC%8B%9C%EA%B3%84/%EC%97%AC%EC%84%B1%EC%9A%A9-%EC%8B%9C%EA%B3%84/%ED%83%B1%ED%81%AC-%EB%A8%B8%EC%8A%A4%ED%8A%B8-%EC%9B%8C%EC%B9%98-CRWSTA0060.html',
				'https://www.cartier.com/ko-kr/%EC%8B%9C%EA%B3%84/%EC%97%AC%EC%84%B1%EC%9A%A9-%EC%8B%9C%EA%B3%84/%ED%83%B1%ED%81%AC-%EB%A8%B8%EC%8A%A4%ED%8A%B8-%EC%9B%8C%EC%B9%98-CRWSTA0062.html'
				]


	user_agent_list = [
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
	'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
	'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
	]

	SenderMailServer = ''
	SenderEmail = ''
	SenderPW = ''
	TargetEmail = ['']
	
	# Do Job
	IsCartierOnline(targetUrl, user_agent_list, SenderMailServer, SenderEmail, SenderPW, TargetEmail)
	sys.exit()