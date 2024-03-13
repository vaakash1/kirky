import pstats

p = pstats.Stats('long_scipy_example.prof')
p.sort_stats('cumtime').print_stats(15)  # This will print the top 10 functions that took the most time