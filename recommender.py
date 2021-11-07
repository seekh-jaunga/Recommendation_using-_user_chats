# -*- coding: utf-8 -*-
"""Recommender.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11K1KKl9DHejDbE8S_gL-__B3iVRqzn_Y
"""

import numpy as np
import pandas as pd
import re

products = pd.read_csv('https://drive.google.com/uc?export=download&id=1-AT49daSBoy1oFNoy9g_n13rn3iJftF9')
#user_data = pd.read_csv('https://drive.google.com/uc?export=download&id=1-A6P1w_GXqc1y4jFwQ1dj1DhSs5E_QNg')
#pp = pd.read_csv('https://drive.google.com/uc?export=download&id=1p7qsdklDSyarH7jJc2B39VQObEzxN2jZ')
#pp_user = pd.read_csv('https://drive.google.com/uc?export=download&id=1-0W0V_YWNHRTHLuwM3TX4ZK3oUEfsAys')



#cutting down the date to reduce load
index_array = []
for i in range(1,1001):index_array.append(i)
products = products.sample(1000)
products = products.set_index(pd.Index(index_array))
user_data = products.sample(25)
pp = products[['product_category_tree','uniq_id','description']]
arr = []
for x in pp['product_category_tree']:
    y = re.sub(r"[\[\"\]>>,]", "",x)
    arr.append(y.lower())
pp['product_category_tree']=arr
pp_user = user_data[['product_category_tree','uniq_id','description']]
arr = []
for x in user_data['product_category_tree']:
    y = re.sub(r"[\[\"\]>>,]", "",x)
    arr.append(y.lower())
pp_user['product_category_tree']=arr
arr = ''
#data cut down and cleaned also


print('training starts')

from sklearn.feature_extraction.text import TfidfVectorizer
tfv = TfidfVectorizer(max_features=None,
                     strip_accents='unicode',
                     analyzer='word',
                     min_df=10,
                     token_pattern=r'\w{1,}',
                     ngram_range=(1,3),#take the combination of 1-3 different kind of words
                     stop_words='english')#removes all the unnecessary characters like the,in etc.

#fitting the description column.
tfv_matrix = tfv.fit_transform(products['description'].values.astype('U'))#converting everythinng to sparse matrix.

from sklearn.metrics.pairwise import sigmoid_kernel
sig = sigmoid_kernel(tfv_matrix,tfv_matrix)#how description of first product is related to first product and so on.

print('training completed')

indices = pd.Series(products.index,index=products['uniq_id']).drop_duplicates()

def product_recommendation(uniq_id,sig=sig):
    print(uniq_id)
    indx = indices[uniq_id]
    print('indx are ', indx)
    
    #getting pairwise similarity scores
    sig_scores = list(enumerate(sig[indx]))
    print(type(sig_scores))
    #sorting products
    sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
    
    #10 most similar products score
    sig_scores = sig_scores[1:11]
    
    #product indexes
    product_indices = [i[0] for i in sig_scores]
    
    #Top 10 most similar products
    return products['product_name'].iloc[product_indices]

def get_recommendations(prdct,specs):
  prdct = prdct.lower()
  for i in range(len(specs)):
    specs[i]=specs[i].lower()

  recs = []
  max_sim = 0
  uniq_id = 'null'

  for x,y,z in zip(pp_user['product_category_tree'],pp_user['uniq_id'],pp_user['description']):
    x_split = x.split()
    if x_split.count(prdct)>0:
      z_split = z.split()
      sims = 0
      for spec in specs:
        if z_split.count(spec)>0:
          sims+=1
      if sims >= max_sim:
        max_sim = sims
        uniq_id = y
            #temp = product_recommendation(y)
            #recs.append(temp)
  
  if uniq_id!='null':
        recs.append(product_recommendation(uniq_id))
     
  if len(recs)==0:
    print('user has never bought any product similar to it, so recommending by itself')
    for x,y,z in zip(pp_user['product_category_tree'],pp_user['uniq_id'],pp_user['description']):
      x_split = x.split()
      if x_split.count(prdct)>0:
        z_split = z.split()
        sims = 0
        for spec in specs:
          if z_split.count(spec)>0:
            sims+=1
        if sims >= max_sim:
            max_sim = sims
            uniq_id = y
    if uniq_id!='null':
        recs.append(product_recommendation(uniq_id))            
           
  print("\nTop Recommended products are: \n")
  return recs
  #print(product_recommendation(n).unique())

#sample product and specs for now
#prdct = 'pants'
#specs = ['black']

#get_recommendations(prdct,specs)

