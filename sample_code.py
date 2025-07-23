def calculate_area(length, width):
    """Calculate the area of a rectangle."""
    if length <= 0 or width <= 0:
        raise ValueError("Length and width must be positive")
    return length * width

def calculate_perimeter(length, width):
    """Calculate the perimeter of a rectangle."""
    return 2 * (length + width)

def greet(name):
    """Greet a person by name."""
    print(f"Greeting: {name}")
    return f"Hello, {name}!"