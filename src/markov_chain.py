#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import sys
import MeCab
from graph import *
from graph2gv import *

argvs = sys.argv
argc = len(argvs)


def set_sentences(txts):
	'''
	txts から文章を読み込む．
	'''
	sentences = []
	if txts is not None:
		[sentences.extend(open_text(txt)) for txt in txts]		# Flatten
	else:
		sentences.append("あいうえおかきくけこ")
		sentences.append("あいうえおかきくけこあいうえおかきくけこあいうえおかきくけこ")
		sentences.append("すもももももももものうち")
		sentences.append("赤巻紙青巻紙黄巻紙")
		sentences.append("カエルぴょこぴょこ三ぴょこぴょこ合わせてぴょこぴょこ六ぴょこぴょこ")
		sentences.append("志布志市志布志町志布志志布志市役所志布志支所")
		sentences.append("すもももももももものののののののののうち")
	# print("raw_sentences", sentences, "\n")

	m = MeCab.Tagger("-Owakati")
	sentences = [m.parse(x).split() for x in sentences]
	return sentences


def open_text(txt_name):
	'''
	"\n\n"の区切りごとに txt_name 内の文章をリストに入れる．
	'''
	sentences = []
	with open(txt_name, "r", encoding="UTF-8") as f:
		sentences = f.read().split("\n\n")
		sentences = [s.replace("\n", "").replace("\ufeff", "") for s in sentences]
		# print(sentences)
	return sentences


def gen_n_markov_chain(sent, n, graph):
	'''
	分かち書きされた文章 sent から n 階マルコフ連鎖を生成する．
	'''
	if n <= 0:
		print("Error, n <= 0: n =", n,)
		return
	elif n > len(sent):
		print("Error, too much: n =", n,)
		return
	# graph.set_init_terms(("0Start",) + tuple(sent[: n - 1]))
	graph.set_edge(("0Start",) + tuple(sent[0: n - 1]), tuple(sent[0: n]), 1, sent[n - 1])		# 開始地点: 0Start
	[graph.set_edge(tuple(sent[i: i + n])
					, tuple(sent[i + 1: i + n + 1])
					, 1
					, sent[i + n]) for i in range(len(sent) - n)]		#n階マルコフ連鎖
	if n == 1:		# 終了地点: End1
		graph.set_edge((sent[-1],), ("End1",), 1, "End1")
	else:
		graph.set_edge(tuple(sent[-n:]), tuple(sent[1 - n:] + ["End1"]), 1, "End1")


def chain_contraction_serial(n, graph):
	'''
	# n 階マルコフ連鎖モデルの graph に対する直列方向の縮約を行う．
	'''
	is_contracted = True
	while is_contracted is True:
		is_contracted = False
		iter_db = list(graph.G.nodes())
		for term1 in iter_db:		# for の中で一度も縮約が行われなかったら while から出る
			# print(term1)
			if term1 in graph.G.nodes() and term1[0] != "0Start" and len(graph.G.successors(term1)) == 1:
				term2 = graph.G.successors(term1)[0]
				# print(term2)
				if term2[-1] != "End1" and len(graph.G.predecessors(term2)) == 1:
					if graph.is_linear_node(term2, n - 1):
						combine_serial_nodes(term1, term2, n, graph)
						is_contracted = True
						# break


def combine_serial_nodes(term1, term2, n, graph):
	''' 直列したノード(term1, term2)を結合する '''
	new_t1 = term1[-1]
	new_t2 = term2[-1]
	if isinstance(new_t1, tuple):
		new_t1 = str(new_t1)
	if isinstance(new_t2, tuple):
		new_t2 = str(new_t2)
	new_term = term1[:-1] + (new_t1 + new_t2,)		# n == 1 のときは (term1[0] + term2[0],) と同値
	# print(term1, term2, "->", new_term)

	graph.change_node(term1, new_term)
	n_terms = graph.G.successors(term2)
	[graph.set_edge(new_term, n_term, graph.G[term2][n_term]["weight"], n_term[-1]) for n_term in n_terms]
	if n > 1:
		tree = graph.get_tree(term2, n - 1)
		# print(tree)
		[graph.change_tree(n_tree, new_term, 1) for n_tree in tree]
		# graph.change_tree(tree, new_term, 1)
	graph.remove_node(term2)


def chain_contraction_parallel(n, graph):
	'''
	# n 階マルコフ連鎖モデルの graph に対する並列方向の縮約を行う．
	'''
	is_contracted = True
	while is_contracted is True:
		is_contracted = False		# graph 内のノード同士で結合が行われたか
		iter_db = list(graph.G.nodes())
		for term in iter_db:		# for の中で一度も縮約が行われなかったら while から出る
			if term in graph.G.nodes() and len(graph.G.successors(term)) > 1:
				n_terms = graph.G.successors(term)
				is_contracted2 = False		# n_terms　内のノード同士で結合が行われたか
				for i in range(len(n_terms) - 1):
					if graph.is_linear_node(n_terms[i], n - 1) == False:
						continue		# End が含まれている or 戻り先が一つでない
					for j in range(i + 1, len(n_terms)):
						if graph.is_linear_node(n_terms[j], n - 1) == False:
							continue		# End が含まれている or 戻り先が一つでない

						term1 = n_terms[i]
						term2 = n_terms[j]
						p_n_terms_i = graph.G.predecessors(term1)
						p_n_terms_j = graph.G.predecessors(term2)
						terminal_terms_i = graph.get_tree_terminal(term1, n)
						terminal_terms_j = graph.get_tree_terminal(term2, n)
						# #
						# print(term, "to", term1, term2)
						# print(term1, "'s root:", p_n_terms_i)
						# print(term2, "'s root:", p_n_terms_j)
						# print("terminal nodes of i:", terminal_terms_i)
						# print("terminal nodes of j:", terminal_terms_j)
						# #
						if set(p_n_terms_i) == set(p_n_terms_j) \
							and (len(set(terminal_terms_i)) > 0 or term1[-1] == term2[-1]) \
							and set(terminal_terms_i) == set(terminal_terms_j) \
							and graph.is_linear_node(term1, n - 1) \
							and graph.is_linear_node(term2, n - 1):
							combine_parallel_nodes(term1, term2, n, graph)
							is_contracted = True
							is_contracted2 = True
							break
					if is_contracted2:
						break


def combine_parallel_nodes(term1, term2, n, graph):
	''' 並列したノード(term1, term2)を結合する '''
	new_t1 = term1[-1]
	new_t2 = term2[-1]
	if isinstance(new_t1, str):
		new_t1 = (new_t1,)
	if isinstance(new_t2, str):
		new_t2 = (new_t2,)
	new_term = term1[:-1] + (tuple(sorted(new_t1 + new_t2,)),)
	# print(term1, term2, "->", new_term)

	if n > 1:
		tree1 = graph.get_tree(term1, n - 1)
		[graph.change_tree(n_tree, new_term, 1) for n_tree in tree1]
		tree2 = graph.get_tree(term2, n - 1)
		[graph.change_tree(n_tree, new_term, 1) for n_tree in tree2]

	graph.change_node(term2, term1)
	graph.change_node(term1, new_term)


def print_params():
	print("nodes   :", len(graph.G.nodes()))
	print("edges   :", len(graph.G.edges()))
	print("weights :", sum([graph.G[e[0]][e[1]]["weight"] for e in graph.G.edges()]))


def gen_graphviz(name, graph):
	'''
	graphviz を用いて graph を name.pdf（画像）, name.gv（dot言語ファイル） として出力する
	'''
	print("wait...")
	chain_weights = {}
	chain_labels = {}
	for e in graph.G.edges(data=True):
		chain_weights[e[:2]] = e[2]["weight"]
		chain_labels[e[:2]] = e[2]["label"]
	makegv(chain_weights, chain_labels, name, "dot")
	print(name + ".gv was generated.\n")


def gen_random_sentense1(unbiased_init_terms, graph):
	w = unbiased_init_terms[random.randint(0, len(unbiased_init_terms) - 1)]
	[print(x, end="") for x in w[1:]]
	while 1:
		n_w = graph.G.successors(w)
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


def gen_random_sentense(n, graph):
	print("ランダム文章生成:\n")
	# unbiased_init_terms = list(set(graph.init_terms))
	unbiased_init_terms = [x for x in graph.G.nodes() if x[0] == "0Start"]

	[gen_random_sentense1(unbiased_init_terms, graph) for x in range(n)]


if __name__ == "__main__":
	N = 1
	txts = None
	graph = graph()

	if argc == 1:
		pass
	elif argc == 2:
		N = int(argvs[1])
	elif argc > 2:
		N = int(argvs[1])
		txts = argvs[2:]

	sentences = set_sentences(txts)
	[gen_n_markov_chain(s, N, graph) for s in sentences]		# n階マルコフ連鎖
	# graph.print_elem()

	###########################################################
	########################  Outputs #########################
	###########################################################
	print_params()
	gen_graphviz("output0_N" + str(N), graph)		# ファイル出力

	chain_contraction_serial(N, graph)		# 直列方向の縮約
	print_params()
	gen_graphviz("output1_N" + str(N), graph)		# ファイル出力

	chain_contraction_parallel(N, graph)		# 並列方向の縮約
	print_params()
	gen_graphviz("output2_N" + str(N), graph)		# ファイル出力

	chain_contraction_serial(N, graph)		# 直列方向の縮約
	print_params()
	gen_graphviz("output3_N" + str(N), graph)		# ファイル出力

	chain_contraction_parallel(N, graph)		# 並列方向の縮約
	print_params()
	gen_graphviz("output4_N" + str(N), graph)		# ファイル出力

	gen_random_sentense(10, graph)		# ランダムな文章を生成
