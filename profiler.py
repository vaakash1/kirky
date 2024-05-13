import cProfile
import example

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    # Run your code here
    example.run()

    profiler.disable()
    profiler.dump_stats('example_fractions.prof')
