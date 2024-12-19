from particle_system import ParticleSystem
import timeit


def benchmark_chunk_sizes(chunk_sizes: list[tuple[int, int]], num_particles: list[int], iterations: int = 10):
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
        particle_system = ParticleSystem(width=1000, height=1000, color_distribution=[((255, 0, 0), num), ((0, 255, 0), num)], chunk_size=10000)
        
        results = {}

        for x_chunk, y_chunk in chunk_sizes:
            particle_system._particles = particle_system._particles.rechunk((x_chunk, y_chunk))
            
            def test_move_particles():
                particle_system.move_particles()
            
            exec_time = timeit.timeit(test_move_particles, number=iterations)
            avg_time = exec_time / iterations
            results[(x_chunk, y_chunk)] = avg_time
            print(f"Chunks ({x_chunk}, {y_chunk}): {avg_time:.6f} seconds for moving {num*2} particles")
    
    return results


if __name__ == "__main__":
    chunk_sizes = [(100000, 100000), (50000, 50000), (30000, 30000), (20000, 20000), (10000, 10000), (5000, 5000), (2500, 2500), (1250, 1250)]
    num_particles = [1000, 10000, 100000, 1000000, 10000000]
    benchmark_chunk_sizes(chunk_sizes, num_particles)
    
    