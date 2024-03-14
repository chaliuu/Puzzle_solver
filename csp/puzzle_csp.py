#Look for #IMPLEMENT tags in this file.
'''
All encodings need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = caged_csp(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the FunPuzz puzzle.

The grid-only encodings do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - An enconding of a FunPuzz grid (without cage constraints) built using only 
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - An enconding of a FunPuzz grid (without cage constraints) built using only n-ary 
      all-different constraints for both the row and column constraints. 

3. caged_csp (worth 25/100 marks) 
    - An enconding built using your choice of (1) binary binary not-equal, or (2) 
      n-ary all-different constraints for the grid.
    - Together with FunPuzz cage constraints.
    
note: OpenAI's ChatGPT is used as an aid to draft this code
'''


from cspbase import *
import itertools

def binary_ne_grid(fpuzz_grid):
    N = fpuzz_grid[0][0]  
    csp = CSP("BinaryNEGrid")
    vars = []

   
    for i in range(N):
        row = []
        for j in range(N):
            var = Variable(f'V{i}{j}', range(1, N+1))
            csp.add_var(var)
            row.append(var)
        vars.append(row)
    
   
    for i in range(N):
        for j in range(N):
            for k in range(j+1, N):
                
                row_constraint = Constraint(f"Row_{i}_{j}_{k}", [vars[i][j], vars[i][k]])
                row_constraint.add_satisfying_tuples([(x, y) for x in range(1, N+1) for y in range(1, N+1) if x != y])
                csp.add_constraint(row_constraint)
                
               
                col_constraint = Constraint(f"Col_{j}_{i}_{k}", [vars[j][i], vars[k][i]])
                col_constraint.add_satisfying_tuples([(x, y) for x in range(1, N+1) for y in range(1, N+1) if x != y])
                csp.add_constraint(col_constraint)

    return csp, vars
    

def nary_ad_grid(fpuzz_grid):
    N = fpuzz_grid[0][0]  #get grid size
    csp = CSP("nary_ad_grid")  
    vars = []

    # creating variables for each cell in the grid
    for i in range(N):
        row_vars = []
        for j in range(N):
            var = Variable(f'V{i}{j}', domain=list(range(1, N+1)))
            csp.add_var(var)
            row_vars.append(var)
        vars.append(row_vars)

    # adding constraints for  each row and column
    for i in range(N):
        for j in range(N):
           
            for k in range(j+1, N):
                constraint_row = Constraint(f"C_row_{i}_{j}_{k}", [vars[i][j], vars[i][k]])
                sat_tuples_row = [(x, y) for x in range(1, N+1) for y in range(1, N+1) if x != y]
                constraint_row.add_satisfying_tuples(sat_tuples_row)
                csp.add_constraint(constraint_row)
                
             
                constraint_col = Constraint(f"C_col_{j}_{i}_{k}", [vars[j][i], vars[k][i]])
                sat_tuples_col = [(x, y) for x in range(1, N+1) for y in range(1, N+1) if x != y]
                constraint_col.add_satisfying_tuples(sat_tuples_col)
                csp.add_constraint(constraint_col)

    return csp, vars




def caged_csp(fpuzz_grid):
    N = fpuzz_grid[0][0]  #get grid size
    grid_csp, grid_vars = nary_ad_grid(fpuzz_grid) #create csp n-ary all-different encoding

    # expand to include cage constraint
    for cage_info in fpuzz_grid[1:]:
        cage_operation = cage_info[-1]
        cage_target = cage_info[-2]

        # map cage variables to proper predefined grid position from nary_ad_grid()
        cage_vars = [grid_vars[(num // 10) - 1][num % 10 - 1] for num in cage_info[:-2]]
        possible_values = range(1, N + 1) # e.g [1, 2, 3] if grid size 3

        sat_tuples = []
        #get all possible value combinations for each cage then evaluate valid ones
        for values in itertools.product(possible_values, repeat=len(cage_vars)):

            #calculate helper values for multiplication, division, and subtraction
            multVal = 1
            for val in values:
                multVal =  multVal * val
            
            divVal = 1
            for val in values:
               if val != max(values):
                   divVal = divVal * val

            subVal = 0
            for val in values:
                if val != max(values):
                    subVal += val
            
            #check operations and if values valid
            if cage_operation == 0 and cage_target == sum(values) :  # check addition valid
                sat_tuples.append(values)

            elif cage_operation == 1:  #check subtraction valid
                if cage_target + subVal == max(values):
                    sat_tuples.append(values)

            elif cage_operation == 2:  #check division valid
                if cage_target * divVal == max(values):
                    sat_tuples.append(values)
        
            elif cage_operation == 3 and cage_target == multVal:  # check multiplication
                sat_tuples.append(values)

        # Create and add the cage constraint
        cage_constraint = Constraint(f"Cage-{cage_info[:-2]}", cage_vars)
        cage_constraint.add_satisfying_tuples(sat_tuples)
        grid_csp.add_constraint(cage_constraint)

    return grid_csp, grid_vars
