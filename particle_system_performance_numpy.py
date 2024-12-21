from particle_system import ParticleSystem
import timeit


def benchmark_chunk_sizes(num_particles: list[int], iterations: int = 10):
    """
    Benchmarks the performance of move_particles with different chunk sizes.
    
    Parameters:
        particle_system (ParticleSystem): The particle system object.
        chunk_sizes (list of tuples): List of (x_chunk, y_chunk) sizes to test.
        iterations (int): Number of iterations for timeit.
    
    Returns:
        dict: A dictionary mapping chunk sizes to average execution time.
    """
    for num in num_particles:
        particle_system = ParticleSystem(width=1000, height=1000, color_distribution=[((255, 0, 0), num), ((0, 255, 0), num)])


        def test_move_particles():
            particle_system.move_particles()
        
        exec_time = timeit.timeit(test_move_particles, number=iterations)
        avg_time = exec_time / iterations
        print(f"{avg_time:.6f} seconds for moving {num*2} particles")
    
    return


if __name__ == "__main__":
    num_particles = [1000, 10000, 100000, 1000000, 10000000]
    benchmark_chunk_sizes(num_particles)