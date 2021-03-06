from algorithm.individual import IndividualMRP
from algorithm.parameter import *
from algorithm.operator import *
from algorithm.moea import MultiObjectiveEvolutionaryAlgorithm as MOEA
from nsga2 import IndividualNSGA


import random
import copy
import numpy as np

class ProbabilityVector(object):
    
    def __init__(self, learn_rate=None, shift=None):
        self.vector = []
        self.learn_rate = learn_rate
        self.shift = shift
        
    def copy(self):
        pv = ProbabilityVector()
        pv.vector = copy.copy(self.vector)
        pv.learn_rate = self.learn_rate
        pv.shift = self.shift
        return pv
    
    def init_pv(self, length):
        # initialize probability is 0.5.
        self.vector = [0.5 for i in range(length)]
            
    def update_vector(self, chromosome):
        for i in range(len(self.vector)):
            tmp = self.vector[i] * (1 - self.learn_rate) + chromosome[i] * self.learn_rate
            if random.uniform(0, 1) < PM:
                tmp = tmp * (1 - self.shift) + random.randint(0,1) * self.shift
            self.vector[i] = tmp
    
    def generate_chromosome(self):
        chromosome = [1 if random.uniform(0, 1) < p else 0 for p in self.vector]
        return chromosome


'''
@author Bureerat, Sujin, et al.
@title "Population-Based Incremental Learning for Multiobjective Optimisation."
@date 2007
'''
class SubPopulation(object):
    
    def __init__(self, probability_vector):
        self.pv = probability_vector
        self.population = []
        
    def create_sub_population(self, sub_popsize, problem):
        for i in range(sub_popsize):
            ind = IndividualNSGA()
            ind.init_ind(problem=problem)
            self.population.append(ind)
    
    def update_sub_population(self):
        for ind in self.population:
            chromosome = self.pv.generate_chromosome()
            ind.cal_fitness(chromosome)


class PopulationBasedIncrementalLearning(MOEA):
    
    def __init__(self, problem):
        super(PopulationBasedIncrementalLearning, self).__init__(problem=problem)
        self.num_sub = 5
        self.sub_populations = []
        # self.grid = AdaptiveGrid(grid_size=int(EXTERNAL_ARCHIVE_SIZE/2))
        self.external_archive = []

    def name(self):
        return 'PBIL'
        
    def init_population(self):
        for i in range(self.num_sub):
            pv = ProbabilityVector(learn_rate=0.5, shift=0.02)
            pv.init_pv(self.problem.num_link)
            sub = SubPopulation(pv)
            sub.create_sub_population(10, self.problem)
            self.sub_populations.append(sub)
            self.current_population.extend(sub.population)

            for ind in sub.population:
                # self.grid.update_grid(ind)
                self.update_archive(ind)

    def update_archive(self, ind):
        if len(self.external_archive) == 0:
            self.external_archive.append(ind)
        else:
            flag = 0
            for sol in self.external_archive[:]:
                if ind <= sol:
                    self.external_archive.remove(sol)
                elif ind >= sol or ind == sol:
                    flag += 1
            if flag == 0:
                self.external_archive.append(ind)

    def update_pv_by_mean(self):
        # select_number = random.randint(1, len(self.external_archive.archive)-2)
        select_number = random.randint(1, len(self.external_archive)-2)
        # select_lst = np.random.randint(0, len(self.external_archive.archive)-1, size=select_number)
        select_lst = np.random.randint(0, len(self.external_archive)-1, size=select_number)
        means = np.zeros(self.problem.num_link, dtype=int)

        for i in select_lst:
            # means += np.array(self.grid.archive[i].solution.chromosome)
            means += np.array(self.external_archive[i].solution.chromosome)

        means /= select_number

        for sub in self.sub_populations:
            sub.pv.update_vector(means)
            sub.update_sub_population()

            for ind in sub.population:
                # self.grid.update_grid(ind)
                self.update_archive(ind)

    def update_pv_by_weight_sum(self):
        ran = random.uniform(0,1)
        weight_vector = [ran, 1-ran]
        fit_list = []
        # for cube in self.grid.archive:
        for ind in self.external_archive:
            # ind= cube.solution
            fit = ind.fitness[0] * weight_vector[0] + ind.fitness[1] * weight_vector[1]
            fit_list.append(fit)
        
        index_select = fit_list.index(min(fit_list))
        # ind_select = self.grid.archive[index_select].solution
        ind_select = self.external_archive[index_select]

        for sub in self.sub_populations:
            sub.pv.update_vector(ind_select.chromosome)
            sub.update_sub_population()

            for ind in sub.population:
                # self.grid.update_grid(ind)
                self.update_archive(ind)

    
    def run(self):
        self.init_population()

        gen = 0
        while gen < MAX_NUMBER_FUNCTION_EVAL:
            # self.update_pv_by_weight_sum()
            self.update_pv_by_weight_sum()

            gen += 1
        
        # return self.grid.get_solutions()
        return self.external_archive

    
'''
@author Jong-Hwan Kim, et al.
@title "Evolutionary Multi-Objective Optimization in Robot Soccer System for Education."
@date 2009
'''
class MultiObjectivePopulationBasedIncrementalLearning(MOEA):
    
    def __init__(self, problem):
        super(MultiObjectivePopulationBasedIncrementalLearning, self).__init__(problem)
        self.pv_list = []
    
    def init_population(self):
        for i in range(POPULATION_SIZE):
            pv = ProbabilityVector()
            pv.init_pv(self.problem.num_link)
            self.pv_list.append(pv)
            ind = IndividualMRP()
            ind.init_ind(problem=self.problem)
            self.current_population.append(ind)
            
    def update_archive(self):
        union_set = []
        union_set.extend(self.current_population)
        union_set.extend(self.external_archive)
        
        self.external_archive = []
        self.external_archive.extend(fast_nondominated_sort(union_set)[0])
        
        if len(self.external_archive) > EXTERNAL_ARCHIVE_SIZE:
            neighbor_distance_set = []
            
            for ind in self.external_archive:
                neighbor_distance = []
                for bhd in self.external_archive:
                    neighbor_distance.append(ind.distance_to(bhd))
                
                neighbor_distance.sort()
                neighbor_distance_set.append(neighbor_distance[1])
            
            tmp = copy.copy(neighbor_distance_set)
            tmp.sort()
            
            delete_num = EXTERNAL_ARCHIVE_SIZE - len(self.external_archive)
            for i in range(delete_num):
                self.external_archive.pop(neighbor_distance_set.index(tmp[i]))

    def update_pv_by_randomly(self):
        pass

            
    def run(self):
        pass
    


