#Aysenur Guller 27796
import pycosat

def dimacs_to_graph(filename):
    """
  Reads a graph from a file in the DIMACS coloring format.

  Args:
      filename: Path to the file containing the graph data.

  Returns:
      A list of edges.
  """
    edges = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('e'):
                _, v1, v2 = line.split()
                edges.append((int(v1), int(v2)))
    vertices = list(set(sum(edges, ())))       
    return edges,vertices

def create_CNF(vertices, edges, k):
    """
  Encodes the vertex coloring problem as a CNF formula.

  Args:
      vertices: Set of vertices in the graph.
      edges: List of edges connecting vertices.
      k: Number of available colors.

  Returns:
      A list of clauses representing the CNF formula.
  """
    clauses = []

   # 1. At least one color per vertex
    for vertex in vertices:
        clause = []
        for color in range(1, k + 1):
            clause.append((vertex - 1) * k + color)
        clauses.append(clause)

    # 2. At most one color per vertex
    for vertex in vertices:
        for c1 in range(1, k + 1):
            for c2 in range(c1 + 1, k + 1):
                clauses.append([-((vertex - 1) * k + c1), -((vertex - 1) * k + c2)])

    # 3. Adjacent vertices cannot have the same color
    for v1, v2 in edges:
        for color in range(1, k + 1):
            clauses.append([-(v1 - 1) * k - color, -(v2 - 1) * k - color])

    return clauses

def check_vertex_coloring(vertices, edges, k):
    """
  Checks if the graph can be colored with at most k colors using a SAT solver.

  Args:
      vertices: Set of vertices in the graph.
      edges: List of edges connecting vertices.
      k: Number of colors to attempt coloring with.

  Returns:
      True if the graph is colorable with at most k colors, False otherwise.
     """
    clauses = create_CNF(vertices, edges, k)
    solution = pycosat.solve(clauses)
    return solution != 'UNSAT', solution

def find_chromatic_number(vertices, edges):
    """
  Finds the minimum number of colors needed to color the graph (chromatic number).

  Args:
      vertices: Set of vertices in the graph.
      edges: List of edges connecting vertices.

  Returns:
      The chromatic number of the graph.
    """
    k = 1
    while True:
        valid_coloring, solution = check_vertex_coloring(vertices, edges, k)
        if valid_coloring:
            return k, solution
        k += 1

def print_solution(vertices,num):
    """
  Prints the color assignment for each vertex in a solution.

  Args:
      vertices: Set of vertices in the graph.
      num_colors: Number of colors used in the solution.
      solution: The SAT solver solution returned by pycosat.solve.
  """
    print("Vertex coloring solution:")
    for vertex in range(1, len(vertices) + 1):
        for color in range(1, num + 1):
            if (vertex - 1) * num + color in solution:
                print(f"Vertex {vertex}: Color {color}")


graph_file = "instances/ex.col"
edges,vertices = dimacs_to_graph(graph_file)

#Part 1
k=4
is_colorable,solution=check_vertex_coloring(vertices,edges,k)
if(is_colorable):
    print("SATISFIABLE with given k:",k)
    print_solution(vertices,k)
else:
    print("UNSATIFIABLE with given k:",k)
    

# Part2
chromatic_num, solution = find_chromatic_number(vertices, edges)
if chromatic_num:
    print("Chromatic number:", chromatic_num)
    print_solution(vertices,chromatic_num)
