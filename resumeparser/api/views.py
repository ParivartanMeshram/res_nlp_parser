from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
from .tinyresumeparser import resume_parser, get_text
import requests
import uuid



def resumeparsing(request, *args, **kwrgs):

	if request.method == 'GET':
		url_list = list(request.GET.get('url_list').split(","))
		# url_list="http://workonicparser.itechnolabs.tech/api/?url_list=https://workonic.yapits.com/uploaded_resumes/1597385807tani_resume.pdf,https://workonic.yapits.com/uploaded_resumes/1597588784MaheshShardul[4_11].docx,https://workonic.yapits.com/uploaded_resumes/1597647997DurgeshKumarAwasthi[4_8].pdf".split(",")
		print(len(url_list))
		data = dict()
		c=0
		for url in url_list:
			r = requests.get(url, allow_redirects=True)
			if url.endswith(".pdf"):
				resumename = 'api/media/resume'+str(uuid.uuid1())+".pdf"
			if url.endswith(".docx"):
				resumename = 'api/media/resume' + str(uuid.uuid1()) + ".docx"
			with open(resumename,'wb') as f:
				f.write(r.content)
			data[c] = resume_parser(resumename)#, 'resume':url}
			data[c]['resume'] = url
			c+=1
		# data= resume_parser("api/media/"+"AbhilashaShukla.docx")
		# print(get_text("api/media/"+"AbhilashaShukla.docx"))
		# print(data)
		# return HttpResponse("hi")
		#
		return HttpResponse(json.dumps(data))
