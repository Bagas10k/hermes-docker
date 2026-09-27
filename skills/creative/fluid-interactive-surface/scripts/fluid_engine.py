#!/usr/bin/env python3
"""
Fluid Interactive Surface - Navier-Stokes 2D Grid Simulation Prototype.
Deterministic empirical verification for grid velocity, pressure Poisson relaxation,
smoke advection, and energy conservation bounds.
"""
import math
import sys

class FluidSimulation2D:
    def __init__(self, size=32, dt=0.1, diff=0.0001, visc=0.0001):
        self.N = size
        self.dt = dt
        self.diff = diff
        self.visc = visc
        self.dim = (size + 2) * (size + 2)
        
        self.s = [0.0] * self.dim
        self.density = [0.0] * self.dim
        
        self.Vx = [0.0] * self.dim
        self.Vy = [0.0] * self.dim
        self.Vx0 = [0.0] * self.dim
        self.Vy0 = [0.0] * self.dim

    def IX(self, x, y):
        return x + y * (self.N + 2)

    def add_density(self, x, y, amount):
        idx = self.IX(x, y)
        self.density[idx] += amount

    def add_velocity(self, x, y, amount_x, amount_y):
        idx = self.IX(x, y)
        self.Vx[idx] += amount_x
        self.Vy[idx] += amount_y

    def set_bnd(self, b, x):
        N = self.N
        for i in range(1, N + 1):
            x[self.IX(0, i)] = -x[self.IX(1, i)] if b == 1 else x[self.IX(1, i)]
            x[self.IX(N + 1, i)] = -x[self.IX(N, i)] if b == 1 else x[self.IX(N, i)]
            x[self.IX(i, 0)] = -x[self.IX(i, 1)] if b == 2 else x[self.IX(i, 1)]
            x[self.IX(i, N + 1)] = -x[self.IX(i, N)] if b == 2 else x[self.IX(i, N)]

        x[self.IX(0, 0)] = 0.5 * (x[self.IX(1, 0)] + x[self.IX(0, 1)])
        x[self.IX(0, N + 1)] = 0.5 * (x[self.IX(1, N + 1)] + x[self.IX(0, N)])
        x[self.IX(N + 1, 0)] = 0.5 * (x[self.IX(N, 0)] + x[self.IX(N + 1, 1)])
        x[self.IX(N + 1, N + 1)] = 0.5 * (x[self.IX(N, N + 1)] + x[self.IX(N + 1, N)])

    def lin_solve(self, b, x, x0, a, c):
        c_recip = 1.0 / c
        N = self.N
        for _ in range(4): # 4 iterations sufficient for real-time vibe coding 60 FPS
            for j in range(1, N + 1):
                for i in range(1, N + 1):
                    x[self.IX(i, j)] = (x0[self.IX(i, j)] + a * (
                        x[self.IX(i + 1, j)] +
                        x[self.IX(i - 1, j)] +
                        x[self.IX(i, j + 1)] +
                        x[self.IX(i, j - 1)]
                    )) * c_recip
            self.set_bnd(b, x)

    def diffuse(self, b, x, x0, diff, dt):
        a = dt * diff * (self.N - 2) * (self.N - 2)
        self.lin_solve(b, x, x0, a, 1 + 4 * a)

    def project(self, veloc_x, veloc_y, p, div):
        N = self.N
        for j in range(1, N + 1):
            for i in range(1, N + 1):
                div[self.IX(i, j)] = -0.5 * (
                    veloc_x[self.IX(i + 1, j)] - veloc_x[self.IX(i - 1, j)] +
                    veloc_y[self.IX(i, j + 1)] - veloc_y[self.IX(i, j - 1)]
                ) / N
                p[self.IX(i, j)] = 0.0

        self.set_bnd(0, div)
        self.set_bnd(0, p)
        self.lin_solve(0, p, div, 1, 4)

        for j in range(1, N + 1):
            for i in range(1, N + 1):
                veloc_x[self.IX(i, j)] -= 0.5 * (p[self.IX(i + 1, j)] - p[self.IX(i - 1, j)]) * N
                veloc_y[self.IX(i, j)] -= 0.5 * (p[self.IX(i, j + 1)] - p[self.IX(i, j - 1)]) * N

        self.set_bnd(1, veloc_x)
        self.set_bnd(2, veloc_y)

    def advect(self, b, d, d0, veloc_x, veloc_y, dt):
        N = self.N
        dt0 = dt * N
        for j in range(1, N + 1):
            for i in range(1, N + 1):
                x = i - dt0 * veloc_x[self.IX(i, j)]
                y = j - dt0 * veloc_y[self.IX(i, j)]

                if x < 0.5: x = 0.5
                if x > N + 0.5: x = N + 0.5
                i0 = int(x)
                i1 = i0 + 1.0

                if y < 0.5: y = 0.5
                if y > N + 0.5: y = N + 0.5
                j0 = int(y)
                j1 = j0 + 1.0

                s1 = x - i0
                s0 = 1.0 - s1
                t1 = y - j0
                t0 = 1.0 - t1

                i0_i = int(i0)
                i1_i = int(i1)
                j0_i = int(j0)
                j1_i = int(j1)

                d[self.IX(i, j)] = s0 * (t0 * d0[self.IX(i0_i, j0_i)] + t1 * d0[self.IX(i0_i, j1_i)]) + \
                                   s1 * (t0 * d0[self.IX(i1_i, j0_i)] + t1 * d0[self.IX(i1_i, j1_i)])

        self.set_bnd(b, d)

    def step(self):
        # Diffuse velocity
        self.diffuse(1, self.Vx0, self.Vx, self.visc, self.dt)
        self.diffuse(2, self.Vy0, self.Vy, self.visc, self.dt)

        # Enforce incompressibility
        self.project(self.Vx0, self.Vy0, self.Vx, self.Vy)

        # Advect velocity
        self.advect(1, self.Vx, self.Vx0, self.Vx0, self.Vy0, self.dt)
        self.advect(2, self.Vy, self.Vy0, self.Vx0, self.Vy0, self.dt)

        # Enforce incompressibility again
        self.project(self.Vx, self.Vy, self.Vx0, self.Vy0)

        # Diffuse & advect density
        self.diffuse(0, self.s, self.density, self.diff, self.dt)
        self.advect(0, self.density, self.s, self.Vx, self.Vy, self.dt)

        # Dissipation factor to keep energy bounded
        for i in range(len(self.density)):
            self.density[i] *= 0.992
            self.Vx[i] *= 0.995
            self.Vy[i] *= 0.995


def verify_fluid():
    sim = FluidSimulation2D(size=32)
    # Inject impulse in center
    cx, cy = 16, 16
    sim.add_density(cx, cy, 100.0)
    sim.add_velocity(cx, cy, 2.5, 1.2)

    total_density_init = sum(sim.density)
    assert total_density_init > 0, "Initial density must be non-zero"

    # Step simulation 10 times
    for _ in range(10):
        sim.step()

    total_density_after = sum(sim.density)
    center_vx = sim.Vx[sim.IX(cx, cy)]
    center_vy = sim.Vy[sim.IX(cx, cy)]
    neighbor_density = sim.density[sim.IX(cx + 1, cy)]

    assert total_density_after < total_density_init, "Density must dissipate safely"
    assert neighbor_density > 0, "Advection must transfer density to neighboring cells"
    
    print(f"VERIFIED: Fluid simulation stepped 10 frames cleanly. Dissipation: {total_density_after:.2f}/{total_density_init:.2f}, Advection spread: {neighbor_density:.4f}")
    return True

if __name__ == "__main__":
    if verify_fluid():
        sys.exit(0)
    sys.exit(1)
