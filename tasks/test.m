function output_vars = main
  % Index sets
  N = cell(1, 4);
  N(1)  = 1;
  N(2)  = 2;
  N(3)  = 3;
  N(4)  = 4;
  N_lbl = "N";
  N_x_S = cell(1, 4);
  N_x_S(1)  = [1];
  N_x_S(2)  = [2];
  N_x_S(3)  = [1, 2];
  N_x_S(4)  = [1, 2];
  N_x_S_lbl = "N_x_S";
  A = cell(1, 3);
  A(1)  = 1;
  A(2)  = 2;
  A(3)  = 3;
  A_lbl = "A";
  A_x_S = cell(1, 3);
  A_x_S(1)  = [1];
  A_x_S(2)  = [2];
  A_x_S(3)  = [1, 2];
  A_x_S_lbl = "A_x_S";
  S = cell(1, 2);
  S(1)  = 1;
  S(2)  = 2;
  S_lbl = "S";

  N_const = [1, 2, 3];
  N_dyn = [4];
  A_conv = [1, 2, 3];

  % Variables
  % starting time
  to = to;

  % initial condition for species mass in nodes
  no = MultiDimVar({N_x_S_lbl}, {N_x_S});
  no(4) = [n41; n42];
  no = sparse(no);

  % end time
  te = te;

  % net diffusional mass transfer
  fnd = MultiDimVar({N_x_S_lbl}, {N_x_S});
  fnd(4) = [zero; zero];
  fnd = sparse(fnd);

  % production term
  pn = MultiDimVar({N_x_S_lbl}, {N_x_S});
  pn(4) = [zero; zero];
  pn = sparse(pn);

  % incidence matrix of directed graphs for for species NS x AS
  Fc_NS_AS = MultiDimVar({N_x_S_lbl, A_x_S_lbl}, {N_x_S, A_x_S});
  Fc_NS_AS.value(1, 1) = -1;
  Fc_NS_AS.value(5, 1) = 1;
  Fc_NS_AS.value(2, 3) = -1;
  Fc_NS_AS.value(6, 3) = 1;
  Fc_NS_AS.value(5, 5) = -1;
  Fc_NS_AS.value(3, 5) = 1;
  Fc_NS_AS.value(6, 6) = -1;
  Fc_NS_AS.value(4, 6) = 1;
  Fc_NS_AS = sparse(Fc_NS_AS);

  % block difference operator
  Dc_NS_AS = MultiDimVar({N_x_S_lbl, A_x_S_lbl}, {N_x_S, A_x_S});
  Dc_NS_AS.value(1, 1) = -1;
  Dc_NS_AS.value(5, 1) = 1;
  Dc_NS_AS.value(2, 3) = -1;
  Dc_NS_AS.value(6, 3) = 1;
  Dc_NS_AS.value(5, 5) = -1;
  Dc_NS_AS.value(3, 5) = 1;
  Dc_NS_AS.value(6, 6) = -1;
  Dc_NS_AS.value(4, 6) = 1;
  Dc_NS_AS = sparse(Dc_NS_AS);

  % numerical value one half
  onehalf = onehalf;

  % molar concentration
  c = MultiDimVar({N_x_S_lbl}, {N_x_S});
  c(3) = [c31; c32];
  c(1) = [c11; c12];
  c(2) = [c21; c22];
  c = sparse(c);

  % difference operator
  Dc = MultiDimVar({N_lbl, A_lbl}, {N, A});
  Dc.value(1, 1) = -1;
  Dc.value(4, 1) = 1;
  Dc.value(2, 2) = -1;
  Dc.value(4, 2) = 1;
  Dc.value(4, 3) = -1;
  Dc.value(3, 3) = 1;
  Dc = sparse(Dc);

  % valve constant
  cv_A = MultiDimVar({A_lbl}, {A});
  cv_A(3) = [cv3];
  cv_A(1) = [cv1];
  cv_A(2) = [cv2];
  cv_A = sparse(cv_A);

  % thermodynamic pressure
  p = MultiDimVar({N_lbl}, {N});
  p(3) = [p3];
  p(1) = [p1];
  p(2) = [p2];
  p = sparse(p);

  % 
  dEdt = MultiDimVar({N_lbl}, {N});
  dEdt(4) = [zero; zero];
  dEdt = sparse(dEdt);

  % mass density
  density = MultiDimVar({N_lbl}, {N});
  density(4) = [rho_node4];
  density = sparse(density);

  % 
  l_A = MultiDimVar({A_lbl}, {A});
  l_A(1) = [l1];
  l_A(2) = [l2];
  l_A(3) = [l3];
  l_A = sparse(l_A);

  % 
  kf_A = MultiDimVar({A_lbl}, {A});
  kf_A(1) = [kfa1];
  kf_A(2) = [kfa2];
  kf_A(3) = [kfa3];
  kf_A = sparse(kf_A);

  % species molecular masses
  Mm = MultiDimVar({S_lbl}, {S});
  Mm(1) = [lambda1];
  Mm(2) = [lambda2];
  Mm = sparse(Mm);

  % 
  h_A = MultiDimVar({A_lbl}, {A});
  h_A(3) = [h3];
  h_A(1) = [h1];
  h_A(2) = [h2];
  h_A = sparse(h_A);

  % 
  g = g;

  % 
  A_A = MultiDimVar({A_lbl}, {A});
  A_A(3) = [A3];
  A_A(1) = [A1];
  A_A(2) = [A2];
  A_A = sparse(A_A);

  % 
  rho_A = MultiDimVar({A_lbl}, {A});
  rho_A(3) = [rho_arc3];
  rho_A(1) = [rho_arc1];
  rho_A(2) = [rho_arc2];
  rho_A = sparse(rho_A);

  % species molar mass
  n = MultiDimVar({N_x_S_lbl}, {N_x_S});
  n = sparse(n);

  % differential molar mass balance
  dndt = MultiDimVar({N_x_S_lbl}, {N_x_S});
  dndt = sparse(dndt);

  % net convective molar mass flow
  fnc = MultiDimVar({N_x_S_lbl}, {N_x_S});
  fnc = sparse(fnc);

  % convective molar mass flow per arc
  fnc_AS = MultiDimVar({A_x_S_lbl}, {A_x_S});
  fnc_AS = sparse(fnc_AS);

  % moler concentration in convective arc
  c_AS = MultiDimVar({A_x_S_lbl}, {A_x_S});
  c_AS = sparse(c_AS);

  % volumetric flow in x-direction
  fV = MultiDimVar({A_lbl}, {A});
  fV = sparse(fV);

  % direction of convective flow
  d = MultiDimVar({A_lbl}, {A});
  d = sparse(d);

  % foundation state -- volume
  V = MultiDimVar({N_lbl}, {N});
  V = sparse(V);

  % 
  Ev = MultiDimVar({N_lbl}, {N});
  Ev = sparse(Ev);

  % 
  Ef = MultiDimVar({N_lbl}, {N});
  Ef = sparse(Ef);

  % 
  Ek = MultiDimVar({N_lbl}, {N});
  Ek = sparse(Ek);

  % 
  Ep = MultiDimVar({N_lbl}, {N});
  Ep = sparse(Ep);

  % mass
  m = MultiDimVar({N_lbl}, {N});
  m = sparse(m);

  % 
  Ev_A = MultiDimVar({A_lbl}, {A});
  Ev_A = sparse(Ev_A);

  % 
  Ek_A = MultiDimVar({A_lbl}, {A});
  Ek_A = sparse(Ek_A);

  % 
  Ep_A = MultiDimVar({A_lbl}, {A});
  Ep_A = sparse(Ep_A);

  % 
  v_A = MultiDimVar({A_lbl}, {A});
  v_A = sparse(v_A);

  % 
  m_A = MultiDimVar({A_lbl}, {A});
  m_A = sparse(m_A);


% Integrators
  % Initial conditions
  phi_0(1:2) = no(N_dyn);

  % Integration interval
  integration_interval = [to, te];

  % Integrator routine
  [t, phi] = ode15s(@f, integration_interval, phi_0);

  % Integrand
  function dphidt = f(t, phi) 
    n(N_dyn) = phi(1:2);

    Ef(N_dyn) = E_30(l_A, F, kf_A, N_dyn, A_conv);

    m(N_dyn) = E_23(Mm, n, N_dyn);

    V(N_dyn) = rootE_22(density, m, V, N_dyn);

    c(N_dyn) = E_21(n, V, N_dyn);

    sol = system1(Ep_A, g, P_N_A, Ep, Dc, m_A, Ek_A, Ev_A, h_A, cv_A, Ek, p, dEdt, Ev, onehalf, Ef, A_A, rho_A, v_A, F, fV, A_conv, N_const, N_dyn);
    v_A(A_conv) = sol(1:3);
    Ep(N_dyn) = sol(4:4);
    Ev(N_dyn) = sol(5:5);
    Ev_A(A_conv) = sol(6:8);
    Ek_A(A_conv) = sol(9:11);
    Ek(N_dyn) = sol(12:12);
    m_A(A_conv) = sol(13:15);
    p(N_dyn) = sol(16:16);
    fV(A_conv) = sol(17:19);
    Ep_A(A_conv) = sol(20:22);

    d(A_conv) = E_20(Dc, p, indexunion(N_const, N_dyn), A_conv);

    c_AS(A_conv) = E_19(Dc_NS_AS, d, onehalf, c, indexunion(N_const, N_dyn), A_conv);

    fnc_AS(A_conv) = E_12(c_AS, fV, A_conv);

    fnc(N_dyn) = E_5(Fc_NS_AS, fnc_AS, N_dyn, A_conv);

    dndt(N_dyn) = E_3(fnd, fnc, pn, N_dyn);

    n(N_dyn) = E_1(dndt, to, no, te, t, N_dyn);

    dphidt(1:2) = dndt(N_dyn)
  endfunction
endfunction

% Functions for the equations
function sol = E_30(l_A, F, kf_A, N, A)
  sol =  F(N,A) * (kf_A(A) .* l_A(A));
endfunction

function sol = E_23(Mm, n, N)
  sol = blockReduce(Mm, "S", "NS", n(N);
endfunction

function sol = rootE_22(density, m, V, N)
  function F = root(x)
    V(N) = x
    F = m(N) .* reciprocal(V(N)) - density(N);
    F = F.value;
  endfunction

  init_guess = [Initial_Guess]
  sol = fsolve(@root, init_guess)

endfunction

function sol = E_21(n, V, N)
  sol = khatrirao(reciprocal(V(N)), {"N"}, n(N), {"NS"});
endfunction

function sol = system1(Ep_A, g, P_N_A, Ep, Dc, m_A, Ek_A, Ev_A, h_A, cv_A, Ek, p, dEdt, Ev, onehalf, Ef, A_A, rho_A, v_A, F, fV, A_conv, N_const, N_dyn)
  function F = sys(x)
    v_A(A_conv) = x(1:3)
    Ep(N_dyn) = x(4:4)
    Ev(N_dyn) = x(5:5)
    Ev_A(A_conv) = x(6:8)
    Ek_A(A_conv) = x(9:11)
    Ek(N_dyn) = x(12:12)
    m_A(A_conv) = x(13:15)
    p(N_dyn) = x(16:16)
    fV(A_conv) = x(17:19)
    Ep_A(A_conv) = x(20:22)

    function sol = E_35(A_A, v_A, fV, A)
      sol = fV(A) * reciprocal(A_A(A)) - v_A(A);
      sol = sol.value;
    endfunction
    function sol = E_28(Ep_A, F, Ep, N, A)
      sol = F(N,A) * Ep_A(A) - Ep(N);
      sol = sol.value;
    endfunction
    function sol = E_27(Ev_A, F, Ev, N, A)
      sol = F(N,A) * Ev_A(A) - Ev(N);
      sol = sol.value;
    endfunction
    function sol = E_31(Ev_A, fV, P_N_A, p, N, A)
      sol = -fV(A) * (P_N_A(N,A) * p(N)) - Ev_A(A);
      sol = sol.value;
    endfunction
    function sol = E_33(Ek_A, v_A, onehalf, m_A, A)
      sol =  onehalf * m_A(A) * v_A(A) * v_A(A) - Ek_A(A);
      sol = sol.value;
    endfunction
    function sol = E_29(Ek, F, Ek_A, N, A)
      sol = F(N,A) * Ek_A(A) - Ek(N);
      sol = sol.value;
    endfunction
    function sol = E_34(m_A, rho_A, fV, A)
      sol = rho_A(A) * fV(A) - m_A(A);
      sol = sol.value;
    endfunction
    function sol = E_26(dEdt, Ev, Ef, Ek, Ep, N)
      sol = Ev(N) + Ep(N) + Ek(N) + Ef(N) - dEdt(N);
      sol = sol.value;
    endfunction
    function sol = E_18(Dc, cv_A, p, fV, N, A)
      sol = cv_A(A) .* (Dc(N,A) * p(N)) - fV(A);
      sol = sol.value;
    endfunction
    function sol = E_32(Ep_A, m_A, h_A, g, A)
      sol = m_A(A) * g * h_A(A) - Ep_A(A);
      sol = sol.value;
    endfunction

    F(1:3) = E_35(A_A, v_A, fV, A_conv)
    F(4:4) = E_28(Ep_A, F, Ep, N_dyn, A_conv)
    F(5:5) = E_27(Ev_A, F, Ev, N_dyn, A_conv)
    F(6:8) = E_31(Ev_A, fV, P_N_A, p, indexunion(N_const, N_dyn), A_conv)
    F(9:11) = E_33(Ek_A, v_A, onehalf, m_A, A_conv)
    F(12:12) = E_29(Ek, F, Ek_A, N_dyn, A_conv)
    F(13:15) = E_34(m_A, rho_A, fV, A_conv)
    F(16:16) = E_26(dEdt, Ev, Ef, Ek, Ep, N_dyn)
    F(17:19) = E_18(Dc, cv_A, p, fV, indexunion(N_const, N_dyn), A_conv)
    F(20:22) = E_32(Ep_A, m_A, h_A, g, A_conv)
  endfunction

  init_guess = [initial_guess]
  sol = fsolve(@sys, init_guess)

endfunction

function sol = E_20(Dc, p, N, A)
  sol = sign(Dc(N,A) * p(N));
endfunction

function sol = E_19(Dc_NS_AS, d, onehalf, c, N, A)
  sol = ( (onehalf .* (Dc_NS_AS(N,A) - khatriRao(d(A), {"A"}, abs(Dc_NS_AS(N,A)), {"NS", "AS"}))) ) * c(N);
endfunction

function sol = E_12(c_AS, fV, A)
  sol = khatriRao(fV(A), {"A"}, c_AS(A), {"AS"});
endfunction

function sol = E_5(Fc_NS_AS, fnc_AS, N, A)
  sol = F_NS_AS(N,A) * fnc_AS(A);
endfunction

function sol = E_3(fnd, fnc, pn, N)
  sol = fnc(N) + fnd(N) + pn(N);
endfunction

function sol = E_1(dndt, to, no, te, t, N)
  sol = Integral(dndt,t,to,te) + no;
endfunction


% Auxiliar functions
function result = indexunion(varargin)
  result = varargin{1};
  for i = 2:nargin
    result = union(result, varargin{i});
  endfor
endfunction