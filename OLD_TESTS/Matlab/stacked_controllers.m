function stacked_controllers
  % To be used with Stacked_Controllers document, the following values have been used:
  % alpha1 = 11 (Node 1 Species 1)
  % alpha2 = 12 (Node 2 Species 2)
  % alpha3 = 13 (Node 3 Species 3)
  indexOrder = {"N", "A", "I", "p", "q", "t", "u", "S"};

  % Index dimension sizes
  N_size = 11;
  A_size = 9;
  I_size = 2;
  p_size = 2;   % Max number of inputs that a node receives
  q_size = 1;   % Max number of outputs that a node have
  t_size = 3;   % Max size of the signal vector (both input and output need to match)
  u_size = 3;   % Max size of the signal vector (both input and output need to match)
  S_size = 3;

  % Measured quantities in macro
  alpha_NS = MultiDimVar({"N", "S"}, [N_size S_size], indexOrder);
  alpha_NS(1, 1) = 11;
  alpha_NS(1, 2) = 12;
  alpha_NS(1, 3) = 13;

  % Interface variable from macro --> control for multiple values
  _mw_IS = MultiDimVar({"I", "S"}, [I_size S_size], indexOrder);

  % Output for the control nodes
  y_Nqu = MultiDimVar({"N", "q", "u"}, [N_size q_size u_size], indexOrder);
    % Set point for the inversor
  y_Nqu(4, 1, 1) = -1;
  y_Nqu(4, 1, 2) = -1;
  y_Nqu(4, 1, 3) = -1;
    % Set point
  y_Nqu(6, 1, 1) = 62;
  y_Nqu(6, 1, 2) = 64;
  y_Nqu(6, 1, 3) = 66;

  % Input for the control nodes
  u_Npt = MultiDimVar({"N", "p", "t"}, [N_size p_size t_size], indexOrder);

  % Information vector passed through control arcs
  y_At = MultiDimVar({"A", "t"}, [A_size t_size], indexOrder);

  % Output value from control
  cz_N = MultiDimVar({"N"}, [N_size], indexOrder);
  
  % Interface variable from control --> macro
  _cz_I = MultiDimVar({"I"}, [I_size], indexOrder);

  % Controlled variables in macro
  xi_N = MultiDimVar({"N"}, [N_size], indexOrder);

  % Incidence matrices
  F_NI_source = MultiDimVar({"N", "I"}, [N_size I_size], indexOrder);
  F_NI_source(1, 1) = 1;
  F_NI_source(10, 2) = 1;

  F_NI_sink = MultiDimVar({"N", "I"}, [N_size I_size], indexOrder);
  F_NI_sink(2, 1) = 1;
  F_NI_sink(11, 2) = 1;

  F_NA_source = MultiDimVar({"N", "A"}, [N_size A_size], indexOrder);
  F_NA_source(2, 1) = 1;
  F_NA_source(3, 3) = 1;
  F_NA_source(4, 2) = 1;
  F_NA_source(6, 4) = 1;
  F_NA_source(5, 5) = 1;
  F_NA_source(7, 6) = 1;
  F_NA_source(3, 7) = 1;
  F_NA_source(8, 8) = 1;
  F_NA_source(9, 9) = 1;

  F_NA_sink = MultiDimVar({"N", "A"}, [N_size A_size], indexOrder);
  F_NA_sink(3, 1) = 1;
  F_NA_sink(3, 2) = 1;
  F_NA_sink(5, 3) = 1;
  F_NA_sink(5, 4) = 1;
  F_NA_sink(7, 5) = 1;
  F_NA_sink(8, 6) = 1;
  F_NA_sink(8, 7) = 1;
  F_NA_sink(9, 8) = 1;
  F_NA_sink(10, 9) = 1;

  % Constant vectors to add dimensions of a proper size to variables without
  % affecting thir values. Similar to add singleton dimensions, but dimensions
  % need to have their actial sizes.
  S_u = MultiDimVar({"t"}, [u_size], indexOrder);
  S_u(1) = 1;

  S_q = MultiDimVar({"q"}, [q_size], indexOrder);
  S_q(1) = 1;

  % Selection matrix for instruments that measure specied related quantities
  S_Nus = MultiDimVar({"N", "u", "S"}, [N_size u_size S_size], indexOrder);
  S_Nus(2, 1, 1) = 1;
  S_Nus(2, 2, 2) = 1;
  S_Nus(2, 3, 3) = 1;

  % Identity matrix to transform u into t
  I_tu = MultiDimVar({"t", "u"}, [t_size u_size], indexOrder);
  I_tu(1, 1) = 1;
  I_tu(2, 2) = 1;
  I_tu(3, 3) = 1;

  % Selection matrix for arcs connected to inputs
  S_Ap = MultiDimVar({"A", "p"}, [A_size p_size], indexOrder);
  S_Ap(1, 1) = 1;
  S_Ap(2, 2) = 1;
  S_Ap(3, 1) = 1;
  S_Ap(4, 2) = 1;
  S_Ap(5, 1) = 1;
  S_Ap(6, 1) = 1;
  S_Ap(7, 2) = 1;
  S_Ap(8, 1) = 1;
  S_Ap(9, 1) = 1;

  % Selection matrix for arcs connected to outputs
  S_Aq = MultiDimVar({"A", "q"}, [A_size q_size], indexOrder);
  S_Aq(1, 1) = 1;
  S_Aq(2, 1) = 1;
  S_Aq(3, 1) = 1;
  S_Aq(4, 1) = 1;
  S_Aq(5, 1) = 1;
  S_Aq(6, 1) = 1;
  S_Aq(7, 1) = 1;
  S_Aq(8, 1) = 1;
  S_Aq(9, 1) = 1;

  % Map between input size and output size
  A_Ntu = MultiDimVar({"N", "t", "u"}, [N_size t_size u_size], indexOrder);
  A_Ntu(3, 1, 1) = 1;
  A_Ntu(3, 2, 2) = 1;
  A_Ntu(3, 3, 3) = 1;
  A_Ntu(5, 1, 1) = 1;
  A_Ntu(5, 2, 2) = 1;
  A_Ntu(5, 3, 3) = 1;
  A_Ntu(7, 1, 1) = -71;
  A_Ntu(7, 1, 2) = -72;
  A_Ntu(7, 1, 3) = -73;
  A_Ntu(7, 2, 1) = 71;
  A_Ntu(7, 2, 2) = 72;
  A_Ntu(7, 2, 3) = 73;
  A_Ntu(8, 1, 1) = 1;
  A_Ntu(8, 2, 2) = 1;
  A_Ntu(8, 3, 3) = 1;
  A_Ntu(9, 1, 1) = 1;
  A_Ntu(9, 2, 1) = 0.5;

  % Map between inputs and outputs
  A_Npq = MultiDimVar({"N", "p", "q"}, [N_size p_size q_size], indexOrder);
  A_Npq(7, 1, 1) = 1;
  A_Npq(9, 1, 1) = 1;

  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Equations %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  % This indices are always used as a whole
  p = [1 2];
  q = [1];
  t = [1 2 3];
  u = [1 2 3];
  S = [1 2 3];

  % Interface 1
  N = [1];
  I = [1];
  _mw_IS(I, S) = einsum(F_NI_source(N, I), alpha_NS(N, S), {"N"});

  % Node 2 (Instrument multiple values)
  N = [2];
  I = [1];
  y_Nqu(N, q, u) = einsum(einsum(einsum(F_NI_sink(N, I), _mw_IS(I, S), {"I"}), ...
    S_Nus(N, u, S), {"S"}) , S_q(q));

  % Arcs 1, 2
  N = [2 4];
  A = [1 2];
  y_At(A, t) = reducesum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), {"q"});

  % Node 3 (Multiplication)
  N = [3];
  A = [1 2];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  y_Nqu(N, q, u) = einsum(einsum(reducemult(u_Npt(N, p, t), {"p"}), A_Ntu(N, t, u), {"t"}), S_q(q));

  % Arc 3,6,7
  N = [3 6];
  A = [3 4 7];
  y_At(A, t) = reducesum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), {"q"});

  % Nodes 5 (Addition)
  N = [5];
  A = [3 4];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  y_Nqu(N, q, u) = einsum(einsum(reducesum(u_Npt(N, p, t), {"p"}), A_Ntu(N, t, u), {"t"}), S_q(q));

  % Arcs 5
  N = [5];
  A = [5];
  y_At(A, t) = reducesum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), {"q"});

  % Nodes 7 (Outer controller)
  N = [7];
  A = [5];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  y_Nqu(N, q, u) = einsum(einsum(u_Npt(N, p, t), A_Ntu(N, t, u), {"t"}), A_Npq(N, p, q), {"p"});

  % Arcs 6
  N = [7];
  A = [6];
  y_At(A, t) = reducesum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), {"q"});

  % Nodes 8 (Addition)
  N = [8];
  A = [6 7];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  y_Nqu(N, q, u) = einsum(einsum(reducesum(u_Npt(N, p, t), {"p"}), A_Ntu(N, t, u), {"t"}), S_q(q));

  % Arcs 8
  N = [8];
  A = [8];
  y_At(A, t) = reducesum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), {"q"});

  % Nodes 9 (Inner controller)
  N = [9];
  A = [8];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  y_Nqu(N, q, u) = einsum(einsum(u_Npt(N, p, t), A_Ntu(N, t, u), {"t"}), A_Npq(N, p, q), {"p"});
  
  % Arcs 9
  N = [9];
  A = [9];
  y_At(A, t) = reducesum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), {"q"});

  % Nodes 10 (not sure about the name, opposite of instruments)
  N = [10];
  A = [9];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  cz_N(N) = reducesum(u_Npt(N, p, t), {"p", "t"});

  % Interfaces 2
  N = [10];
  I = [2];
  _cz_I(I) = einsum(F_NI_source(N, I), cz_N(N), {"N"});

  % Nodes 11
  N = [11];
  I = [2];
  xi_N(N) = einsum(F_NI_sink(N, I), _cz_I(I), {"I"});
endfunction