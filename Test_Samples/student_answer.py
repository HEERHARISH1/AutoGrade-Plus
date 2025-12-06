import math

def calculate_stats(numbers):
    if not numbers:
        return None
    
    # Calculate Mean
    mean = sum(numbers) / len(numbers)
    
    # Calculate Median
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    if n % 2 == 1:
        median = sorted_nums[n // 2]
    else:
        # BUG: Taking the upper middle element instead of average of two middle elements
        median = sorted_nums[n // 2] 
        
    # Calculate Standard Deviation
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    std_dev = math.sqrt(variance)
    
    return {
        'mean': round(mean, 2),
        'median': round(median, 2),
        'std_dev': round(std_dev, 2)
    }
