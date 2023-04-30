import numpy as np
import re
import os
import pandas as pd 
from nltk.tokenize import RegexpTokenizer, sent_tokenize
from urllib.request import urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

# Loading files 
stop_word_file = '/blackcoffer/StopWords/StopWords_Generic.txt'

positive_words_file = '/blackcoffer/MasterDictionary/positive-words.txt'

negative_word_file = '/blackcoffer/MasterDictionary/negative-words.txt'

input = pd.read_excel('/blackcoffer/Input.xlsx')

# print(input.head())

urls = input['URL']

def GetArticleNames(urls):
    titles = []
    
    for i in range(len(urls)):
        title = urls[i]
        title_clean = title[title.index('m/' )+ 2 : -1].replace('-', ' ')
        titles.append(title_clean)
    return titles


titles = GetArticleNames(urls)

text = []
for url in urls:
    
    page = requests.get(url, headers = {"User-Agent":"XY"})
    soup = BeautifulSoup(page.text , 'html.parser')

    try:
        s_text = soup . find(attrs = { 'class' : 'td-post-content'}).get_text()
    except Exception:
        s_text = ""
    
    text.append(s_text)


text_transform = []
for i in range(len(text)):
    text_transform.append(text[i].replace('\n', ' '))


with open(positive_words_file, "r") as pos_file:
    positive_words = pos_file.read().lower()
positive_word_list = positive_words.split('\n')

# positive_word_list[:5]

with open(negative_word_file, 'r', encoding="ISO-8859-1") as neg_file:
    negative_words= neg_file.read().lower()
negative_word_list = negative_words.split('\n')

# negative_word_list[:5]


with open(stop_word_file,'r') as stop_word_file:
    stop_words = stop_word_file.read().lower()
stop_word_list = stop_words.split('\n')

# stop_word_list[:5]


def Tokenizer(text):
    text = text.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    filtered_words = list(filter(lambda token: token not in stop_word_list, tokens))
    return filtered_words

def FilterWords(text):
    words = []
    
    for i in range(len(text)):
        word = Tokenizer(text[i])
        words.append(word)
    return words


text_list= FilterWords(text_transform)
# text_list[0][:5]

words_count = []
for i in range(len(text_list)):
    word_count = len(text_list[i])
    words_count.append(word_count)



def PositiveScore(text):
    positive_score=[] 
    for i in range(len(text)):
        pos_word = 0
        for word in text[i]:
            if word in positive_word_list:
                pos_word +=1
        positive_score.append(pos_word)
    return positive_score


positive_score = PositiveScore(text_list)
# positive_score[0]


def NegativeScore(text):
    negative_score=[] 
    for i in range(len(text)):
        neg_word = 0
        for word in text[i]:
            if word in negative_word_list:
                neg_word +=1
        negative_score.append(neg_word)
    return negative_score


negative_score = NegativeScore(text_list)
# negative_score[0]

def PolarityScore(positive_score, negative_score):
    polarity_score = []
    for i in range(len(positive_score)):
        pol_score = (positive_score[i] - negative_score[i])/((positive_score[i] + negative_score[i])+0.000001)
        polarity_score.append(pol_score)
    return polarity_score

polarity_score = PolarityScore(positive_score, negative_score)
# polarity_score[0]


def SubjectivityScore(positive_score, negative_score, total_word_count):
    subjectivity_score = []
    for i in range(len(positive_score)):
        sub_score = ((positive_score[i] + negative_score[i])/ ((total_word_count[i]) + 0.000001))
        subjectivity_score.append(sub_score)
    return subjectivity_score

subjectivity_score = SubjectivityScore(positive_score, negative_score, words_count)
# subjectivity_score[0]



def SentenceCount(text):
    sentence_count=[]
    for i in range(len(text)):
        sentences =  len(sent_tokenize(text[i]))
        sentence_count.append(sentences)
    return sentence_count


sentence_count = SentenceCount(text_transform)
# sentence_count[0]


def AverageSentenceLength(words_count, sentence_count):
    
    Average_Sentence_Lenght=[]
    for i in range(len(words_count)):
        sent_count = sentence_count[i]
        if sent_count > 0 : 
            avg_sent_len = round(words_count[i] / sentence_count[i])
            Average_Sentence_Lenght.append(avg_sent_len)
        else:
            avg_sent_len = 0
            Average_Sentence_Lenght.append(avg_sent_len)
    return Average_Sentence_Lenght



average_sentence_lenght = AverageSentenceLength(words_count, sentence_count)
# average_sentence_lenght[0]


def ComplexWordCount(text):
    complex_word_count =[]
    for i in range(len(text)):
        complexWord = 0

        for word in text[i]:
            vowels=0
            if word.endswith(('es','ed')):
                pass
            else:
                for w in word:
                    if(w=='a' or w=='e' or w=='i' or w=='o' or w=='u'):
                        vowels += 1
                if(vowels > 2):
                    complexWord += 1
        complex_word_count.append(complexWord)
    return complex_word_count

complex_word_count = ComplexWordCount(text_list)
# complex_word_count[0]


def PercentageComplexWord(complex_word_count, words_count):
    complex_word_percentage = []
    
    for i in range(len(words_count)):
        if words_count[i] > 0 :
            complex_word_percent = complex_word_count[i]/words_count[i]
        else:
            complex_word_percent = 0
        complex_word_percentage.append(complex_word_percent)
    
    return complex_word_percentage


percentage_complex_word = PercentageComplexWord(complex_word_count, words_count)
# percentage_complex_word[0]



def FogIndex(average_sentence_lenght, percentage_complex_word):
    fog_index = []
    for i in range(len(average_sentence_lenght)):
        fogIndex = 0.4 * (average_sentence_lenght[i] + percentage_complex_word[i])
        fog_index.append(fogIndex)
    return fog_index


fog_index = FogIndex(average_sentence_lenght, percentage_complex_word)
# fog_index[0]



def SyllablesCount(text):
    syllable_count = []
    for i in range(len(text)):
        count = 0
        for j in range(len(text[i])):
            
            vowels = 'aeiouy'
            starts = ['ou','ei','ae','ea','eu','oi']
            endings = ['es','ed']
            word = text[i][j].strip(".:;?!")
            if word[0] in vowels:
                count +=1
            for index in range(1,len(word)):
                if word[index] in vowels and word[index-1] not in vowels:
                    count +=1
            if word.endswith('e'):
                count -= 1
            if word.endswith('le'):
                count+=1
            if count == 0:
                count +=1
        syllable_count.append(count)
    return syllable_count


syllable_count = SyllablesCount(text_list)
# syllable_count[0]


def PresonalPronoun(words):
    presonal_pronoun = []
    for i in range(len(words)):
        pronounRegex = re.compile(r'\b(I|we|my|ours|(?-i:us))\b',re.I)
        pronouns = pronounRegex.findall(words[i])
        presonal_pronoun.append(pronouns)
    return presonal_pronoun

presonal_pronoun = PresonalPronoun(text_transform)

# presonal_pronoun[0]



char_count=[]
for i in range(len(text_transform)):
    char = text_transform[i].replace(' ', '')
    char = len(char)
    char_count.append(char)


# char_count[7]


avg_word_count = []
for i in range(len(char_count)):
    if words_count[i] == 0 | char_count[i]==0 :
        AWC = 0
        avg_word_count.append(AWC)
    else:
        AWC = char_count[i]/words_count[i]
        avg_word_count.append(round(AWC))


# avg_word_count[0]

input['TITLE'] = titles
input['POSITIVE SCORE'] = positive_score
input['NEGATIVE SCORE'] = negative_score
input['POLARITY SCORE'] = polarity_score
input['SUBJECTIVITY SCORE'] = subjectivity_score
input['PERCENTAGE OF COMPLEX WORDS'] = percentage_complex_word
input['AVG SENTENCE LENGTH'] = average_sentence_lenght
input['FOG INDEX'] = fog_index
input['AVG NUMBER OF WORDS PER SENTENCE'] = average_sentence_lenght
input['COMPLEX WORD COUNT'] = complex_word_count
input['WORD COUNT'] = words_count
input['SYLLABLE PER WORD'] = syllable_count
input['PERSONAL PRONOUNS'] = presonal_pronoun
input['AVG WORD LENGTH'] = avg_word_count

# print(input.head())

input.to_excel("Output Data Structure.xlsx")

