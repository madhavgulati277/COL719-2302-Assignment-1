# Packages Imported
import glob
import json
import networkx as nx
import matplotlib.pyplot as plt
import random

# Global Dependecies

# Array of Input Statements
statements = []

# Dictionary of AST's
ast_ll = {}

# Global Variables
op_count = {'=': 0,
            '+': 0,
            '-': 0,
            '/': 0,
            '*': 0}
var_count = {}
curr_dependency = {}

# Graph
G = nx.DiGraph()
id_map = {}


def read_inputs(file):
    readFile = glob.glob(file)[0]
    # Reading Gate Delays
    with open(readFile) as f:
        for line in f:
            line_arr = line.strip().split()
            if (len(line_arr) > 2):
                statements.append(line_arr)
# Reading Inputs


def process_asts():
    line_no = 0
    for statement in statements:
        ast = []
        ast.append([statement[0]])
        ast.append(["="])
        ast.append(construct_ast(statement[2:]))
        ast_ll[line_no] = ast
        curr_dependency[statement[0]] = line_no
        line_no += 1
# Create AST's for all statements


def construct_ast(rhs):
    if (len(rhs) == 1):
        if (rhs[0] in curr_dependency):
            temp = {}
            temp[rhs[0]] = ast_ll[curr_dependency[rhs[0]]][2]
            # print(temp)
            return temp
        else:
            return rhs
    add = []
    sub = []
    mul = []
    div = []
    for i in range(0, len(rhs)):
        if rhs[i] == '+':
            add.append(i)
        if (rhs[i] == '–' or rhs[i] == '-'):
            sub.append(i)
        if rhs[i] == '*':
            mul.append(i)
        if rhs[i] == '/':
            div.append(i)
    if (len(sub) != 0):
        each = sub.pop(len(sub)-1)
        a = []
        a.append(construct_ast(rhs[0:each]))
        a.append(rhs[each:each+1])
        a.append(construct_ast(rhs[each+1:]))
        return a
    elif (len(add) != 0):
        each = add.pop(len(add)-1)
        a = []
        a.append(construct_ast(rhs[0:each]))
        a.append(rhs[each:each+1])
        a.append(construct_ast(rhs[each+1:]))
        return a
    elif (len(mul) != 0):
        each = mul.pop(len(mul)-1)
        a = []
        a.append(construct_ast(rhs[0:each]))
        a.append(rhs[each:each+1])
        a.append(construct_ast(rhs[each+1:]))
        return a
    elif (len(div) != 0):
        each = div.pop(len(div)-1)
        a = []
        a.append(construct_ast(rhs[0:each]))
        a.append(rhs[each:each+1])
        a.append(construct_ast(rhs[each+1:]))
        return a
# Construct AST


def print_write_ast():
    # for each in ast_ll:
    #     print(each, " : ", ast_ll[each])
    with open("output-ast.txt", 'w') as file:
        json.dump(ast_ll, file)
# Print AST as Array of Arrays


def operator_count(input, count):
    count[input] = count[input] + 1
    if (input == '='):
        return str(count[input]) + '='
    elif (input == '+'):
        return str(count[input]) + '+'
    elif (input == '-'):
        return str(count[input]) + '-'
    elif (input == '*'):
        return str(count[input]) + '*'
    elif (input == '/'):
        return str(count[input]) + '/'
# Operator Count


def create_dfg():

    for each in ast_ll:
        # Single AST for each statment
        ast = ast_ll[each]

        # Parent =
        parent_v = ast[1][0]
        parent = operator_count(parent_v, op_count)
        parent_id = id(parent)
        id_map[parent] = parent_id
        G.add_node(parent_id, name=parent_v)

        # Left Child

        left_child = ast[0][0]

        if (left_child in var_count):
            var_count[left_child] = var_count[left_child]+1
        else:
            var_count[left_child] = 1
        left_child_c = left_child+str(var_count[left_child])
        curr_dependency[left_child] = [left_child_c, op_count['=']]
        left_child_id = id(left_child_c)
        id_map['write-'+left_child_c] = left_child_id
        G.add_node(left_child_id, name='write')
        G.add_edge(left_child_id, parent_id, label=left_child_c)
        # Right Child
        right_child = ast[2]

        if (right_child == left_child):
            print("invalid input")

        if (type(ast[2]) == type({})):
            # Method 1
            for each in ast[2]:
                child_v = curr_dependency[each][0]
                # child_v = each+str(var_count[each])
            child = "write-" + child_v
            if child in id_map.keys():
                id_temp = id_map[child]
                edges = G.edges(id_temp)
                id_map.pop(child)
                for each in edges:
                    G.add_edge(each[1], parent_id, label=child_v)
                G.remove_node(id_temp)

            else : 
                depend_arr = curr_dependency[each]
                id_connect = id_map[str(depend_arr[1])+"="]
                edges = G.edges(id_connect)
                for each in edges:
                    G.add_edge(each[1], parent_id, label=child_v)
        else:
            construct_dfg(right_child, parent_id, op_count)

# Process DFG


def construct_dfg(ast, parent_id, op_count):
    if (len(ast) == 1):
        child = ast[0]
        if (child.isdigit()):
            child_id = id(child)
            id_map[child] = child_id
            G.add_node(child_id, name=child)
            G.add_edge(child_id, parent_id)
        else:
            if (child in var_count):
                var_count[child] = var_count[child]+1
            else:
                var_count[child] = 1
            child_c = child+str(var_count[child])
            child_id = id(child_c)
            id_map['read-'+child_c] = child_id
            G.add_node(child_id, name='read')
            G.add_edge(child_id, parent_id, label=child_c)
    else:
        # Child
        child_v = ast[1][0]
        child = operator_count(child_v, op_count)
        child_id = id(child)
        id_map[child] = child_id
        G.add_node(child_id, name=child_v)
        G.add_edge(child_id, parent_id)

        # Left Grandchild
        # Method 1

        if (type(ast[0]) == type({})):
            for each in ast[0]:
                child_v = curr_dependency[each][0]
                # child_v = each+str(var_count[each])
                child = "write-" + child_v
                if child in id_map.keys():
                    id_temp = id_map[child]
                    edges = G.edges(id_temp)
                    id_map.pop(child)
                    for each in edges:
                        G.add_edge(each[1], child_id, label=child_v)
                    G.remove_node(id_temp)
                else:
                    depend_arr = curr_dependency[each]
                    id_connect = id_map[str(depend_arr[1])+"="]
                    edges = G.edges(id_connect)
                    for each in edges:
                        G.add_edge(each[1], child_id, label=child_v)
        else:
            construct_dfg(ast[0], child_id, op_count)

        # Right GrandChild
        # Method 1
        if (type(ast[2]) == type({})):
            for each in ast[2]:
                child_v = curr_dependency[each][0]
                # child_v = each+str(var_count[each])
                child = "write-" + child_v
                if child in id_map.keys():
                    id_temp = id_map[child]
                    edges = G.edges(id_temp)
                    id_map.pop(child)
                    for each in edges:
                        G.add_edge(each[1], child_id, label=child_v)
                    G.remove_node(id_temp)
                else:
                    depend_arr = curr_dependency[each]
                    id_connect = id_map[str(depend_arr[1])+"="]
                    edges = G.edges(id_connect)
                    for each in edges:
                        G.add_edge(each[1], child_id, label=child_v)
                    # print(id_map[child_v])
                    # print('write-code')
        else:
            construct_dfg(ast[2], child_id, op_count)
# Construct DFG


def print_write_dfg():
    labels = {node: G.nodes[node]['name'] for node in G.nodes()}
    edge_labels = nx.get_edge_attributes(G, 'label')
    # pos = {node: (i, i) if i % 2 == 0 else (i, -i)
    #        for i, node in enumerate(G.nodes)}
    # pos = {node: (0, -i) for i, node in enumerate(G.nodes)}
    seed = random.randint(1, 20)
    pos = nx.spring_layout(G, seed=seed)
    nx.draw(G, pos, with_labels=True, node_size=100, node_color='yellow',
            font_size=9, font_color='black', arrowsize=10, font_weight='bold', labels=labels)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.write_weighted_edgelist(G, "output-dfg.txt")
    dpi = 200  # dots per inch
    plt.savefig("output-dfg-diagram.png", dpi=dpi,
                bbox_inches='tight', pad_inches=0.7)
    with open("output-keymap.txt", 'w') as file:
        json.dump(id_map, file)
    # plt.show()
# Print and Write DFG


if __name__ == "__main__":
    # Input
    read_inputs("input.txt")
    # AST
    process_asts()
    # DFG
    create_dfg()
    # Output
    print_write_ast()
    print_write_dfg()
    # print(id_map)
    # print(curr_dependency)
