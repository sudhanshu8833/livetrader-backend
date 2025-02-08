import time

def measure_time(comparison_func, iterations=1000000, runs=10):
    times = []
    for _ in range(runs):
        start_time = time.time()
        for _ in range(iterations):
            comparison_func()
        times.append(time.time() - start_time)
    return sum(times) / len(times)

# Integer comparison function
def int_comparison():
    if 12345 == 12345:
        pass

# String comparison function
def string_comparison():
    if "12345" == "12345":
        pass

# Measure average time for integer comparison
int_comparison_time = measure_time(int_comparison)

# Measure average time for string comparison
string_comparison_time = measure_time(string_comparison)

print(f"Average integer comparison time: {int_comparison_time}")
print(f"Average string comparison time: {string_comparison_time}")