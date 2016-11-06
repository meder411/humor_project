import string
replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
z = 'print.this.out.with.spaces'
print z.translate(replace_punctuation)
