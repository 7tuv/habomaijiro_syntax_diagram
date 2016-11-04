#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx

class graph:
	def __init__(self):
		self.G = nx.DiGraph()
		self.init_terms = []

	def print_elem(self):
		print(self.G.node())
		print(self.G.reverse())

		chain_weights = {}
		chain_labels = {}
		for e in self.G.edges(data=True):
			chain_weights[e[:2]] = e[2]["weight"]
			chain_labels[e[:2]] = e[2]["label"]
		print(chain_weights)
		print(chain_labels)

		print(self.init_terms)

	def set_init_terms(self, term):
		self.init_terms.append(tuple(term))

	def set_node(self, term):
		''' 新しいノードを加える '''
		self.G.add_node(term)

	def set_edge(self, source, target, weight, label=""):
		''' 新しいエッジを加える '''
		if self.G.has_edge(source, target):
			self.G[source][target]["weight"] += weight
			self.G[source][target]["label"] += label
		else:
			self.G.add_edge(source, target)
			self.G[source][target]["weight"] = weight
			self.G[source][target]["label"] = label

	def remove_node(self, term):
		''' ノードをを削除する '''
		self.G.remove_node(term)

	def remove_edge(self, term, n_term):
		''' エッジを削除する '''
		self.G.remove_edge(term, n_term)

	def change_node(self, term, new_term):
		''' ノード term を new_term に変更する '''
		n_terms = self.G.successors(term)
		p_terms = self.G.predecessors(term)
		# print(term)
		# print(p_terms)
		# print(n_terms)

		[self.set_edge(new_term, n_term, self.G[term][n_term]["weight"], n_term[-1]) for n_term in n_terms]
		[self.set_edge(p_term, new_term, self.G[p_term][term]["weight"], new_term[-1]) for p_term in p_terms]
		self.remove_node(term)
		# self.print_elem()

	def is_linear_node(self, term, n):
		'''
		ノード term より n 個遷移先の全てのノードから，分岐なしにノード term まで遡れるとき True を返す．
		'''
		if n == 0:		# 深さ 0 の時は無条件で True
			return True
		elif term not in self.G.nodes():
			return True
		n_terms = self.G.successors(term)
		value = all([len(self.G.predecessors(n_term)) == 1 for n_term in n_terms])
		if n == 1:
			return value
		else:
			return value and all([self.is_linear_node(n_term, n - 1) for n_term in n_terms])

	def get_tree(self, term, n):
		'''
		ノード term から深さ n までの遷移先の木を取得する．
		structure ::= [term, [structure(==n_term)]]
		'''
		n_terms = self.G.successors(term)
		if n <= 1:
			return n_terms[:]		# 深いコピー
		else:
			return [[n_term, (self.get_tree(n_term, n - 1))] for n_term in n_terms]

	def get_tree_terminal(self, term, n):
		'''
		ノード term から深さ n の遷移先の末端ノードを取得する．
		structure ::= [term, [structure(==n_term)]]
		'''
		n_terms = self.G.successors(term)
		if n <= 1:
			return n_terms[:]		# 深いコピー
		else:
			tmp = []
			tmp.extend([self.get_tree_terminal(n_term, n - 1) for n_term in n_terms])
			result = []
			[result.extend(x) for x in tmp]
			return result

	def change_tree(self, tree, new_term, n):
		'''
		木 tree の ノードに含まれる特定の単語を，全て new_term に置き換える．
		特定の単語とは tree のルートノードの右から n + 1 番目である．
		'''
		if not isinstance(tree, list):
			# print("in change_tree", tree, new_term[n:] + tree[-n:])
			self.change_node(tree, new_term[n:] + tree[-n:])
		else:		# 末端の node から変更することで，グラフの整合性を保つ
			[self.change_tree(n_tree, new_term, n + 1) for n_tree in tree[1]]
			term = tree[0]
			self.change_node(term, new_term[n:] + term[-n:])

	# def change_nodes(self, term, new_term, n):
	# 	if n <= 0 or term not in graph.db:
	# 		self.change_node(term, new_term)

	def remove_tree(self, tree, n):
		'''
		木 tree に含まれるノードを削除する．
		'''
		if not isinstance(tree, list):
			# print("rm:", tree)
			self.remove_node(tree)
		else:
			# print(tree)
			[self.remove_tree(n_tree, n - 1) for n_tree in tree[1]]
			term = tree[0]
			# print("rm:", term)
			self.remove_node(term)

	# def remove_nodes(self, term, n):
	# 	if n <= 0 or term not in self.db:
	# 		print(term)
	# 		self.remove_node(term)
	# 	else:
	# 		print(self.db[term])
	# 		[self.remove_nodes(n_term, n - 1) for n_term in self.db[term]]
	# 		print(self.db[term])
	# 		print(term)
	# 		self.remove_node(term)
