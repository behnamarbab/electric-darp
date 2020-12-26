from ga import GA

test_sheets = ["5passenger parameters", "10passenger parameters", "20passenger parameters", "240passenger parameters"]

print("Enter ID:")
for i in range(len(test_sheets)):
    print('{}: {}'.format(i, test_sheets[i]))

sheet_num = int(input())

test1 = GA(input_file="testinstance.xlsx", parameters_sheet=test_sheets[sheet_num], population_size=50)
test1.run(iterations=1000, new_gen_size=40)

# test1 = GA(input_file="testinstance.xlsx", parameters_sheet=test_sheets[0], population_size=50)
# test1.run(iterations=1000, new_gen_size=40)

# test2 = GA(input_file="testinstance.xlsx", parameters_sheet=test_sheets[1], population_size=50)
# test2.run(iterations=1000, new_gen_size=40)

# test3 = GA(input_file="testinstance.xlsx", parameters_sheet=test_sheets[2], population_size=50)
# test3.run(iterations=1000, new_gen_size=40)

