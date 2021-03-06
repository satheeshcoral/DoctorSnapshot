#!/usr/bin/env python3
# Created by Nuo Wang.
# Last modified on 8/17/2017.

# Required libraries.
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk import tokenize
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import gensim
import logging
import pickle

### Step 1: Setting up.

# Load my dataset.
reviews = pd.read_csv("PATH/data/yelp_reviews.csv")
doctors = pd.read_csv("PATH/data/yelp_doctors.csv")

# Extract review texts.
review_main_text_list = []
for i in range(0, len(reviews)):
    paragraphs = reviews.loc[i]["review main text"]
    sentences = tokenize.sent_tokenize(paragraphs)
    for sentence in sentences:
        review_main_text_list.append(sentence)
                
# Set up tokenizer.
tokenizer = RegexpTokenizer(r'\w+')
# Set up stop words.
stop = set(stopwords.words('english'))
# Set up stemmer.
p_stemmer = PorterStemmer()
# Set up logging.
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

### Step 2: Processing texts.

# Store all words.
all_words = []
# Store all sentences.
all_sentences = []
# Store all cleaned up texts.
cleaned_up_review_list = []
# For each review.
for sentence in review_main_text_list:
    # Tokenization
    raw = sentence.lower()
    tokens = tokenizer.tokenize(raw)
    
    # Get stop words
    j = 0
    while j < len(tokens):
        if tokens[j] in stop:
            del tokens[j]
        else:
            j += 1

    cleaned_text = [p_stemmer.stem(i) for i in tokens]
    
    all_sentences.append(cleaned_text)
    for token in cleaned_text:
        all_words.append(token)

### Step 3: Train word2vec and t-SNE model.
# Here I train a word2vec model and reduce it to a 2D t-SNE space.

# Train word2vec using sentences.
model = gensim.models.Word2Vec(all_sentences, size=50, window=100, min_count=5, iter=10, workers=1)

# Prepare input for t-SNE
all_words_unique = nltk.FreqDist(all_words).most_common(4100)
all_words_unique_vec = []
all_words_unique_word = []
for index2, item2 in enumerate(all_words_unique):
    all_words_unique_vec.append(list(model.wv[item2[0]]))
    all_words_unique_word.append(item2[0])
    
# Set up t-SNE model.
tsne_model = TSNE(n_components=2, random_state=10, perplexity=50.0)
X = np.array(all_words_unique_vec)
np.set_printoptions(suppress=True)
# Train t-SNE model.
tsne_result = tsne_model.fit_transform(X) 

### Step 4: Project previous LDA topics on to the word2vec/t-SNE space.

num_category = 11
# The topic words for each LDA topic.
most_popular = [
["care","patient","time","great","alway","recommend","staff","year","offic","best","question","good","help","realli"],
["insur","pay","compani","cover","charg","cost","paid","pocket","price","offic","payment","medic","servic","amount","claim"],
["call", "appoint", "offic", "get", "back", "time", "phone", "week", "told", "hour", "schedul", "wait", "said", "ask"],
["dentist", "teeth", "procedur", "staff", "pain", "tooth", "go", "recommend", "need", "dental", "feel", "would", "experi", "root", "wisdom"],
["surgeri","knee","surgeon","mri","injuri","shoulder","orthoped","month","hand","perform","bone"],
["babi","son","daughter","husband","pregnanc","deliv","birth","kid","first","ob","hospit","old","year","deliveri"],
["allergi","test","shot","allergist","food","year","prick","sinu","scratch","sick","cat","eczema","spray","steroid"],
["skin","dermatologist","acn","face","prescrib","cream","want","tri","csi"],
["eye","surgeon","done","consult","result","lasik","post","vision","perform"],
["breast","reconstruct","hand","recoveri","heal","reduct","remov","bone","thumb","implant","grind","broheen"],
["botox","kidney","treatment","western","inject","urologist","urolog"]
]

x = []
y = []
n = []

for index1 in range(0, num_category):
    x.append([])
    y.append([])
    n.append([])
    for index2, item2 in enumerate(most_popular[index1]):
        try:
            index3 = all_words_unique_word.index(item2)
            x[index1].append(tsne_result[index3][0])
            y[index1].append(tsne_result[index3][1])
            n[index1].append(item2)
        except:
            pass

# Plot results.
fig, ax = plt.subplots(figsize=(3,3), dpi=150, facecolor="white")
ax.set_facecolor("white")
plt.style.use("fivethirtyeight")

for j in range(0, 3):
    for i, txt in enumerate(n[j]):
        ax.annotate(txt, (x[j][i],y[j][i]))
        
ax.scatter(x[0], y[0], label="Positive comments", color='#E74C3C')
ax.scatter(x[1], y[1], label="Payment", color='#8E44AD')
ax.scatter(x[2], y[2], label="Appointments & visits", color='#3498DB')
# ax.scatter(x[3], y[3], label="Dental care", color='#1ABC9C')
# ax.scatter(x[4], y[4], label="Surgery", color='#27AE60')
# ax.scatter(x[5], y[5], label="Women's health", color='#F1C40F')
# ax.scatter(x[6], y[6], label="Allergy treatments", color='#F39C12')
# ax.scatter(x[7], y[7], label="Skin procedures", color='#DC7633')
# ax.scatter(x[8], y[8], label="Eye care", color='#A6ACAF')
# ax.scatter(x[9], y[9], label="Reconstructive surgery", color='#5D6D7E')
# ax.scatter(x[10], y[10], label="Urology treatments", color='#000000')

frame1 = plt.gca()
frame1.axes.get_xaxis().set_visible(False)
frame1.axes.get_yaxis().set_visible(False)

# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# ax.legend()
