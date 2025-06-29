---
title: Research presentations
---

Here is an incomplete sample of some research presentations I have given.

<h2><a href="{{site.url}}/files/talks/structure_in_time.pdf" class="iwantyoubold">Enforcing conservation laws and dissipation inequalities numerically via auxiliary variables</a></h2>

<p>Related coauthors: Boris Andrews, Mingdong He, Kaibo Hu</p>

<p>We propose a general strategy for enforcing multiple conservation laws and dissipation inequalities in the numerical solution of initial value problems. The key idea is to represent each conservation law or dissipation inequality by means of an associated test function; we introduce auxiliary variables representing the projection of these test functions onto a discrete test set,
and modify the equation to use these new variables. </p>

<p>We demonstrate these ideas by their application to the several problems, including the Kepler and Kovalevskaya problems, the Benjamin-Bona-Mahony equation, and the Navier-Stokes equations. In particular, we generalize to arbitrary order the energy-dissipating and
helicity-tracking scheme of Rebholz for the incompressible Navier-Stokes equations, and devise the
first time discretization of the compressible equations that conserves mass, momentum, and energy,
and provably dissipates entropy.</p>


<h2><a href="{{site.url}}/files/talks/multicomponent_flows.pdf" class="iwantyoubold">Discretising the Navier-Stokes-Onsager-Stefan-Maxwell equations of multicomponent flow</a></h2>

<p>Related coauthors: Charles Monroe, Alexander Van-Brunt, Francis Aznaran, Kars Knook, Aaron Baier-Reinio</p>

<p>Multicomponent fluids are mixtures of distinct chemical species (i.e. components) that interact through complex physical processes such as cross-diffusion and chemical reactions. Additional physical phenomena often must be accounted for when modelling these fluids; examples include momentum transport, thermal effects, and (for charged species) electrical effects.</p>

<p>Despite the ubiquity of chemical mixtures in nature and engineering, multicomponent fluids have received very little attention from the finite element community, with many important applications remaining out of reach from numerical methods currently available in the literature.</p>

<p>In this talk, we present a novel class of high-order finite element methods for simulating cross-diffusion and momentum transport (i.e. convection) in multicomponent fluids modelled with the Navier-Stokes-Onsager-Stefan-Maxwell equations. Our model can also incorporate local electroneutrality when the species carry electrical charge, making the numerical methods particularly desirable for simulating liquid electrolytes in electrochemical applications. We discuss challenges that arise when discretising the partial differential equations of multicomponent flow, as well as some salient theoretical properties of our numerical schemes.</p>

<p>We present numerical simulations involving (i) the microfluidic non-ideal mixing of hydrocarbons and (ii) the transient evolution of a lithium-ion battery electrolyte in a Hull cell electrode. </p>

<h2><a href="{{site.url}}/files/talks/reynolds_robust_solvers.pdf" class="iwantyoubold">Reynolds-robust solvers for incompressible flow problems</a></h2>

<p>Related coauthors: Florian Wechsung, Ridgway Scott, Lawrence Mitchell, Fabian Laakmann, Alexei Gazca</p>

 <p>When approximating PDEs with the finite element method, large sparse linear systems must be solved. The ideal preconditioner yields convergence that is algorithmically optimal and parameter robust, i.e. the number of Krylov iterations required to solve the linear system to a given accuracy does not grow substantially as the mesh or problem parameters are changed.</p>

<p>Achieving this for the stationary Navier--Stokes has proven challenging: LU factorisation is Reynolds-robust but scales poorly with degree of freedom (dof) count, while Schur complement approximations such as PCD and LSC degrade as the Reynolds number is increased.</p>

<p>Building on the seminal work of Schöberl, Olshanskii, and Benzi, in this talk we present a novel preconditioner for the Newton linearisation of the stationary Navier--Stokes equations in three dimensions that achieves both Reynolds robustness and optimal complexity in dof count at low orders. The exact details of the preconditioner varies with discretisation, but the general theme is to combine augmented Lagrangian stabilisation, a custom multigrid prolongation operator involving local solves on coarse cells, and an additive patchwise relaxation on each level that captures the kernel of the divergence operator.</p>

<p>We present simulations with robust performance over Reynolds numbers 10 to 10000, several orders of magnitude better than what was previously possible. We also present an extension to a system of equations arising in the magnetohydrodynamics of liquid metals.</p>

<h2><a href="{{site.url}}/files/talks/deflation.pdf" class="iwantyoubold">Computing multiple solutions of nonlinear problems</a></h2>

<p>Related coauthors: Ásgeir Birkisson, Casper Beentjes, Simon Funke, Jon Chapman, Panos Kevrekidis, Matteo Croci, Thomas Surowiec, Saullo Castro, Jingmin Xia</p>

<p>Many nonlinear problems exhibit multiple solutions-think of an umbrella
inverted by the wind, a light switch, or a child's seesaw.
Computing the distinct solutions of a nonlinear problem as its
parameters are varied is a central task in applied
mathematics and engineering. The solutions are captured in a bifurcation
diagram, plotting (some functional of) the solutions as a function of the parameters. In this
talk I will present a new algorithm, deflated continuation, for this task.</p>

<p>Deflated continuation has three advantages. First, it is capable of computing
disconnected bifurcation diagrams; previous algorithms only aimed to compute
that part of the bifurcation diagram continuously connected to the initial data.
Second, its implementation is very simple: it only requires a minor
modification to an existing Newton-based solver. Third, it can scale to very
large discretisations if a good preconditioner is available; no auxiliary
problems must be solved.</p>

<p>We present applications to hyperelastic structures, singularly perturbed problems,
and Bose-Einstein condensates, among others. </p>

<h2><a href="{{site.url}}/files/talks/fast_riesz_maps_simplices.pdf" class="iwantyoubold">Fast high-order solvers on simplices for the de Rham complex</a></h2>

<p>Related coauthors: Pablo Brubeck, Robert Kirby, Charles Parker</p>

<p>We present new finite elements for solving the Riesz maps of the de Rham complex on triangular and tetrahedral meshes at high order. The finite elements discretize the same spaces as usual, but with different basis functions, so that the resulting matrices have desirable properties. These properties mean that we can solve the Riesz maps to a given accuracy in a 𝑝-robust number of iterations with 𝒪(𝑝⁶) flops in three dimensions, rather than the naive 𝒪(𝑝⁹) flops.</p>

<p>The degrees of freedom build upon an idea of Demkowicz et al., and consist of integral moments on an equilateral reference simplex with respect to a numerically computed polynomial basis that is orthogonal in two different inner products. As a result,  the interior-interface and interior-interior couplings are provably weak, and we devise a preconditioning strategy by neglecting them.</p>

<p>The combination of this approach with a space decomposition method on vertex and edge star patches allows us to efficiently solve the canonical Riesz maps at high order.
We apply this to solving the Hodge Laplacians of the de Rham complex with novel augmented Lagrangian preconditioners.</p>
