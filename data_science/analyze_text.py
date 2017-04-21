"""
analyze_text.py
Created by Kenneth Potts
April 20, 2017
"""

import numpy as np
import nltk
from nltk import ngrams


def analyze(sents, word_dict={}, grams_dict={}, n=2, n_gram_frequency=3, sort_n_grams=False):
    """
    calculates statistics based on word counts, sentence counts, word frequencies, and n-gram frequencies
    
    :param sents: (list) list of sentences
    :param word_dict: (optional) empty dictionary
    :param grams_dict: (optional) empty dictionary
    :param n: (int) n for n-grams, number of consecutive words to be considered
    :param n_gram_frequency: (int) frequency cut-off for n-grams
    :param sort_n_grams: option to sort the returned n-grams based on frequency, expensive, False recommended
    :return: total_num_words, num_unique_words, num_sentences, avg_sentence_length, \
           common_ngrams, counts_for_common_ngrams, sorted_words
    """
    num_sents = len(sents)
    sent_lengths = np.zeros(len(sents))

    for i in range(num_sents):
        sent = sents[i].lower()  # lowercase
        sent = sent.strip()  # remove special chars
        word_list = sent.split(' ')  # break into words
        sent_lengths[i] = len(word_list)
        try:
            grams = ngrams(word_list, n)
        except Exception:
            nltk.download('punkt')  # a corpus needed to run ngrams
            grams = ngrams(word_list, n)  # saves a few lines of code
        for gram in grams:
            if gram in grams_dict:
                grams_dict[gram] += 1
            else:
                grams_dict[gram] = 1
        for word in word_list:
            if word in word_dict:
                word_dict[word] += 1
            else:
                word_dict[word] = 1

    # for words
    unique_words = np.array(list(word_dict.keys()))
    word_counts = np.array(list(word_dict.values()))
    num_unique_words = unique_words.shape[0]
    total_num_words = word_counts.sum()
    sorted_idx = np.argsort(word_counts)[::-1]  # argsort largest to smallest
    sorted_words = unique_words[sorted_idx]

    # for sentences
    unique_ngrams = np.array(list(grams_dict.keys()))
    ngrams_count = np.array(list(grams_dict.values()))
    num_unique_ngrams = unique_ngrams.shape[0]
    # total_num_ngrams = ngrams_count.sum()

    if sort_n_grams:
        sorted_idx_ngrams = np.argsort(ngrams_count)[::-1]  # argsort largest to smallest
        unique_ngrams = unique_words[sorted_idx_ngrams]
        ngrams_count = ngrams_count[sorted_idx_ngrams]

    ngrams_count_bools = ngrams_count >= n_gram_frequency # where the common ngrams are
    idx_common_ngrams = np.arange(ngrams_count.shape[0])[ngrams_count_bools] # get indices
    count_common_ngrams = ngrams_count[ngrams_count_bools]
    common_ngrams = unique_ngrams[idx_common_ngrams]

    avg_sent_length = np.mean(sent_lengths)

    return total_num_words, num_unique_words, num_sents, avg_sent_length,\
           common_ngrams, count_common_ngrams, sorted_words


def analyze_file(file, n=2, n_gram_frequency=3, print_stats=True, sort_n_grams=False):
    """
    calculates statistics based on word counts, sentence counts, word frequencies, and n-gram frequencies

    :param file: file object or file path string, txt file
    :param n: (int) n for n-grams, number of consecutive words to be considered
    :param n_gram_frequency: (int) frequency cut-off for n-grams
    :param print_stats: True for print out of stats
    :param sort_n_grams: option to sort the returned n-grams based on frequency, expensive, False recommended
    :return: total_num_words, num_unique_words, num_sentences, avg_sentence_length, \
           common_ngrams, counts_for_common_ngrams, sorted_words
    """
    text = ''
    if type(file) == str:
        file = open(file, 'r')
        text = file.read()
    else:
        try:
            text = file.read()
        except Exception:
            raise TypeError('File type not yet supported')
    text = text.replace('\n', ' ')  # \n of no interest to me!
    sents = nltk.tokenize.sent_tokenize(text)

    word_dict = {}
    grams_dict = {}

    total_num_words, num_unique_words, num_sents, avg_sent_length, common_ngrams, count_common_ngrams, sorted_words = \
        analyze(sents, word_dict=word_dict, grams_dict=grams_dict, n=n,
                n_gram_frequency=n_gram_frequency, sort_n_grams=sort_n_grams)

    if print_stats:
        print("======STATS======")
        print("Total word count: {}".format(total_num_words))
        print("The count of unique words: {}".format(num_unique_words))
        print("Number of sentences: {}".format(num_sents))
        print("Total word count: {}".format(total_num_words))
        print("Average sentence length in words: {}".format(avg_sent_length))
        print("5 common {}-grams, used more than {} times:".format(n, n_gram_frequency))
        for i in range(5):
            print(common_ngrams[i])
        print("See returned values for more")
        print("5 most common words:")
        for i in range(5):
            print(sorted_words[i])
        print("See returned values for more")

    return total_num_words, num_unique_words, num_sents, avg_sent_length,\
           common_ngrams, count_common_ngrams, sorted_words


if __name__ == '__main__':
    file_path = "data/MobyCh1.txt"  # put file path here
    analyze_file(file_path)
