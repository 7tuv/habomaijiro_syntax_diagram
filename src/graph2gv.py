#!/usr/bin/env python
# -*- coding: utf-8 -*-

from graphviz import Digraph

exists_in_start = {}
exists_in_end = {}


def gen_n_edges(G, chain, c_weight, c_label):		# N階マルコフ連鎖の可視化に対応
	strlist1 = list(map(str, chain[0]))
	strlist2 = list(map(str, chain[1]))
	split_char = " , "
	label = ""
	style = ""

	if c_weight != 1:
		label = str(c_weight)
		style = "bold"
	# else:
	# 	return			# c_weight == 1 の矢印を省略

	# label = c_label
	# if label == "End1":
	# 	label = "End"

	if len(strlist1) == 1:		# N == 1
		G.edge(strlist1[0], strlist2[0], label=label, style=style)
	else:		# N > 1
		str1 = split_char.join(strlist1)
		str2 = split_char.join(strlist2)

		if strlist1[0] == "0Start":
			strlist1[0] = "Start"		# ラベルでは 0Start の0を外す
			str1 = split_char.join(strlist1)
			# G.edge("0Start", str1, label=label, style='dashed')
			if str1 in exists_in_start:
				exists_in_start[str1] += c_weight
			else:
				exists_in_start[str1] = c_weight

		elif strlist2[-1] == "End1":
			strlist2[-1] = "End"		# ラベルでは End1 の1を外す
			str2 = split_char.join(strlist2)
			if str2 in exists_in_end:
				exists_in_end[str2] += c_weight
			else:
				exists_in_end[str2] = c_weight

		G.edge(str1, str2, label=label, style=style)


def gen_start_edges(G, str1, c_weight):
	if c_weight == 1:
		G.edge("0Start", str1, style='dashed')
	else:
		G.edge("0Start", str1, label=str(c_weight), style='dashed')


def gen_end_edges(G, str2, c_weight):
	if c_weight == 1:
		G.edge(str2, "End1", style='dashed')
	else:
		G.edge(str2, "End1", label=str(c_weight), style='dashed')


def makegv(chain_weights, chain_labels, filename, engine):
	exists_in_start.clear()
	exists_in_end.clear()
	G = Digraph(name="G", filename=filename + ".gv", format="pdf", engine=engine, encoding="utf-8")
	# G.body.append('sep="+125,+125"')
	# G.body.append('nodesep="0.4"')
	# G.body.append('ranksep="0.4"')
	# G.graph_attr['rankdir'] = 'LR'
	# G.graph_attr['splines'] = 'line'
	G.graph_attr['charset'] = "UTF-8"
	# G.graph_attr['size'] = "150, 250"
	# G.graph_attr['concentrate'] = "true"

	# G.node_attr['shape'] = 'box'
	G.node_attr['fontname'] = 'MS UI Gothic'
	# G.node_attr['fixedsize'] = 'true'
	# G.node_attr['width'] = '1.6'
	# G.node_attr['height'] = '0.9'

	# G.edge_attr['fontname'] = 'bold'
	G.edge_attr['fontname'] = 'MS UI Gothic'
	# G.edge_attr['labeldistance'] = '0.5'

	G.node("0Start", label="Start", shape="box", fontname="bold")
	G.node("End1", label="End", shape="doublecircle", fontname="bold")

	[gen_n_edges(G, chain, chain_weights[chain], chain_labels[chain]) for chain in chain_weights]
	[gen_start_edges(G, str1, exists_in_start[str1]) for str1 in exists_in_start]
	[gen_end_edges(G, str2, exists_in_end[str2]) for str2 in exists_in_end]

	G.save()
	G.render(filename=filename, view=0, cleanup=1)

#  dot -Tpdf xxx.gv -o xxx.pdf
#  dot -Tpng xxx.gv -o xxx.png
#  sfdp -Gsize=67! -Goverlap=prism -Tpng xxx.gv -o xxx.png
