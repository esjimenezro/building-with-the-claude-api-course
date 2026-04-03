def greeting(name):
    return f"Hello, {name}!"


def calculate_pi_to_5th_digit():
    """
    Calculate pi to the 5th decimal place using the Machin formula:
    π/4 = 4*arctan(1/5) - arctan(1/239)
    
    Returns pi rounded to 5 decimal places: 3.14159
    """
    def arctan_series(x, terms=100):
        """Calculate arctan(x) using Taylor series expansion"""
        result = 0
        x_squared = x * x
        x_power = x
        
        for n in range(terms):
            # Taylor series: arctan(x) = x - x³/3 + x⁵/5 - x⁷/7 + ...
            sign = (-1) ** n
            term = sign * x_power / (2 * n + 1)
            result += term
            x_power *= x_squared
            
            # Break if term becomes negligibly small
            if abs(term) < 1e-15:
                break
                
        return result
    
    # Machin's formula: π/4 = 4*arctan(1/5) - arctan(1/239)
    pi_over_4 = 4 * arctan_series(1/5) - arctan_series(1/239)
    pi_value = 4 * pi_over_4
    
    # Round to 5 decimal places
    return round(pi_value, 5)
