import numpy as np
import sys
import pprint
import json
import networkx as nx
from matplotlib import pyplot as plt
import pandas
import numpy as np
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures
import os
import pandas as pd

pp = pprint.PrettyPrinter(indent=4)


# this function insert and edge device to the ED_m and ED_c matrix
def insert_edge_device(ED_m, ED_c, num_edge,new_edm_info, new_edc_info, ed_dict, ed_info):
	row_m,col_m = ED_m.shape
	row_c,col_c = ED_c.shape
	if len(new_edm_info) != col_m:
		print("the required info of the new edge device is incomplete, edge device cann't be added.")
		return ED_m, ED_c, num_edge
	if len(new_edc_info) != col_c:
		print("the required info of the new edge device is incomplete, edge device cann't be added.")
		return ED_m, ED_c, num_edge
	else:
		ED_m=np.append(ED_m,[new_edm_info],axis=0)
		ED_c=np.append(ED_c,[new_edc_info],axis=0)
		num_edge +=1
		ed_dict[num_edge-1]=ed_info; # update the new edge device avialble resource in the dictionary
		return ED_m, ED_c, num_edge, ed_dict

# this helper function extract a patch rows:row_r x col_s:col_e
def extract_blocks(row_s, row_e, col_s, col_e, block):
	row,col=block.shape
	new_array=np.empty((0,col_e-col_s+1))
	for i in range(row):
		if i>= row_s and i <= row_e:
			new_array=np.append(new_array,[block[i][col_s:col_e+1]],axis=0)
	return new_array


# this did not pass exhaustive test, need to test on the reliability of this code
def insert_task(ED_m, ED_c, num_edge, num_task, new_edm_info, new_edc_info):
	row_m,col_m = ED_m.shape
	row_c,col_c = ED_c.shape
	new_EDm=np.empty((num_edge,0))
	if new_edm_info.shape[1] != 2*num_task+1 or new_edm_info.shape[0] !=  num_edge:
		print("the required info of the new task on each device is incomplete, task can't be added edm.")
	if new_edc_info.shape[1] != 1 or new_edc_info.shape[0] !=  num_edge:
		print("the required info of the new task on each device is incomplete, task can't be added edc.")
	else:
		for i in range(num_task):
			new_EDm=np.append(new_EDm, extract_blocks(0,num_edge-1,i*num_task,i*num_task+num_task-1,ED_m), axis=1)
			new_EDm=np.append(new_EDm,extract_blocks(0,num_edge-1,i,i,new_edm_info),axis=1)
		new_EDm=np.append(new_EDm,extract_blocks(0,num_edge-1, num_task, 2*num_task, new_edm_info),axis=1)
		new_EDc=np.append(ED_c,new_edc_info,axis=1)
		num_task += 1
	return new_EDm, new_EDc, num_task


def BFS(edge_adj):
	vert_dict={}
	for u in edge_adj.keys():
		if u not in vert_dict.keys():
			vert_dict[u]={'color':'white','dis':sys.maxsize,'anc': None}
	vert_dict['0']['color']="grey"
	vert_dict['0']['dis']=0
	vert_dict['0']['anc']=None
	queue=[]
	queue.append('0')
	while queue:
		u = queue.pop(0)
		for v in edge_adj[u]:
			if v != "end":
				if vert_dict[v]['color'] == 'grey':
					vert_dict[v]['dis'] = vert_dict[u]['dis'] + 1
					vert_dict[v]['anc'] = u
				if vert_dict[v]['color'] == 'white':
					vert_dict[v]['color'] = 'grey'
					vert_dict[v]['dis'] = vert_dict[u]['dis'] + 1
					vert_dict[v]['anc'] = u
					queue.append(v)
		vert_dict[u]['color'] = 'black'
	vert_dict['1']['color']="grey"
	vert_dict['1']['dis']=0
	vert_dict['1']['anc']=None
	queue=[]
	queue.append('1')
	while queue:
		u = queue.pop(0)
		for v in edge_adj[u]:
			if v != "end":
				if vert_dict[v]['color'] == 'grey':
					vert_dict[v]['dis'] = vert_dict[u]['dis'] + 1
					vert_dict[v]['anc'] = u
				if vert_dict[v]['color'] == 'white':
					vert_dict[v]['color'] = 'grey'
					vert_dict[v]['dis'] = vert_dict[u]['dis'] + 1
					vert_dict[v]['anc'] = u
					queue.append(v)
		vert_dict[u]['color'] = 'black'
	return vert_dict	


# this returns the application in stages contain tasks in each stage
def app_stage(edge_adj):
	vert_dict = BFS(edge_adj)
	vert_dict.pop('s')
	num_vert = len(vert_dict.keys())
	stages = vert_dict[str(num_vert-1)]['dis']	# number of stages in one application instance
	stage_dict = {}
	
	for i in range(stages+1):
		if i not in stage_dict.keys():
			stage_dict[i]=[]
	for vert in vert_dict.keys():
			stage_dict[vert_dict[vert]['dis']].append(vert)
	return vert_dict, stage_dict

def task_info(vertices):
	task_dic = dict()
	for each in vertices:
		if each["name"] != "s" and each["name"] != 0:
			task_dic[each["name"]]=[each["file"],each["model"],each["input"]]
	return task_dic

def plot(graph):
    plt.tight_layout()
    nx.draw_networkx(graph, arrows=True)
    #plt.savefig("../figures/DAG.png", format="PNG") #save plot
    plt.show() #show plot
    plt.clf()

def dag(edges):
    graph = nx.DiGraph()
    graph.add_edges_from(edges)
    graph.nodes()
    ## TODO: check if the graph is cyclic
    # plot(graph)
    return graph

def linearize_dag(graph,path,paths=[]):
    datum = path[-1]              
    if datum in graph.keys():
        for val in graph[datum]:
            new_path = path + [val]
            paths = linearize_dag(graph, new_path, paths)
    else:
        paths += [path]
    return paths


def dag_linearization(f):
    # returns JSON object as a dictionary
    data = json.load(f)
    #read edges of the graph
    edge_list = []
    for source in data["Application"]["Edges"].keys():
        for target in data["Application"]["Edges"][source]:
            edge_list.append(tuple([source,target]))

    graph = dag(edge_list)
    lin_dag=linearize_dag(data["Application"]["Edges"],path=["0"],paths=[])
    #lin_list contains all the linearized chains in the DAG
    lin_list=[]
    for each_dag in lin_dag:
        tmp_dag=[]
        for idx, each in enumerate(each_dag):
            if idx < len(each_dag)-1:
                tmp_dag.append(tuple([each_dag[idx],each_dag[idx+1]]))
        lin_list.append(tmp_dag)

    #read vertices of the graph
    vertex_dict = data["Application"]["Vertices"]
    edge_adj = data["Application"]["Edges"]
    return data, graph, lin_list, vertex_dict, edge_adj

def task_info_update(task,ED_tasks,time):
	pass
	return

def trans_time_estimate(file,ntbd):
		#transtime = math.ceil(os.path.getsize(file)/ntbd))
		#used a fixed size for testing purposes
	return math.ceil(1200/ntbd)

def cpu_regression_setup(task_types, num_edge, app_path):
	X_s=[]
	Y_s=[]
	X_fit=[]
	regression_models=[]
	edge_device_list=[]
	regression_task_list = []
	for i in range(task_types):
		task = "#tk"+str(i) 
		regression_task_list.append(task)
	for i in range(num_edge):
		device="ED"+str(i)+".csv"
		edge_device_list.append(device)

	for i in range(num_edge):
		tmp=pandas.read_csv(os.path.join(app_path,edge_device_list[i]))
		X_s.append(tmp[regression_task_list])
		Y_s.append(tmp['cpu_usage'])
	poly = PolynomialFeatures(degree=3)
	for i in range(num_edge):
		X_fit.append(poly.fit_transform(X_s[i]))
	for i in range(num_edge):
		regression_models.append(linear_model.LinearRegression().fit(X_fit[i],Y_s[i]))
	return regression_models

def latency_regression_setup(task_types,num_edge, EDmc_path):
	X=[100,80,50,30,10,5]
	latency_regression_model=[]
	edge_list=[]
	for i in range(num_edge):
		device="ED"+str(i)+"_latency"
		edge_list.append(device)
	for i in range(num_edge):	
		ED = np.array(pd.read_excel(EDmc_path,engine="openpyxl",sheet_name=edge_list[i],skiprows=0, nrows= task_types))
		ED_latency=[]
		for j in range(task_types):
			Y = np.log(ED[j])
			Z=np.polyfit(X, Y, 1)
			fit_func = np.poly1d(Z)
			ED_latency.append(fit_func)
		latency_regression_model.append(ED_latency)
	return latency_regression_model







