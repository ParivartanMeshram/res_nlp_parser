import os

import docx2txt
import spacy
from django.conf import settings
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacy.lang.en import English
import re
import io
import json
import pandas as pd
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage



nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(
                resource_manager,
                fake_file_handle,
                codec='utf-8',
                laparams=LAParams()
            )
            page_interpreter = PDFPageInterpreter(
                resource_manager,
                converter
            )
            page_interpreter.process_page(page)
            text = fake_file_handle.getvalue()
            yield text
            converter.close()
            fake_file_handle.close()


def get_text_all_from_pdf(file_path):
    text = ''
    for page in extract_text_from_pdf(file_path):
        text += ' ' + page
    return text


def extract_text_from_doc(file_path):
    try:
        temp = docx2txt.process(file_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)
    except:
        return " "


def get_text(file_path):
    file_type = file_path.split(".")[-1]
    if file_type == "pdf":
        text = get_text_all_from_pdf(file_path)
    elif file_type == "docx" :
        text=extract_text_from_doc(file_path)
    else:
        raise ValueError("unsupported file format")
    return text


# def extract_name(cv_text):
#     nlp_text = nlp(cv_text)
#     pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
#     matcher.add('NAME', None, pattern)
#     matches = matcher(nlp_text)
#     for match_id, start, end in matches:
#         span = nlp_text[start:end]
#         return span.text


def extract_mobile_number(text):
    regex=r'''(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)[-\.\s]*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'''
    phone=re.findall(re.compile(regex),text)

    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number

def extract_skills(resume_text):
    nlp=English()
    nlp_text = nlp(resume_text.lower())
    with open("api/skills.json") as f:
        SKILLS = json.loads(f.read())
    matcher = PhraseMatcher(nlp.vocab)
    patterns = list(nlp.pipe(SKILLS))
    matcher.add("SKILLS", None, *patterns)
    matches = matcher(nlp_text)
    return list(set([nlp_text[start:end].text for match_id, start, end in matches]))

def extract_email(resume_text):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", resume_text)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None

def extract_name(cv_text):
    expnlp = spacy.load("api/name_model_5_drop_0.1_sgd_losses_i50")
    doc = expnlp(cv_text)
    return ["{}".format(ent.text) for ent in doc.ents]

def extract_experience(cv_text):
    expnlp=spacy.load("api/exp_model_2")
    doc = expnlp(cv_text)
    return ["{}".format(ent.text) for ent in doc.ents]

def resume_parser(file_path):
    cv_text = get_text(file_path)
    data=dict.fromkeys(("Name","Email","ContactNo","Experience","Skills"))
    data["Name"]=extract_name(cv_text)
    data["ContactNo"]=extract_mobile_number(cv_text)
    data["Email"]=extract_email(cv_text)
    data["Skills"]=extract_skills(cv_text)
    data["Experience"]=extract_experience(cv_text)
    return data


# if __name__ == "__main__":
#     # import os
#     # path=os.path.join(os.getcwd(),"test")
#     # files=[f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
#     # for res in files:
#     #      print(resume_parser("./test/{}".format(res)))
#     nlp = spacy.load('en_core_web_sm')
#     cv_text = get_text("./resume3.docx")
#     cv_text2=get_text("./resume1.pdf")
#     doc=nlp(cv_text)
#     doc2=nlp(cv_text2)
#     all_world=[token.text for token in doc
#                if  not token.is_stop and token.is_alpha and token.pos_=="PROPN"]
#     all_world2 = [token.text for token in doc2
#                  if  not token.is_stop and token.is_alpha and token.pos_ == "PROPN"]
#     diff=" ".join(set([x for x in all_world if x in all_world2]))
#     nlp3=English()
#     doc3=nlp(diff)
#     print([x.is_stop for x in doc3])
#     # print(all_world,all_world2)
#     # print(extract_text_from_doc("./test/Veera.V.docx"))
#     # print(extract_skills(cv_text))
#     # print(extract_name(cv_text))
#     # print(extract_mobile_number(cv_text))
#     # print(resume_parser("./resume1.pdf"))
#     # print(resume_parser("./resume2.docx"))
#     # print(resume_parser("./resume.docx"))
#     # print(resume_parser("./resume5.pdf"))