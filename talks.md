---
title: Research presentations
---

Here is an incomplete sample of research presentations, to give an idea of the kind of research I do.

<h2><a href="{{site.url}}/files/talks/structure_in_time.pdf">Enforcing conservation laws and dissipation inequalities numerically via auxiliary variables</a></h2>

<p>Related authors: Boris Andrews</p>

<p>We propose a general strategy for enforcing multiple conservation laws and dissipation inequalities in the numerical solution of initial value problems. The key idea is to represent each conservation law or dissipation inequality by means of an associated test function; we introduce auxiliary variables representing the projection of these test functions onto a discrete test set,
and modify the equation to use these new variables. We demonstrate these ideas by their application to the Navier-Stokes equations. We generalize to arbitrary order the energy-dissipating and
helicity-tracking scheme of Rebholz for the incompressible Navier-Stokes equations, and devise the
first time discretization of the compressible equations that conserves mass, momentum, and energy,
and provably dissipates entropy.</p>


<h2><a href="{{site.url}}/files/talks/multicomponent_flows.pdf">Discretising the Navier-Stokes-Onsager-Stefan-Maxwell equations of multicomponent flow</a></h2>

<p>Related authors: Charles Monroe, Alexander Van-Brunt, Francis Aznaran, Kars Knook, Aaron Baier-Reinio</p>

<p>Multicomponent fluids are mixtures of distinct chemical species (i.e. components) that interact through complex physical processes such as cross-diffusion and chemical reactions. Additional physical phenomena often must be accounted for when modelling these fluids; examples include momentum transport, thermal effects, and (for charged species) electrical effects.

Despite the ubiquity of chemical mixtures in nature and engineering, multicomponent fluids have received very little attention from the finite element community, with many important applications remaining out of reach from numerical methods currently available in the literature.

In this talk, we present a novel class of high-order finite element methods for simulating cross-diffusion and momentum transport (i.e. convection) in multicomponent fluids modelled with the Navier-Stokes-Onsager-Stefan-Maxwell equations. Our model can also incorporate local electroneutrality when the species carry electrical charge, making the numerical methods particularly desirable for simulating liquid electrolytes in electrochemical applications. We discuss challenges that arise when discretising the partial differential equations of multicomponent flow, as well as some salient theoretical properties of our numerical schemes.

We present numerical simulations involving (i) the microfluidic non-ideal mixing of hydrocarbons and (ii) the transient evolution of a lithium-ion battery electrolyte in a Hull cell electrode. </p>

