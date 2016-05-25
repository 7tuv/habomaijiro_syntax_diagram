#!/usr/bin/env python
# -*- coding: utf-8 -*-


class graph:
	def __init__(self):
		self.db = {}
		self.db_r = {}
		self.chain_weights = {}
		self.chain_labels = {}
		self.init_terms = []

	def print_elem(self):
		print(self.db)
		print(self.db_r)
		print(self.chain_weights)
		print(self.chain_labels)
		print(self.init_terms)

	def set_init_terms(self, term):
		self.init_terms.append(tuple(term))

	def set_node(self, term):		# 新しい頂点を加える
		if term not in self.db:
			self.db[term] = []
		if term not in self.db_r:
			self.db_r[term] = []

	def set_edge(self, source, target, weight, label=""):		# 新しい矢印を加える
		self.set_node(source)
		self.set_node(target)

		if target not in self.db[source]:
			self.db[source].append(target)

		if source not in self.db_r[target]:
			self.db_r[target].append(source)

		if (source, target) in self.chain_weights:
			self.chain_weights[(source, target)] += weight
		else:
			self.chain_weights[(source, target)] = weight

		if (source, target) in self.chain_labels:
			# self.chain_labels[(source, target)] += label
			pass
		else:
			self.chain_labels[(source, target)] = label

	def remove_node(self, term):		# 頂点を削除する
		n_terms = self.db[term]
		p_terms = self.db_r[term]
		for n_term in n_terms:
			self.db_r[n_term].remove(term)
			del self.chain_weights[(term, n_term)]
			del self.chain_labels[(term, n_term)]
		for p_term in p_terms:
			self.db[p_term].remove(term)
			del self.chain_weights[(p_term, term)]
			del self.chain_labels[(p_term, term)]
		del self.db[term]
		del self.db_r[term]
		# self.print_elem()

	def remove_edge(self, term, n_term):		# 矢印を削除する
		self.db[term].remove(n_term)
		self.db_r[n_term].remove(term)
		del self.chain_weights[(term, n_term)]
		del self.chain_labels[(term, n_term)]
		# self.print_elem()

	def change_node(self, term, new_term):		# 頂点の term を new_term に変更する
		n_terms = self.db[term]
		p_terms = self.db_r[term]
		# print(term)
		# print(p_terms)
		# print(n_terms)

		[self.set_edge(new_term, n_term, self.chain_weights[(term, n_term)], n_term[-1]) for n_term in n_terms]
		[self.set_edge(p_term, new_term, self.chain_weights[(p_term, term)], new_term[-1]) for p_term in p_terms]
		self.remove_node(term)
		# self.print_elem()

	def is_linear_node(self, term, n):
		if n == 0:		# 深さ 0 の時は無条件で True
			return True
		elif term not in self.db:
			return True
		n_terms = self.db[term]
		value = all([len(self.db_r[n_term]) == 1 for n_term in n_terms])
		if n == 1:
			return value
		else:
			return value and all([self.is_linear_node(n_term, n - 1) for n_term in n_terms])

	def get_tree(self, term, n):		# ある頂点 term から深さ n までの遷移先の頂点を(深く)取得する
		if term not in self.db:			# structure ::= [term, [structure(==n_term)]]
			return []
		n_terms = self.db[term]
		if n <= 1:
			return n_terms[:]		# 深いコピー
		else:
			return [[n_term, (self.get_tree(n_term, n - 1))] for n_term in n_terms]

	def change_tree(self, tree, new_term, n):		# 末端の node から変更することで，整合性を保つ
		if not isinstance(tree, list):				# また上5行目の深いコピーは，この整合性を保つために必要な条件である
			# print("in change_tree", tree, new_term[n:] + tree[-n:])
			# print(tree)
			self.change_node(tree, new_term[n:] + tree[-n:])
		else:
			# print(tree)
			[self.change_tree(n_tree, new_term, n + 1) for n_tree in tree[1]]
			term = tree[0]
			self.change_node(term, new_term[n:] + term[-n:])

	# def change_tree(self, tree, new_term, n):		# 末端の node から変更することで，整合性を保つ
	# 	if not isinstance(tree, list):				# また上5行目の深いコピーは，この整合性を保つために必要な条件である
	# 		# print("in change_tree", tree, new_term[n:] + tree[-n:])
	# 		self.change_node(tree, new_term[n:] + tree[-n:])
	# 	else:
	# 		[self.change_tree(n_tree, new_term, n + 1) for n_tree in tree[1]]
	# 		term = tree[0]
	# 		self.change_node(term, new_term[n:] + term[-n:])

	# def change_nodes(self, term, new_term, n):
	# 	if n <= 0 or term not in graph.db:
	# 		self.change_node(term, new_term)

	def remove_tree(self, tree, n):
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
