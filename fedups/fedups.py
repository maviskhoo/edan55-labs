import numpy as np
import copy

# ==================== FUNCTIONS ====================
def monte_carlo(starting_state, ending_state):

    # Initialise global variables
    global p_matrix
    global t_matrix
    global N

    current_state = starting_state
    
    prob = 1
    time = 0

    while current_state != ending_state:

        next_state = np.random.choice(N,p=p_matrix[current_state])

        prob = prob * p_matrix[current_state][next_state]
        time += t_matrix[current_state][next_state]

        current_state = next_state

    return prob, time

def run_monte_carlo(num_simulations, starting_state, ending_state):

    total_time = 0

    for _ in range(num_simulations):

        _, time = monte_carlo(starting_state,ending_state)
        total_time += time
    
    # Calculate average delivery times
    avg_time = total_time / num_simulations

    return avg_time

def markov(pMatrix, time):
    l = len(pMatrix)
    
    # Construct the coefficient matrix A
    A = pMatrix - np.eye(l)
    
    # Construct the constant vector b
    b = -time
    
    # Solve the linear system of equations
    x = np.linalg.solve(A, b)
    
    return x

def build_matrix(start, finish, type):
    
    taken = build_path(start)
    
    l = len(taken)

    if l == N:
        return np.array(p_matrix), b
    
    pM = np.array([np.array([0.0 for _ in range(l)]) for _ in range(l)])
    t = np.array([0.0 for _ in range(l)])
    
    not_in_path = np.array([x for x in range(N - 1, -1, -1)])
    for x in taken:
        index = np.argwhere(not_in_path==x)
        not_in_path = np.delete(not_in_path, index)
    
    for x in range(l):
        v = taken[x]
        if v == start:
            if type == 'f':
                F = x
            else:
                P = x
        if v == finish:
            H = x
        vect = copy.copy(p_matrix[v])
        for y in not_in_path:
            vect = np.delete(vect, y)        
        pM[x] = vect
        t[x] = b[v]
    
    return pM, t
    
    
def build_path(n, taken = None):
    if taken is None:
        taken = []

    taken.append(n)
    for next_state, x in enumerate(p_matrix[n]):
        if x > 0.0 and next_state not in taken:
            build_path(next_state, taken)

    return taken 
    

def check_possible (starting_state, ending_state, visited = None):
    
    if visited == None:
        visited = []

    if starting_state == ending_state:
        return 1
    
    visited.append(starting_state)

    for next_state, x in enumerate(p_matrix[starting_state]):
        if x > 0.0 and next_state not in visited:
            if check_possible(next_state, ending_state, visited) == 1:
                return 1
            
    return 0

# ==================== MAIN ====================

filename = "small"
num_of_montecarlo_runs = 50000
f = open(f"fedups/data/{filename}.in","r")

N, M, H, F, P = map(int, f.readline().split())
H_original = H

# Create N x N probability matrix - Represent the probability for state transition
p_matrix = [[float(0) for _ in range(N)] for _ in range(N)]

# Create M x M time matrix - Represent the time for each road
t_matrix = [[0 for _ in range(N)] for _ in range(N)]

# Create a b[N] vector
b = np.zeros(N)

for road in range(M):
    u, v, t, p_uv, p_vu = f.readline().split()

    u = int(u)
    v = int(v)
    t = int(t)
    p_uv = float(p_uv)
    p_vu = float(p_vu)

    p_matrix[u][v] = p_uv
    p_matrix[v][u] = p_vu
    t_matrix[u][v] = t_matrix[v][u] = t

    b[u] += p_uv * t
    b[v] += p_vu * t

f.close()

if check_possible(F,H) == 1:
    print("FedUPS")
    time_fedups = run_monte_carlo(num_of_montecarlo_runs, F, H)
    print("Monte-Carlo Algo: " + str(time_fedups))

    # Calculate estimated delivery time E(G)
    A_fedups,b_fedups = build_matrix(F,H,"f")
    results_fedups = markov(A_fedups,b_fedups)
    estimated_time_fedups = results_fedups[F]
    print("Markov Algo: " + str(estimated_time_fedups))

    # Calculate relative accuracy
    relative_accuracy_fedups = estimated_time_fedups - time_fedups
    relative_accuracy_fedups = relative_accuracy_fedups/estimated_time_fedups
    print("Relative Accuracy: " + str(relative_accuracy_fedups))
else:
    print("FedUps tried to deliver your package, but you were not at home")

if check_possible(P,H) == 1:
    print("PostNHL")
    time_postNHL = run_monte_carlo(num_of_montecarlo_runs, P, H)
    print("Monte-Carlo Algo: " + str(time_postNHL))

    H = H_original
    A_postNHL,b_postNHL = build_matrix(P,H,"p")
    results_postNHL = markov(A_postNHL,b_postNHL)
    estimated_time_postNHL = results_postNHL[P]
    print("Markov Algo: " + str(estimated_time_postNHL))

    # Calculate relative accuracy
    relative_accuracy_postNHL = estimated_time_postNHL - time_postNHL
    relative_accuracy_postNHL = relative_accuracy_postNHL/estimated_time_postNHL
    print("Relative Accuracy: " + str(relative_accuracy_postNHL))
else:
    print("PostNHL tried to deliver your package, but you were not at home")