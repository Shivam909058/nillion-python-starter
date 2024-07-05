from nada_dsl import *

def nada_main():
    # Define parties
    party1 = Party(name="Party1")
    party2 = Party(name="Party2")
    party3 = Party(name="Party3")

    # Define inputs
    a = SecretInteger(Input(name="A", party=party1))
    b = SecretInteger(Input(name="B", party=party2))
    c = SecretInteger(Input(name="C", party=party3))  # Constant as input from party3

    # Perform computation (a * b + c)
    product = a * b
    result = product + c

    # Define output
    return [Output(result, "my_output", party3)]
