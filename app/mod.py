def mod_difference(a, b, ref):
    return ((a - b) % ref)

# Define your numbers and reference number
num2 = 2000
num1 = 2150	

reference = 50

# Calculate the difference between the two numbers in terms of the modulus of the reference number
#diff = mod_difference(num1, num2, reference)

# Print the result
#print(f"The difference between {num1} and {num2} in terms of mod {reference} is {diff}.")
def round_closest_strike(number,ref):
    return round(number / ref) * ref

print(round_closest_strike((2000-24),50))
