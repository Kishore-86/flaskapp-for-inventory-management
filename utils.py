import random

def generate_id(prefix):
    return f"{prefix}{random.randint(1000,9999)}"
