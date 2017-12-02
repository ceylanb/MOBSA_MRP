"""
@author Zhang, Qingfu, and H. Li.
@title "MOEA/D: A Multiobjective Evolutionary Algorithm Based on Decomposition."
@date 2007)
"""

from algorithm.individual import IndividualMRP
from algorithm.parameter import POPULATION_SIZE, MAX_NUMBER_FUNCTION_EVAL, PC, PM, INF
from problem.mrp.multicast_routing_problem import MulticastRoutingProblem as MRP
from problem.kp.knapsack_problem import MultiObjectiveKnapsackProblem as MOKP
from algorithm.util import write_list_to_json, write_performance, read_json_as_list, plot_ps

import random
import copy
import numpy

class WeightVector(object):

    def __init__(self, NumOfNeighbor):
        self.weight_vector = []
        self.index_neighbor = []
        self.H = float(POPULATION_SIZE - 1)
        self.N = POPULATION_SIZE
        self.T = NumOfNeighbor
        
    '''
    @function for create N weight vectors.
    '''
    def create_weight_vector(self):
        # lambda vector
        lv = numpy.array(range(0, self.N)) / self.H
        for i in range(self.N):
            vector = [lv[i], lv[self.N - i - 1]]
            self.weight_vector.append(vector)
    
    '''
    @function for create each vector's neighbors, due to the distance od two vector
    '''
    
    def create_neighborhood(self):
        for vec in self.weight_vector:
            neighbor = []
            distance = []
            for tem in self.weight_vector:
                distance.append(numpy.linalg.norm(numpy.array(vec) - numpy.array(tem)))
            
            temp = copy.copy(distance)
            temp.sort()
            
            for i in range(self.T):
                neighbor.append(distance.index(temp[i]))
                distance[distance.index((temp[i]))] = 12
            
            self.index_neighbor.append(neighbor)
    
    def initialize_vector(self):
        self.create_weight_vector()
        self.create_neighborhood()
    
class SubProblem(object):
    '''
    The sub_problem in MOEA/D
    @member the weight vector
    @member the list of neighbor solutions' index
    @member one solution
    
    '''
    
    def __init__(self, weight_vector, index_neighbor, solution):
        self.weight_vector = weight_vector
        self.index_neighbor = index_neighbor
        self.solution = solution
    
    '''
    @method Weighted Sum Approach, key='WS'
    @method Tchebycheff Approach, key='TF'
    '''
    
    @staticmethod
    def cal_fit(ind, weight_vector, str_func_type, reference_point):
        fit = 0.0
        if str_func_type == 'WS':
            fit += weight_vector[0] * ind.fitness[0] + weight_vector[1] * ind.fitness[1]
        elif str_func_type == 'TF':
            x = weight_vector[0] * abs(ind.fitness[0] - reference_point[0])
            y = weight_vector[1] * abs(ind.fitness[1] - reference_point[1])
            fit = max(x, y)
        return fit
    

class MultiObjectiveEvolutionaryAlgorithmBasedOnDecomposition(object):
    
    def __init__(self, problem):
        self.problem = problem
        self.current_population = []
        self.external_archive = []
        self.reference_point = [INF, INF]
    
    def init_population(self):
        vectors = WeightVector(POPULATION_SIZE/10)
        vectors.initialize_vector()
        for i in range(POPULATION_SIZE):
            ind = IndividualMRP()
            ind.initialize(IndividualMRP.create_chromosome(self.problem.num_link), self.problem)
            
            sub_sol = SubProblem(weight_vector=vectors.weight_vector[i],
                                 index_neighbor=vectors.index_neighbor[i],
                                 solution=ind)
            self.current_population.append(sub_sol)
            self.update_external_archive(ind)
    
    def update_external_archive(self, ind):
        if len(self.external_archive) == 0:
            self.external_archive.append(ind)
        else:
            flag = 0
            for sol in self.external_archive[:]:
                if sol.is_dominated(ind):
                    self.external_archive.remove(sol)
                elif ind.is_dominated(sol) or ind.is_equal(sol):
                    flag += 1
            if flag == 0:
                self.external_archive.append(ind)
    
    def update_reference_point(self, ind):
        tmp = []
        for fit, ref in zip(ind.fitness, self.reference_point):
            tmp.append(fit if fit < ref else ref)
        self.reference_point = tmp
    
    def reproduction(self, ind):
        index1 = 0
        index2 = 0
        while index1 == index2:
            index1 = random.randint(0, len(ind.index_neighbor)-1)
            index2 = random.randint(0, len(ind.index_neighbor)-1)
        
        ind1 = self.current_population[ind.index_neighbor[index1]].solution.copy()
        ind2 = self.current_population[ind.index_neighbor[index2]].solution.copy()
        
        if random.random() < PC:
            ind1.crossover(ind2)
        
        ind1.mutation()
        ind2.mutation()
        
        if ind1.is_dominated(ind2):
            return ind2
        elif ind2.is_dominated(ind2):
            return ind1
        else:
            return ind1 if random.random() < 0.5 else ind2
    
    def update_neighbor_solution(self, new_solution, ind):
        for i in ind.index_neighbor:
            ind_select = self.current_population[i]
            fit1 = ind.cal_fit(new_solution, ind_select.weight_vector,
                               'TCHEBYCHEFF', self.reference_point)
            fit2 = ind.cal_fit(ind_select.solution, ind_select.weight_vector,
                               'TCHEBYCHEFF', self.reference_point)
            
            if fit1 < fit2:
                ind_select.solution = new_solution.copy()
    
    def main(self):
        self.init_population()
        
        gen = 0
        while gen < MAX_NUMBER_FUNCTION_EVAL:
            print 'Gen >>> ', gen
            for ind in self.current_population:
                new_solution = self.reproduction(ind)
                self.update_reference_point(new_solution)
                self.update_neighbor_solution(new_solution, ind)
                self.update_external_archive(new_solution)
                
            gen += 1
        

if __name__ == '__main__':
    pass
    
    
    
    