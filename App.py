import random
from pyeasyga import pyeasyga
import requests
import json

global max_weight
global max_volume

fileName = '11.txt'
contentType = 'application/json'
head = {'content-type': contentType}
url = 'https://cit-home1.herokuapp.com/api/ga_homework'
percent = 0.2
population = 200
mutation_percent = 0.05
change_betwee_population = 0.1
len_of_individual = 30

data = open(fileName).readlines()

first_row = list((map(float, data[0].split())))
max_weight = first_row[0]
max_volume = first_row[1]

data = data[1:]

input_data = []

for i in range(0, len(data)):
    input_data.append(list((map(float, data[i].split()))))
ga = pyeasyga.GeneticAlgorithm(input_data)
ga.population_size = 200


def fitness(individual, data):
    weight, volume, price = 0, 0, 0
    for (selected, item) in zip(individual, data):
        if selected:
            weight += item[0]
            volume += item[1]
            price += item[2]
    if weight > max_weight or volume > max_volume:
        price = 0
    return price


ga.fitness_function = fitness
ga.run()


def choose_data_to_create_json(fitness_result):
    weight = 0
    volume = 0
    items = []
    for i in range(0, len(fitness_result[1])):
        if fitness_result[1][i] == 1:
            items.append(i + 1)
            weight += input_data[i][0]
            volume += input_data[i][1]
    return fitness_result[0], weight, round(volume), items


def get_lib_gen_results():
    return choose_data_to_create_json(ga.best_individual())


def fitness(individual, data):
    weight, volume, price = 0, 0, 0
    for (selected, item) in zip(individual, data):
        if selected:
            weight += item[0]
            volume += item[1]
            price += item[2]
    if weight > max_weight or volume > max_volume:
        price = 0
    return item, price, individual


# 2.1
def selection(first_generation):
    count_price = []
    total_price = 0
    for i in range(0, len(first_generation)):
        count_price.append((fitness(first_generation[i], input_data)))
    #here will be roulette
    return count_price


def crossingover(after_selection):
    forward_generation = []
    for i in range(0, len(after_selection), 2):
        child1, child2 = [], []
        for j in range(0, len(after_selection[i][2])):
            ind = random.randint(0, 1)
            if ind == 1:
                child1.append(after_selection[i][2][j])
                child2.append(after_selection[i + 1][2][j])
            else:
                child2.append(after_selection[i][2][j])
                child1.append(after_selection[i + 1][2][j])
        forward_generation.append(child1)
        forward_generation.append(child2)
    return forward_generation


def mutation(make_children_from_individuals):
    for i in range(0, int(len(make_children_from_individuals) * mutation_percent)):
        ind = random.randint(0, len(make_children_from_individuals) - 1)
        number = random.randint(0, 30)
        if make_children_from_individuals[ind][number] == 1:
            make_children_from_individuals[ind][number] = 0
        else:
            make_children_from_individuals[ind][number] = 1
    return make_children_from_individuals


def exchange_old_new_population(old_population, new_population):
    old_population.sort(key=lambda i: float(i[1]))
    new_population.sort(key=lambda i: float(i[1]), reverse=True)
    for i in range(0, len(new_population)):
        old_population[i] = new_population[i][2]
    return old_population


def generate_second():
    first_population = []
    for i in range(0, population):
        individ = []
        for i in range(0, len_of_individual):
            individ.append(int(round(random.random())))
        first_population.append(individ)
    num_of_population = 0
    while num_of_population < 100:
        sel = selection(first_population)
        new_individ = mutation(crossingover(sel))
        forward_gen = selection(new_individ)
        new_population = exchange_old_new_population(first_population, forward_gen)
        new_sel = selection(new_population)
        for i in range(0, len(new_population)):
            first_population[i] = new_population[i]
        if abs(sel[0][1] - new_sel[0][1]) < new_sel[0][1] * change_betwee_population:
            break
        num_of_population = num_of_population + 1
    weight, volume, price = 0, 0, 0
    for (selected, item) in zip(first_population[0], input_data):
        if selected:
            weight += int(item[0])
            volume += int(item[1])
            price += int(item[2])
    if weight > max_weight or volume > max_volume:
        price = 0
    items = []
    for i in range(0, len(first_population[0])):
        if first_population[0][i] == 1:
            items.append(i)
    return price, weight, volume, items


if __name__ == '__main__':
    first = get_lib_gen_results()
    second = generate_second()
    post = requests.post(url, data=json.dumps({
        '1': {'value': int(first[0]), 'weight': int(first[1]), 'volume': int(first[2]), 'items': first[3]},
        '2': {'value': int(second[0]), 'weight': int(second[1]), 'volume': int(second[2]), 'items': second[3]}}),
                         headers=head)
    print(post.status_code)
