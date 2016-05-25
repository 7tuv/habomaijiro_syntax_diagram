#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sys
import MeCab
from graph import *
from graph2gv import *

argvs = sys.argv
argc = len(argvs)

m = MeCab.Tagger("-Owakati")

graph = graph()
make_num = 0

raw_sentences = []


def set_default_sentences():
	raw_sentences.append("あいうえおかきくけこ")
	raw_sentences.append("あいうえおかきくけこあいうえおかきくけこあいうえおかきくけこ")
	raw_sentences.append("すもももももももものうち")
	raw_sentences.append("赤巻紙青巻紙黄巻紙")
	raw_sentences.append("カエルぴょこぴょこ三ぴょこぴょこ合わせてぴょこぴょこ六ぴょこぴょこ")
	raw_sentences.append("志布志市志布志町志布志志布志市役所志布志支所")
	raw_sentences.append("すもももももももものののののののののうち")
	# raw_sentences.append("朕惟フニ我カ皇祖皇宗國ヲ肇ムルコト宏遠ニ德ヲ樹ツルコト深厚ナリ\
	# 我カ臣民克ク忠ニ克ク孝ニ億兆心ヲ一ニシテ世世厥ノ美ヲ濟セルハ此レ我カ國體ノ精華ニシテ教育ノ淵源亦實ニ此ニ存ス\
	# 爾臣民父母ニ孝ニ兄弟ニ友ニ夫婦相和シ朋友相信シ恭儉己レヲ持シ博愛衆ニ及ホシ學ヲ\
	# 修メ業ヲ習ヒ以テ智能ヲ啓發シ德器ヲ成就シ進テ公益ヲ廣メ世務ヲ開キ常ニ國憲ヲ重シ國法ニ遵ヒ一旦緩急アレハ義勇公ニ奉シ以テ天壤無\
	# 窮ノ皇運ヲ扶翼スヘシ是ノ如キハ獨リ朕カ忠良ノ臣民タルノミナラス又以テ爾祖先ノ遺風ヲ顯彰スルニ足ラン\
	# 斯ノ道ハ實ニ我カ皇祖皇宗ノ遺訓ニシテ子孫臣民ノ倶ニ遵守スヘキ所\
	# 之ヲ古今ニ通シテ謬ラス之ヲ中外ニ施シテ悖ラス朕爾臣民ト倶ニ拳々服膺シテ咸其德ヲ一ニセンコトヲ庶幾フ")

	# raw_sentences.append("")


def text2list(text):		# MeCabにより文章を単語に分割
	tmp = m.parse(text)
	# tmp = m.parseNBest(text)
	return tmp.split()


def open_text(txt_name):	# "\n\n"でsentenceを区切る
	raw_sentence = []
	with open(txt_name, "r", encoding="UTF-8") as f:
		data1 = f.read()
		data2 = data1.split("\n\n")
		raw_sentence = [d.replace("\n", "").replace("\ufeff", "") for d in data2]
		# print(raw_sentence)
	return raw_sentence


def gen_n_markov_chain(text, n):
	if n <= 0:
		print("Error, n <= 0: n =", n,)
		return
	elif n > len(text):
		print("Error, too much: n =", n,)
		return
	# graph.set_init_terms(("0Start",) + tuple(text[: n - 1]))
	graph.set_edge(("0Start",) + tuple(text[0: n - 1]), tuple(text[0: n]), 1, text[n - 1])		# 開始地点: 0Start
	graph.set_node(("0Start",) + tuple(text[0: n - 1]))		# db_r[初期ノード]作成のため
	[graph.set_edge(tuple(text[i: i + n])
					, tuple(text[i + 1: i + n + 1])
					, 1
					, text[i + n]) for i in range(len(text) - n)]		#n階マルコフ連鎖
	if n == 1:		# 終了地点: End1
		graph.set_edge((text[-1],), ("End1",), 1, "End1")
		graph.set_node(("End1",))		# db[最終ノード]作成のため
	else:
		graph.set_edge(tuple(text[-n:]), tuple(text[1 - n:] + ["End1"]), 1, "End1")
		graph.set_node(tuple(text[1 - n:] + ["End1"]))


def chain_contraction_serial(n):		# 深さ方向に関する単一な連鎖の縮約（自己破壊的に）
	is_contracted = True
	while is_contracted is True:
		is_contracted = False
		iter_db = list(graph.db)
		for term1 in iter_db:		# for の中で一度も縮約が行われなかったら while から出る
			# print(term1)
			if term1 in graph.db and term1[0] != "0Start" and len(graph.db[term1]) == 1:
				term2 = graph.db[term1][0]
				# print(term2)
				if term2[-1] != "End1" and len(graph.db_r[term2]) == 1:
					if graph.is_linear_node(term2, n - 1):
						chain_contraction_serial_(term1, term2, n)
						is_contracted = True
						# break


def chain_contraction_serial_(term1, term2, n):
	new_t1 = term1[-1]
	new_t2 = term2[-1]
	if isinstance(new_t1, tuple):
		new_t1 = str(new_t1)
	if isinstance(new_t2, tuple):
		new_t2 = str(new_t2)
	new_term = term1[:-1] + (new_t1 + new_t2,)		# n == 1 のときは (term1[0] + term2[0],) と同値
	# print(term1, term2, "->", new_term)

	graph.change_node(term1, new_term)
	n_terms = graph.db[term2]
	[graph.set_edge(new_term, n_term, graph.chain_weights[term2, n_term], n_term[-1]) for n_term in n_terms]
	if n > 1:
		tree = graph.get_tree(term2, n - 1)
		# print(tree)
		[graph.change_tree(n_tree, new_term, 1) for n_tree in tree]
		# graph.change_tree(tree, new_term, 1)
	graph.remove_node(term2)

	# print("graph.db:", graph.db, "\n")
	# print("graph.db_r:", graph.db_r, "\n")
	# print("graph.chain_weights:", graph.chain_weights, "\n")


def chain_contraction_parallel(n):		# 幅方向に関する平行した連鎖の縮約（自己破壊的に）
	is_contracted = True
	while is_contracted is True:
		is_contracted = False
		iter_db = list(graph.db)
		for term in iter_db:		# for の中で一度も縮約が行われなかったら while から出る
			if term in graph.db and len(graph.db[term]) > 1:
				n_terms = graph.db[term]
				# print(n_terms)
				is_contracted2 = False
				for i in range(len(n_terms) - 1):
					if len(graph.db[n_terms[i]]) == 0 or graph.is_linear_node(n_terms[i], n - 1) == False:
						continue		# End が含まれている or rootが一つでない
					meet_nodes_i = get_n_depth_node([n_terms[i]], n)
					for j in range(i + 1, len(n_terms)):
						if len(graph.db[n_terms[j]]) == 0 or graph.is_linear_node(n_terms[j], n - 1) == False:
							continue		# End が含まれている or rootが一つでない
						meet_nodes_j = get_n_depth_node([n_terms[j]], n)
						if set(meet_nodes_i) == set(meet_nodes_j):
							chain_contraction_parallel_(n_terms[i], n_terms[j], n)
							print("gets to", set(meet_nodes_i))
							is_contracted = True
							is_contracted2 = True
							break
					if is_contracted2:
						break


def get_n_depth_node(nodes, n):
	result = []
	[result.extend(graph.db[node]) for node in nodes]
	if n <= 1:
		return result
	else:
		return get_n_depth_node(result, n - 1)


def chain_contraction_parallel_(term1, term2, n):
	new_t1 = term1[-1]
	new_t2 = term2[-1]
	if isinstance(new_t1, str):
		new_t1 = (new_t1,)
	if isinstance(new_t2, str):
		new_t2 = (new_t2,)
	new_term = term1[:-1] + (new_t1 + new_t2,)
	print(term1, term2, "->", new_term)

	graph.change_node(term1, new_term)
	n_terms = graph.db[new_term]
	if n > 1:
		trees1 = graph.get_tree(new_term, n - 1)
		# print(trees1)
		[graph.change_tree(n_tree, new_term, 1) for n_tree in trees1]
		# graph.change_tree(tree, new_term, 1)

	if n > 1:
		trees2 = graph.get_tree(term2, n - 1)
		# print(trees2)
		[graph.remove_tree(n_tree, n - 2) for n_tree in trees2]
	graph.remove_node(term2)

	# if n > 1:
	# 	tree = graph.get_tree(term2, n - 1)
	# 	# print(tree)
	# 	[graph.change_tree(n_tree, new_term, 1) for n_tree in tree]
	# 	# graph.change_tree(tree, new_term, 1)
	# graph.remove_node(term2)

	# print("graph.db:", graph.db, "\n")
	# print("graph.db_r:", graph.db_r, "\n")
	# print("graph.chain_weights:", graph.chain_weights, "\n")


def gen_graphviz(filename):
	global make_num
	print("wait...")
	makegv(graph.chain_weights, graph.chain_labels, terms, N
			, filename + str(make_num) + "_N" + str(N), "dot")
	print(filename + str(make_num) + ".gv was generated." )
	make_num += 1


def gen_random_sentense1():
	# unbiased_init_terms = list(set(graph.init_terms))
	unbiased_init_terms = [x for x in graph.db if x[0] == "0Start"]
	w = unbiased_init_terms[random.randint(0, len(unbiased_init_terms) - 1)]
	[print(x, end="") for x in w[1:]]
	while 1:
		n_w = graph.db[w]
		w = n_w[random.randint(0, len(n_w) - 1)]
		if w[-1] == "End1":
			break
		try:
			if isinstance(w[-1], tuple):
				print(w[-1][random.randint(0, len(w[-1]) - 1)], end="")
				# print(w[-1], end="")
			else:
				print(w[-1], end="")
		except UnicodeEncodeError:
			print("\nエンコードエラー", end="")
	print("\n")


def gen_random_sentense(n):
	print("ランダム文章生成")
	[gen_random_sentense1() for x in range(n)]


if __name__ == "__main__":
	N = 1
	txts = []
	if argc == 1:
		set_default_sentences()
	elif argc == 2:
		N = int(argvs[1])
		set_default_sentences()
	elif argc > 2:
		N = int(argvs[1])
		txts = argvs[2:]
		for txt in txts:
			raw_sentences.extend(open_text(txt))		# Flatten
	# print("raw_sentences", raw_sentences, "\n")

	sentences = []
	simplified_sentences = []
	terms = []
	[sentences.append(text2list(x)) for x in raw_sentences]

	simplified_sentences = [list(set(s)) for s in sentences]

	tmp = []
	[tmp.extend(sentence) for sentence in simplified_sentences]		# Flatten
	terms = list(set(tmp))
	# print("terms :", terms, "\n")

	[gen_n_markov_chain(text, N) for text in sentences]		# n階マルコフ連鎖
	# graph.print_elem()



	###########################################################
	########################  Outputs #########################
	###########################################################
	print("chain_num: ", sum(graph.chain_weights.values()), "\n")
	gen_graphviz("output")

	chain_contraction_serial(N)		# 連鎖の縮約
	print("chain_num: ", sum(graph.chain_weights.values()), "\n")
	gen_graphviz("output")		# ファイル出力

	chain_contraction_parallel(N)		# 連鎖の縮約
	print("chain_num: ", sum(graph.chain_weights.values()), "\n")
	gen_graphviz("output")		# ファイル出力

	gen_random_sentense(10)

	# N階マルコフ連鎖に対するグラフの縮約を実装した
