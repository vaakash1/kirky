import pstats
stats = pstats.Stats('example_fractions.prof')
stats.sort_stats('tottime')
stats.print_stats(100)