from ga import GA

sample = GA(input_file="sample.csv", population_size=50)
sample.run(new_gen_size=100)