import math
from main import calculate_pi_to_5th_digit


def test_pi_calculation():
    """Test the calculate_pi_to_5th_digit function"""
    
    # Calculate pi using our function
    calculated_pi = calculate_pi_to_5th_digit()
    
    # The actual value of pi to 5 decimal places
    expected_pi = 3.14159
    
    # Test 1: Check if our calculated value matches the expected value
    print(f"Calculated pi: {calculated_pi}")
    print(f"Expected pi:   {expected_pi}")
    print(f"Match: {calculated_pi == expected_pi}")
    
    # Test 2: Compare with Python's math.pi (rounded to 5 decimal places)
    math_pi_rounded = round(math.pi, 5)
    print(f"Math.pi rounded: {math_pi_rounded}")
    print(f"Matches math.pi: {calculated_pi == math_pi_rounded}")
    
    # Test 3: Check the difference between our calculation and math.pi
    difference = abs(calculated_pi - math.pi)
    print(f"Difference from math.pi: {difference}")
    print(f"Difference < 1e-5: {difference < 1e-5}")
    
    # Test 4: Verify the result is properly rounded to 5 decimal places
    decimal_places = len(str(calculated_pi).split('.')[1])
    print(f"Number of decimal places: {decimal_places}")
    print(f"Has exactly 5 decimal places: {decimal_places == 5}")
    
    # Overall test result
    success = (calculated_pi == expected_pi and 
               calculated_pi == math_pi_rounded and 
               difference < 1e-5 and 
               decimal_places == 5)
    
    print(f"\nAll tests passed: {success}")
    return success


def test_precision():
    """Test that our function is accurate enough"""
    calculated_pi = calculate_pi_to_5th_digit()
    
    # Test against known digits of pi
    pi_digits = "3.14159265358979323846"
    our_digits = str(calculated_pi)
    
    print(f"\nPrecision test:")
    print(f"Known pi:      {pi_digits[:7]}")  # First 5 decimal places
    print(f"Calculated pi: {our_digits}")
    
    # Check if first 6 characters match (3.14159)
    matches = our_digits == pi_digits[:7]
    print(f"First 5 decimal places correct: {matches}")
    
    return matches


if __name__ == "__main__":
    print("Testing pi calculation function...\n")
    
    # Run the main test
    main_test_passed = test_pi_calculation()
    
    # Run precision test
    precision_test_passed = test_precision()
    
    print(f"\n{'='*50}")
    print(f"FINAL RESULTS:")
    print(f"Main test passed: {main_test_passed}")
    print(f"Precision test passed: {precision_test_passed}")
    print(f"Overall success: {main_test_passed and precision_test_passed}")