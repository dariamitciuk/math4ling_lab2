"""Построить граф связей слов, в котором слово представляет собой вершину, 
а взвешенная дуга показывает сколько раз слово в первой вершине упоминалось 
после слова во второй вершине в окне размера N. Найти все пары слов, для которых
наблюдается несоблюдение симметрии в M раз 
(отношение частоты дуги 1->2 к частоте дуги 2->1 больше М)."""

import nltk
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from string import punctuation

import matplotlib.pyplot as plt
import networkx as nx
import math
import numpy as np

import random 

def text_extractor(filename, window):
    """Возвращает строку из слов без посторонних символов и без заглавных букв
    со всеми новостями в случайном окне размера window
    """
    result = []
    with open(filename, encoding="utf-8") as f:
        text = f.readlines()
    start = random.randint(0, len(text) - window)
    for line in text[start:start + window]:
    
        if len(line) < 100: # Не текст новости
            pass
        else:
            # Создаёт файл с исследуемым фрагментом новостей
            with open("part_of_news.txt", "a", encoding="utf-8") as n:
                n.write(line + "\n")
            line = [w.lower() for w in word_tokenize(line) if w.isalpha()]
            result.append(" ".join(line))
    text = " ".join(result)
    
    return text


def bigrams(text):
    """Создаёт частотный словарь биграмм"""

    bigrams_dict = {}
    tokens = word_tokenize(text)
    all_bigrams = ngrams(tokens, 2)

    for bigram in all_bigrams:
        if bigram not in bigrams_dict:
            bigrams_dict[bigram] = 1
        else:
            bigrams_dict[bigram] += 1

    return bigrams_dict

def dict_for_graph(dict_of_bigrams):
    """Возвращает словарь, ключи которого - слова, значения - словари, ключи которых - 
    слова, которые могут идти после него, значения - число таких вхождений
    """

    final_dict = {}

    for bigram, number in dict_of_bigrams.items():
        word = bigram[0]
        if not word in final_dict:
            final_dict[word] = {}
            final_dict[word].update({bigram[1]:number})
        else:
            final_dict[word].update({bigram[1]:number})

    return final_dict


def to_graph(data_dict):
    """Создаёт ориентированный граф, в котором значение ребра показывает,
    число упоминаний слова в первой вершине после слова во второй вершине
    """
    G = nx.MultiDiGraph() 
    for n in data_dict.keys():
        for n2 in data_dict[n].keys():
            # Меняем местами, т.к. в словаре число показывает, сколько раз
            # второе слово шло после первого
            G.add_edge(n2, n, weight=data_dict[n][n2])  
    return G

def diff_proportions(G): 
    """Возвращает словарь, где биграммамам, слова в которых встречались как в одном,
    так и в другом порядке, соответствует отношение количества вхождений более частотного 
    варианта биграммы к менее частотному, а в остальных случаях биграммам соответствует ноль
    """
    diff_dict = {}
    # Идём по соседям в графе и смотрим на значения дуг, которые их соединяют
    for n, nbrsdict in G.adjacency():
        for nbr, keydict in nbrsdict.items():
            for _, eattr in keydict.items():
                for _, weight in eattr.items():
                    # Добавляем данные о частоте биграммы в словарь
                    diff_dict[(n, nbr)] = weight

    # Если зеркальная биграмма существует, то меняем значение на отношение числа
    # вхождений варианта с более частотным порядком к меньшему
    for bigram, freq in diff_dict.items():
        mirror = (bigram[1], bigram[0])
        if mirror in diff_dict and freq != 0:
            diff_dict[bigram] = int(max(freq, diff_dict[mirror]) / \
                                min(freq, diff_dict[mirror]))
            diff_dict[mirror] = 0 # Зеркальный вариант нам больше не интересен
        else:
            diff_dict[bigram] = 0

    return diff_dict

def drawing(G, data_dict, colors='b', layout='spring'):
    """Рисует граф в файл graph.png"""

    if layout=='kawai':
        pstn=nx.kamada_kawai_layout(G)
    elif layout=='circle':
        pstn=nx.drawing.layout.circular_layout(G)
    elif layout=='random':
        pstn=nx.drawing.layout.random_layout(G)
    else:
        pstn=nx.spring_layout(G)

    nx.draw(G, pos=pstn, node_color=colors, edge_color='g', with_labels=True)
    plt.savefig("graph.png")

def main(window=1000, M=100):
    """Создаёт граф и выводит биграммы с параментом M большим выбранного значения;
    window - количество строк, с которыми работаем, M - нижняя граница значения
    отношения частоты биграммы к частоте обратной у ей биграммы
    """

    filename = "news.txt"
    text = text_extractor(filename, window)
    dict_of_bigrams = bigrams(text)
    data_for_graph = dict_for_graph(dict_of_bigrams)
    G1 = to_graph(data_for_graph)
    proportions = diff_proportions(G1)

    for bigram, proportion in proportions.items():
        if proportion > M:
            print(bigram[0] + " " + bigram[1])
    drawing(G1, data_for_graph)

if __name__ == "__main__":
    main(1000, 3) # Исследуем 10 строк, ищем биграммы с параметром M > 3