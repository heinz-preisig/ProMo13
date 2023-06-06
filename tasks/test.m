function output_vars = main
  % Index sets
  N = cell(1, 10);
  N(1)  = 1;
  N(2)  = 2;
  N(3)  = 3;
  N(4)  = 4;
  N(5)  = 5;
  N(6)  = 6;
  N(7)  = 7;
  N(8)  = 8;
  N(9)  = 9;
  N(10)  = 10;
  N_lbl = "N";
  N_x_S = cell(1, 10);
  N_x_S(1)  = [1];
  N_x_S(2)  = [1];
  N_x_S(3)  = [1];
  N_x_S(4)  = [1];
  N_x_S(5)  = [1];
  N_x_S(6)  = [1];
  N_x_S(7)  = [1];
  N_x_S(8)  = [1];
  N_x_S(9)  = [1];
  N_x_S(10)  = [1];
  N_x_S_lbl = "N_x_S";
  A = cell(1, 9);
  A(1)  = 1;
  A(2)  = 2;
  A(3)  = 3;
  A(4)  = 4;
  A(5)  = 5;
  A(6)  = 6;
  A(7)  = 7;
  A(8)  = 8;
  A(9)  = 9;
  A_lbl = "A";
  A_x_S = cell(1, 9);
  A_x_S(1)  = [1];
  A_x_S(2)  = [1];
  A_x_S(3)  = [1];
  A_x_S(4)  = [1];
  A_x_S(5)  = [1];
  A_x_S(6)  = [1];
  A_x_S(7)  = [1];
  A_x_S(8)  = [1];
  A_x_S(9)  = [1];
  A_x_S_lbl = "A_x_S";
  S = cell(1, 1);
  S(1)  = 1;
  S_lbl = "S";

  N_const = [1];
  N_dyn = [2, 3, 4, 5, 6, 7, 8, 9, 10];
  A_diff = [1, 2, 3, 4, 5, 6, 7, 8, 9];

  % Variables
  % initial condition for species mass in nodes
  no = MultiDimVar({N_x_S_lbl}, {N_x_S});
  no(7) = [0];
  no(9) = [0];
  no(8) = [0];
  no(2) = [0];
  no(3) = [0];
  no(10) = [0];
  no(4) = [0];
  no(6) = [0];
  no(5) = [0];
  no = sparse(no);

  % end time
  te = 180;

  % starting time
  to = 0;

  % link variable nProd to interface reactions >>> macroscopic
  _nProd = MultiDimVar({N_x_S_lbl}, {N_x_S});
  _nProd(7) = [0];
  _nProd(9) = [0];
  _nProd(2) = [0];
  _nProd(3) = [0];
  _nProd(10) = [0];
  _nProd(5) = [0];
  _nProd(4) = [0];
  _nProd(6) = [0];
  _nProd(8) = [0];
  _nProd = sparse(_nProd);

  % net molar convectional mass flow
  fnc = MultiDimVar({N_x_S_lbl}, {N_x_S});
  fnc(7) = [0];
  fnc(9) = [0];
  fnc(2) = [0];
  fnc(3) = [0];
  fnc(10) = [0];
  fnc(5) = [0];
  fnc(4) = [0];
  fnc(6) = [0];
  fnc(8) = [0];
  fnc = sparse(fnc);

  % species related incidence matrix for diffusion
  Fd = MultiDimVar({N_x_S_lbl, A_x_S_lbl}, {N_x_S, A_x_S});
  Fd.value(1, 1) = -1;
  Fd.value(4, 1) = 1;
  Fd.value(4, 2) = -1;
  Fd.value(5, 2) = 1;
  Fd.value(5, 3) = -1;
  Fd.value(3, 3) = 1;
  Fd.value(1, 4) = -1;
  Fd.value(10, 4) = 1;
  Fd.value(10, 5) = -1;
  Fd.value(7, 5) = 1;
  Fd.value(7, 6) = -1;
  Fd.value(2, 6) = 1;
  Fd.value(7, 7) = -1;
  Fd.value(8, 7) = 1;
  Fd.value(8, 8) = -1;
  Fd.value(6, 8) = 1;
  Fd.value(6, 9) = -1;
  Fd.value(9, 9) = 1;
  Fd = sparse(Fd);

  % difference operator for species topology (diffusion)
  Dd_NS_AS = MultiDimVar({N_x_S_lbl, A_x_S_lbl}, {N_x_S, A_x_S});
  Dd_NS_AS.value(1, 1) = -1;
  Dd_NS_AS.value(4, 1) = 1;
  Dd_NS_AS.value(4, 2) = -1;
  Dd_NS_AS.value(5, 2) = 1;
  Dd_NS_AS.value(5, 3) = -1;
  Dd_NS_AS.value(3, 3) = 1;
  Dd_NS_AS.value(1, 4) = -1;
  Dd_NS_AS.value(10, 4) = 1;
  Dd_NS_AS.value(10, 5) = -1;
  Dd_NS_AS.value(7, 5) = 1;
  Dd_NS_AS.value(7, 6) = -1;
  Dd_NS_AS.value(2, 6) = 1;
  Dd_NS_AS.value(7, 7) = -1;
  Dd_NS_AS.value(8, 7) = 1;
  Dd_NS_AS.value(8, 8) = -1;
  Dd_NS_AS.value(6, 8) = 1;
  Dd_NS_AS.value(6, 9) = -1;
  Dd_NS_AS.value(9, 9) = 1;
  Dd_NS_AS = sparse(Dd_NS_AS);

  % molar composition
  c = MultiDimVar({N_x_S_lbl}, {N_x_S});
  c(1) = [0; .; 5];
  c = sparse(c);

  % Diffusion Coefficient
  DiffCoeff = MultiDimVar({A_x_S_lbl}, {A_x_S});
  DiffCoeff(3) = [0.65];
  DiffCoeff(5) = [0.65];
  DiffCoeff(1) = [0.65];
  DiffCoeff(2) = [0.65];
  DiffCoeff(4) = [0.65];
  DiffCoeff(9) = [0.65];
  DiffCoeff(8) = [0.65];
  DiffCoeff(7) = [0.65];
  DiffCoeff(6) = [0.65];
  DiffCoeff = sparse(DiffCoeff);

  % fundamental state -- volume
  V = MultiDimVar({N_lbl}, {N});
  V(7) = [1];
  V(9) = [3];
  V(8) = [3];
  V(10) = [1];
  V(3) = [2];
  V(2) = [1];
  V(4) = [3];
  V(6) = [2];
  V(5) = [3];
  V = sparse(V);

  % fundamental state -- molar mass
  n = MultiDimVar({N_x_S_lbl}, {N_x_S});
  n = sparse(n);

  % differential species balance
  dndt = MultiDimVar({N_x_S_lbl}, {N_x_S});
  dndt = sparse(dndt);

  % net diffusional mass flow
  fnd = MultiDimVar({N_x_S_lbl}, {N_x_S});
  fnd = sparse(fnd);

  % diffusional mass flow in a given stream
  fnd_AS = MultiDimVar({A_x_S_lbl}, {A_x_S});
  fnd_AS = sparse(fnd_AS);


% Integrators
  % Initial conditions
  phi_0(1:9) = no(N_dyn);

  % Integration interval
  integration_interval = [to, te];

  % Integrator routine
  [t, phi] = ode15s(@f, integration_interval, phi_0);

  % Integrand
  function dphidt = f(t, phi) 
    n(N_dyn) = phi(1:9);

    c(N_dyn) = E_44(V, n, N_dyn);

    fnd_AS(A_diff) = E_132(Dd_NS_AS, c, DiffCoeff, indexunion(N_const, N_dyn), A_diff);

    fnd(N_dyn) = E_69(Fd, fnd_AS, N_dyn, A_diff);

    dndt(N_dyn) = E_76(_nProd, fnd, fnc, N_dyn);

    n(N_dyn) = E_86(no, te, to, t, dndt, N_dyn);

    dphidt(1:9) = dndt(N_dyn)
  endfunction
endfunction

% Functions for the equations
function sol = E_44(V, n, N)
  sol = khatriRao(inv(V), [N], n, [N_x_S]);
endfunction

function sol = E_132(Dd_NS_AS, c, DiffCoeff, N, A)
  sol = DiffCoeff .* (( Dd_NS_AS )'  * c);
endfunction

function sol = E_69(Fd, fnd_AS, N, A)
  sol = Fd * fnd_AS;
endfunction

function sol = E_76(_nProd, fnd, fnc, N)
  sol = fnc + fnd + _nProd;
endfunction

function sol = E_86(no, te, to, t, dndt, N)
  sol = Integral(dndt,t,to,te) + no;
endfunction


% Auxiliar functions
function result = indexunion(varargin)
  result = varargin{1};
  for i = 2:nargin
    result = union(result, varargin{i});
  endfor
endfunction