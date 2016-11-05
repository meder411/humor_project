from fuzzywuzzy import process

choices = ['i have to eat peas', 'i want to go to the bathroom because i gotta pee', 'i gotta pee, so i went to the bathroom']

print process.extract('i have to pee', choices)
