function output_vars = main
  % Index sets
  % Nodes
  N = cell(1, 4);
  N(1)  = 1;
  N(2)  = 2;
  N(3)  = 3;
  N(4)  = 4;
  N_lbl = "N";
  % Nodes & Species
  NS = cell(1, 4);
  NS(1)  = [1];
  NS(2)  = [2];
  NS(3)  = [1, 2];
  NS(4)  = [1, 2];
  NS_lbl = "NS";
  % Arcs
  A = cell(1, 3);
  A(1)  = 1;
  A(2)  = 2;
  A(3)  = 3;
  A_lbl = "A";
  % Arcs & Species
  AS = cell(1, 3);
  AS(1)  = [1];
  AS(2)  = [2];
  AS(3)  = [1, 2];
  AS_lbl = "AS";
  % Species
  S = cell(1, 3);
  S(1)  = 1;
  S(2)  = 2;
  S(3)  = 3;
  S_lbl = "S";

  % Variables
  % initial condition for species mass in nodes
  value = zeros(6, 1);
  value(5) = n41;
  value(6) = n42;
  no = MultiDimVar(value, {NS_lbl}, {NS});

  % end time
  te = te;

  % starting time
  to = to;

  % net diffusional mass transfer
  value = zeros(6, 1);
  value(5) = zero;
  value(6) = zero;
  fnd = MultiDimVar(value, {NS_lbl}, {NS});

  % production term
  value = zeros(6, 1);
  value(5) = zero;
  value(6) = zero;
  pn = MultiDimVar(value, {NS_lbl}, {NS});

  % incidence matrix of directed graphs for for species NS x AS
  rows = [1, 5, 2, 6, 5, 3, 6, 4];
  cols = [1, 1, 3, 3, 5, 5, 6, 6];
  vals = [-1, 1, -1, 1, -1, 1, -1, 1];
  value = sparse(rows, cols, vals, 6, 6);
  Fc_NS_AS = MultiDimVar(value, {NS_lbl, AS_lbl}, {NS, AS});

  % thermodynamic pressure
  value = zeros(4, 1);
  value(2) = p2;
  value(3) = p3;
  value(1) = p1;
  p = MultiDimVar(value, {N_lbl}, {N});

  % difference operator
  rows = [1, 4, 2, 4, 4, 3];
  cols = [1, 1, 2, 2, 3, 3];
  vals = [-1, 1, -1, 1, -1, 1];
  value = sparse(rows, cols, vals, 4, 3);
  Dc = MultiDimVar(value, {N_lbl, A_lbl}, {N, A});

  % valve constant
  value = zeros(3, 1);
  value(2) = cv2;
  value(3) = cv3;
  value(1) = cv1;
  cv_A = MultiDimVar(value, {A_lbl}, {A});

  % molar concentration
  value = zeros(6, 1);
  value(2) = c21;
  value(3) = c31;
  value(4) = c32;
  value(1) = c11;
  c = MultiDimVar(value, {NS_lbl}, {NS});

  % block difference operator
  rows = [1, 5, 2, 6, 5, 3, 6, 4];
  cols = [1, 1, 3, 3, 5, 5, 6, 6];
  vals = [-1, 1, -1, 1, -1, 1, -1, 1];
  value = sparse(rows, cols, vals, 6, 6);
  Dc_NS_AS = MultiDimVar(value, {NS_lbl, AS_lbl}, {NS, AS});

  % numerical value one half
  onehalf = onehalf;

  % 
  value = zeros(4, 1);
  value(4) = zero;
  dEdt = MultiDimVar(value, {N_lbl}, {N});

  % 
  value = zeros(3, 1);
  value(1) = kfa1;
  value(2) = kfa2;
  value(3) = kfa3;
  kf_A = MultiDimVar(value, {A_lbl}, {A});

  % 
  value = zeros(3, 1);
  value(1) = l1;
  value(2) = l2;
  value(3) = l3;
  l_A = MultiDimVar(value, {A_lbl}, {A});

  % mass density
  value = zeros(4, 1);
  value(4) = rho_node4;
  density = MultiDimVar(value, {N_lbl}, {N});

  % 
  g = g;

  % 
  value = zeros(3, 1);
  value(3) = h3;
  value(1) = h1;
  value(2) = h2;
  h_A = MultiDimVar(value, {A_lbl}, {A});

  % species molecular masses
  value = zeros(2, 1);
  value(1) = lambda1;
  value(2) = lambda2;
  Mm = MultiDimVar(value, {S_lbl}, {S});

  % 
  value = zeros(3, 1);
  value(2) = rho_arc2;
  value(3) = rho_arc3;
  value(1) = rho_arc1;
  rho_A = MultiDimVar(value, {A_lbl}, {A});

  % 
  value = zeros(3, 1);
  value(2) = A2;
  value(3) = A3;
  value(1) = A1;
  A_A = MultiDimVar(value, {A_lbl}, {A});

  % species molar mass
  value = zeros(6, 1);
  n = MultiDimVar(value, {NS_lbl}, {NS});

  % differential molar mass balance
  value = zeros(6, 1);
  dndt = MultiDimVar(value, {NS_lbl}, {NS});

  % net convective molar mass flow
  value = zeros(6, 1);
  fnc = MultiDimVar(value, {NS_lbl}, {NS});

  % convective molar mass flow per arc
  value = zeros(6, 1);
  fnc_AS = MultiDimVar(value, {AS_lbl}, {AS});

  % volumetric flow in x-direction
  value = zeros(3, 1);
  fV = MultiDimVar(value, {A_lbl}, {A});

  % moler concentration in convective arc
  value = zeros(6, 1);
  c_AS = MultiDimVar(value, {AS_lbl}, {AS});

  % direction of convective flow
  value = zeros(3, 1);
  d = MultiDimVar(value, {A_lbl}, {A});

  % 
  value = zeros(4, 1);
  Ek = MultiDimVar(value, {N_lbl}, {N});

  % 
  value = zeros(4, 1);
  Ef = MultiDimVar(value, {N_lbl}, {N});

  % 
  value = zeros(4, 1);
  Ep = MultiDimVar(value, {N_lbl}, {N});

  % 
  value = zeros(4, 1);
  Ev = MultiDimVar(value, {N_lbl}, {N});

  % foundation state -- volume
  value = zeros(4, 1);
  V = MultiDimVar(value, {N_lbl}, {N});

  % 
  value = zeros(3, 1);
  Ek_A = MultiDimVar(value, {A_lbl}, {A});

  % 
  value = zeros(3, 1);
  Ep_A = MultiDimVar(value, {A_lbl}, {A});

  % 
  value = zeros(3, 1);
  Ev_A = MultiDimVar(value, {A_lbl}, {A});

  % mass
  value = zeros(4, 1);
  m = MultiDimVar(value, {N_lbl}, {N});

  % 
  value = zeros(3, 1);
  m_A = MultiDimVar(value, {A_lbl}, {A});

  % 
  value = zeros(3, 1);
  v_A = MultiDimVar(value, {A_lbl}, {A});


  % Integrators
  % Initial conditions
  phi_0(1:2, 1) = no(5:6).value;

  % Integration interval
  integration_interval = [to, te];

  % Integrator routine
  [t, phi] = ode15s(@f, integration_interval, phi_0);

  % Integrand
  function dphidt = f(t, phi) 
    n(5:6) = phi(1:2);

    Ef(4) = E_30(F, kf_A, l_A);

    m(4) = E_23(n, Mm);

    V(4) = E_22(density, m);

    c(5:6) = E_21(n, V);

    sol = system1(Ev_A, dEdt, h_A, F, Ev, p, g, cv_A, Ep_A, A_A, onehalf, fV, P_N_A, Ep, rho_A, Ek, m_A, v_A, Ef, Dc, Ek_A);
    Ev_A(1:3) = sol(1:3);
    Ek_A(1:3) = sol(4:6);
    Ep(4) = sol(7:7);
    Ep_A(1:3) = sol(8:10);
    Ek(4) = sol(11:11);
    v_A(1:3) = sol(12:14);
    p(4) = sol(15:15);
    Ev(4) = sol(16:16);
    m_A(1:3) = sol(17:19);
    fV(1:3) = sol(20:22);

    d(1:3) = E_20(Dc, p);

    c_AS(1:6) = E_19(c, Dc_NS_AS, d, onehalf);

    fnc_AS(1:6) = E_12(fV, c_AS);

    fnc(5:6) = E_5(fnc_AS, Fc_NS_AS);

    dndt(5:6) = E_3(fnd, pn, fnc);

    dphidt(1:2) = dndt(5:6)
  endfunction

end function

% Functions for the equations
function sol = E_30(F, kf_A, l_A)
  sol =  F*(kf_A.*l_A);
endfunction

function sol = E_23(n, Mm)
  sol = blockReduce(Mm, S, N_x_S, n);
endfunction

function sol = E_22(density, m)
  sol = zeros(1);
  sol(1) = fzero(@(x) m .* inv(V) - density(4), Initial_Guess);
endfunction

function sol = E_21(n, V)
  sol = khatriRao(inv(V), [N], n, [N_x_S]);
endfunction

function sol = system1(Ev_A, dEdt, h_A, F, Ev, p, g, cv_A, Ep_A, A_A, onehalf, fV, P_N_A, Ep, rho_A, Ek, m_A, v_A, Ef, Dc, Ek_A)
  sol = fsolve(@sys, )
  function F = sys(x)
    Ev_A(1:3) = x(1:3)
    Ek_A(1:3) = x(4:6)
    Ep(4) = x(7:7)
    Ep_A(1:3) = x(8:10)
    Ek(4) = x(11:11)
    v_A(1:3) = x(12:14)
    p(4) = x(15:15)
    Ev(4) = x(16:16)
    m_A(1:3) = x(17:19)
    fV(1:3) = x(20:22)

    F(1:3) =  -fV* (P_N_A*p)  - Ev_A(1:3)
    F(4:6) =  onehalf*m_A*v_A*v_A - Ek_A(1:3)
    F(7:7) =  F*Ep_A - Ep(4)
    F(8:10) =  m_A*g*h_A - Ep_A(1:3)
    F(11:11) =  F*Ek_A - Ek(4)
    F(12:14) =  fV*inv(A_A) - v_A(1:3)
    F(15:15) =  Ev + Ep + Ek + Ef - dEdt(4)
    F(16:16) =  F*Ev_A - Ev(4)
    F(17:19) =  rho_A*fV - m_A(1:3)
    F(20:22) = cv_A .* (Dc * p) - fV(1:3)
  endfunction
endfunction

function sol = E_20(Dc, p)
  sol = sign(( Dc )'  * p);
endfunction

function sol = E_19(c, Dc_NS_AS, d, onehalf)
  sol = ( (onehalf .* (Dc_NS_AS - khatriRao(d, [A], abs(Dc_NS_AS), [N_x_S, A_x_S]))) )'  * c;
endfunction

function sol = E_12(fV, c_AS)
  sol = khatriRao(fV, [A], c_AS, [A_x_S]);
endfunction

function sol = E_5(fnc_AS, Fc_NS_AS)
  sol = F_NS_AS * fnc_AS;
endfunction

function sol = E_3(fnd, pn, fnc)
  sol = fnc + fnd + pn;
endfunction

