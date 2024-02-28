import pstats

stats = pstats.Stats('profile_results.prof')
stats.sort_stats(pstats.SortKey.TIME)
stats.print_stats(10)