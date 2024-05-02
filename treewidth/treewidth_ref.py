import time
from pathlib import Path

class treewidth():
    
    def __init__(self, file):
        td_file = open(file + ".td", 'r')
        gr_file = open(file + ".gr", 'r')
        
        line = td_file.readline()
        while line[0] == 'c':
            line = td_file.readline()

        _, _, num_vertices, width, time = line.split()
        self.num_vertices = int(num_vertices)
        self.width = int(width)
        self.time = float(time)
        
        line = gr_file.readline()
        while line[0] == 'c':
            line = gr_file.readline()
            
        _, _, num_nodes, num_edges = line.split()
        self.num_nodes = int(num_nodes)
        self.num_edges = int(num_edges)
        
        self.graph = [[] for _ in range(self.num_nodes + 1)]
        
        for _ in range(0, self.num_edges):
            u, v = gr_file.readline().split()
             
            self.graph[int(u)].append(int(v))
            self.graph[int(v)].append(int(u))
           
        self.bags = [[] for _ in range(self.num_vertices + 1)]
        
        for x in range(1, self.num_vertices + 1):
            line = td_file.readline().split()[2:]
            for y in line:
                self.bags[x].append(int(y))
        
        self.tree_structure = [[] for _ in range(self.num_vertices + 1)]
        
        line = td_file.readline()
        while line != "":
            u, v = line.split()
            
            self.tree_structure[int(u)].append(int(v))
            self.tree_structure[int(v)].append(int(u))
            
            line = td_file.readline()
        
    def __call__(self):
        self.in_tree = [0 for _ in range(self.num_vertices + 1)]
        self.tree = [[] for _ in range(self.num_vertices + 1)]
        self.build_tree(1)
        
        best_score = 0
        root_scores = self.compute_maximum_independent_set(1)
        for node_score in root_scores.values():
            best_score = max(best_score, node_score)
        print("Number of nodes =", self.num_nodes, "\nWidth =", self.width - 1, "\nMaximum Independent Set =", best_score)
      
    def check_set_independence(self, set):
        if len(set) == 0 or len(set) == 1:
            return len(set)
        for i in range(len(set)):
            node = set[i]
            neighbours = self.graph[node]
            for n in neighbours:
                if n in set:
                    return -1
        return len(set)
    
    def build_tree(self, node):
        self.in_tree[node] = 1
        neighbours = self.tree_structure[node]
        for n in neighbours:
            if self.in_tree[n] == 0:
                self.tree[node].append(n)
                self.build_tree(n)
    
    def generate_subsets(self, vertex_bag):
        n = 2**len(vertex_bag) - 1
        length = len(bin(n).split('b')[1])
        bitstrings = {}
        for x in range(0, n + 1):
            b = bin(x)
            b = b.replace('b', '0')
            if len(b) > length:
                b = b[-1*length:]
            while len(b) < length:
                b = '0' + b
            nodes = [vertex_bag[y] for y in range(length) if b[y] == '1']
            value = self.check_set_independence(nodes)
            if value != -1:
                bitstrings[b] = value
        return bitstrings
    
    def calculate_mis_scores(self, parent_bitstrings, child_bitstrings, parent, child):
        parent_bag = self.bags[parent]
        child_bag = self.bags[child]
        for parent_bitstring in parent_bitstrings:
            parent_nodes = [parent_bag[y] for y in range(len(parent_bitstring)) if parent_bitstring[y] == '1']
            intersection = [val for val in parent_nodes if val in child_bag]
            best = 0
            for child_bitstring in child_bitstrings:
                child_nodes = [child_bag[y] for y in range(len(child_bitstring)) if child_bitstring[y] == '1']
                if intersection == [val for val in child_nodes if val in parent_bag]:
                    value = child_bitstrings[child_bitstring] - len([val for val in parent_nodes if val in child_nodes])
                    best = max(best, value)
            parent_bitstrings[parent_bitstring] += best
        return parent_bitstrings
    
    
    def compute_maximum_independent_set(self, bag):
        if not self.tree[bag]:
            return self.generate_subsets(self.bags[bag])
        else:
            children = self.tree[bag]
            parent_bitstrings = self.generate_subsets(self.bags[bag])
            for child in children:
                child_bitstrings = self.compute_maximum_independent_set(child)
                parent_bitstrings = self.calculate_mis_scores(parent_bitstrings, child_bitstrings, bag, child)
            return parent_bitstrings
        
        
        
if __name__ == "__main__":
    files = Path("treewidth\data").glob('*')
    done = 0
    prevfile = "nothing"
    largest_n_in_a_min = [0,0,0]
    largest_w_in_a_min = [0,0,0]
    for file in files:
        runtime = 0
        file = str(file)[:-3]
        file_name = file.split('\\')[2]
        if prevfile == file_name:
            td_file = open(file + ".td", 'r')
            line = td_file.readline()

            if line[0] == 'c':
                runtime = float(line.split()[-1])

            if runtime <= 60 and runtime>0:
                print(file_name)
                start_time = time.time()
                tw = treewidth(file)
                tw()
                end_time = time.time()
                print("Runtime =","%s seconds" % (end_time - start_time))
                print("\n")
                if tw.num_nodes > largest_n_in_a_min[1]:
                    largest_n_in_a_min = [file_name, tw.num_nodes, tw.width]
                if tw.width > largest_w_in_a_min[1]:
                    largest_w_in_a_min = [file_name, tw.num_nodes, tw.width]

        prevfile = file_name
     


    print("Largest n = \n" + largest_n_in_a_min + "\n")
    print("Largest w = \n" + largest_w_in_a_min + "\n")
    