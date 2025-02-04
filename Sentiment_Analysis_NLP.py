
# coding: utf-8

# In[30]:


import pandas as pd  
train = pd.read_csv("D:\projects\Sentiment_Analysis_NLP(bag_of_words)\labeledTrainData.tsv", header=0, delimiter="\t", quoting=3)


# In[31]:


train.shape
train.columns.values


# In[32]:


print (train["review"][0])


# In[33]:


from bs4 import BeautifulSoup     
example1 = BeautifulSoup(train["review"][0], "html5lib")
print (train["review"][0])
print (example1.get_text())


# In[34]:


import re
letters_only = re.sub("[^a-zA-Z]",           # The pattern to search for
                      " ",                   # The pattern to replace it with
                      example1.get_text() )  # The text to search
print (letters_only)
lower_case = letters_only.lower() 
words = lower_case.split() 


# In[35]:


import nltk
from nltk.corpus import stopwords
print (stopwords.words("english") )
words = [w for w in words if not w in stopwords.words("english")]
print (words)


# In[36]:


def review_to_words( raw_review ):
    # Function to convert a raw review to a string of words
    # The input is a single string (a raw movie review), and 
    # the output is a single string (a preprocessed movie review)
    #
    # 1. Remove HTML
    review_text = BeautifulSoup(raw_review, "html5lib").get_text() 
    #
    # 2. Remove non-letters        
    letters_only = re.sub("[^a-zA-Z]", " ", review_text) 
    #
    # 3. Convert to lower case, split into individual words
    words = letters_only.lower().split()                             
    #
    # 4. In Python, searching a set is much faster than searching
    #   a list, so convert the stop words to a set
    stops = set(stopwords.words("english"))                  
    # 
    # 5. Remove stop words
    meaningful_words = [w for w in words if not w in stops]   
    #
    # 6. Join the words back into one string separated by space, 
    # and return the result.
    return( " ".join( meaningful_words ))  


# In[37]:


clean_review = review_to_words( train["review"][0] )
print (clean_review)
num_reviews = train["review"].size
clean_train_reviews = []

for i in range( 0, num_reviews ):
    clean_train_reviews.append( review_to_words( train["review"][i] ) )

print ("Cleaning and parsing the training set movie reviews...\n")
clean_train_reviews = []

for i in range( 0, num_reviews ):
    if( (i+1)%1000 == 0 ):
        print ("Review %d of %d\n" % ( i+1, num_reviews )  )                                                                  
    clean_train_reviews.append( review_to_words( train["review"][i] ))


# In[38]:


print ("Creating the bag of words...\n")
from sklearn.feature_extraction.text import CountVectorizer

# Initialize the "CountVectorizer" object, which is scikit-learn's
# bag of words tool.  
vectorizer = CountVectorizer(analyzer = "word",                                tokenizer = None,                                 preprocessor = None,                              stop_words = None,                                max_features = 1000) 

# fit_transform() does two functions: First, it fits the model
# and learns the vocabulary; second, it transforms our training data
# into feature vectors. The input to fit_transform should be a list of 
# strings.
train_data_features = vectorizer.fit_transform(clean_train_reviews)

# Numpy arrays are easy to work with, so convert the result to an 
# array
train_data_features = train_data_features.toarray()
print (train_data_features.shape)


# In[39]:


# Take a look at the words in the vocabulary
vocab = vectorizer.get_feature_names()
print (vocab)


# In[40]:


import numpy as np
# Sum up the counts of each vocabulary word
dist = np.sum(train_data_features, axis=0)
# For each, print the vocabulary word and the number of times it 
# appears in the training set
for tag,count in zip(vocab, dist):
	print (count, tag)


# In[41]:


print ("Training the random forest...")
from sklearn.ensemble import RandomForestClassifier

# Initialize a Random Forest classifier with 100 trees
forest = RandomForestClassifier(n_estimators = 100) 

# Fit the forest to the training set, using the bag of words as 
# features and the sentiment labels as the response variable
#
# This may take a few minutes to run
forest = forest.fit( train_data_features, train["sentiment"] )


# In[42]:


# Read the test data
test = pd.read_csv("D:\projects\Sentiment_Analysis_NLP(bag_of_words)\labeledTrainData.tsv", header=0, delimiter="\t", quoting=3)

# Verify that there are 25,000 rows and 2 columns
print (test.shape)

# Create an empty list and append the clean reviews one by one
num_reviews = len(test["review"])
clean_test_reviews = [] 

print ("Cleaning and parsing the test set movie reviews...\n")
for i in range(0,num_reviews):
    if( (i+1) % 1000 == 0 ):
        print ("Review %d of %d\n" % (i+1, num_reviews))
    clean_review = review_to_words( test["review"][i] )
    clean_test_reviews.append( clean_review )

# Get a bag of words for the test set, and convert to a numpy array
test_data_features = vectorizer.transform(clean_test_reviews)
test_data_features = test_data_features.toarray()

# Use the random forest to make sentiment label predictions
result = forest.predict(test_data_features)

# Copy the results to a pandas dataframe with an "id" column and
# a "sentiment" column
output = pd.DataFrame( data={"id":test["id"], "sentiment":result} )

# Use pandas to write the comma-separated output file
output.to_csv( "D:\projects\Sentiment_Analysis_NLP(bag_of_words)\Bag_of_Words_model.csv", index=False, quoting=3 )

