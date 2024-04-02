function control
  % To be used with new_control document, the following values have been used:
  % alpha1 = 1 (Node 1)
  % alpha2 = 2 (Node 2)
  % beta1 = 31 (Node 3 Species 1)
  % beta2 = 32 (Node 3 Species 2)
  % gamma1 = 131 (Node 13 Output 1)
  % gamma2 = 132 (Node 13 Output 2)
  % gamma3 = 133 (Node 13 Output 3)
  % epsilon1 = 141 (Node 14 Output 1)
  % epsilon2 = 142 (Node 14 Output 2)
  indexOrder = {"N", "A", "I", "p", "q", "t", "u", "S"};

  % Index dimension sizes
  N_size = 21;
  A_size = 11;
  I_size = 8;
  p_size = 2;   % Max number of inputs that a node receives
  q_size = 3;   % Max number of outputs that a node have
  t_size = 3;   % Max size of the signal vector (both input and output need to match)
  u_size = 3;   % Max size of the signal vector (both input and output need to match)
  S_size = 2;

  % Measured quantities in macro
  alpha_N = MultiDimVar({"N"}, [N_size], indexOrder);
  alpha_N(1) = 1;
  alpha_N(2) = 2;

  beta_NS = MultiDimVar({"N", "S"}, [N_size S_size], indexOrder);
  beta_NS(3, 1) = 31;
  beta_NS(3, 2) = 32;

  % Interface variable from macro --> control for single value
  _mv_I = MultiDimVar({"I"}, [I_size], indexOrder);

  % Interface variable from macro --> control for multiple values
  _mw_IS = MultiDimVar({"I", "S"}, [I_size S_size], indexOrder);

  % Output for the control nodes
  y_Nqu = MultiDimVar({"N", "q", "u"}, [N_size q_size u_size], indexOrder);

  % Input for the control nodes
  u_Npt = MultiDimVar({"N", "p", "t"}, [N_size p_size t_size], indexOrder);

  % Information vector passed through control arcs
  y_At = MultiDimVar({"A", "t"}, [A_size t_size], indexOrder);

  % Output value from control
  cz_N = MultiDimVar({"N"}, [N_size], indexOrder);
  
  % Interface variable from control --> macro
  _cz_I = MultiDimVar({"I"}, [I_size], indexOrder);

  % Controlled variables in macro
  gamma_N = MultiDimVar({"N"}, [N_size], indexOrder);
  epsilon_N = MultiDimVar({"N"}, [N_size], indexOrder);

  % Incidence matrices
  F_NI_source = MultiDimVar({"N", "I"}, [N_size I_size], indexOrder);
  F_NI_source(1, 1) = 1;
  F_NI_source(2, 2) = 1;
  F_NI_source(3, 3) = 1;
  F_NI_source(17, 4) = 1;
  F_NI_source(18, 5) = 1;
  F_NI_source(19, 6) = 1;
  F_NI_source(20, 7) = 1;
  F_NI_source(21, 8) = 1;

  F_NI_sink = MultiDimVar({"N", "I"}, [N_size I_size], indexOrder);
  F_NI_sink(4, 4) = 1;
  F_NI_sink(5, 5) = 1;
  F_NI_sink(6, 6) = 1;
  F_NI_sink(7, 7) = 1;
  F_NI_sink(8, 8) = 1;
  F_NI_sink(9, 1) = 1;
  F_NI_sink(10, 2) = 1;
  F_NI_sink(11, 3) = 1;

  F_NA_source = MultiDimVar({"N", "A"}, [N_size A_size], indexOrder);
  F_NA_source(9, 1) = 1;
  F_NA_source(10, 2) = 1;
  F_NA_source(11, 4) = 1;
  F_NA_source(12, 3) = 1;
  F_NA_source(13, 5) = 1;
  F_NA_source(14, 6) = 1;
  F_NA_source(15, 7) = 1;
  F_NA_source(15, 8) = 1;
  F_NA_source(15, 9) = 1;
  F_NA_source(16, 10) = 1;
  F_NA_source(16, 11) = 1;

  F_NA_sink = MultiDimVar({"N", "A"}, [N_size A_size], indexOrder);
  F_NA_sink(12, 1) = 1;
  F_NA_sink(12, 2) = 1;
  F_NA_sink(13, 3) = 1;
  F_NA_sink(14, 4) = 1;
  F_NA_sink(15, 5) = 1;
  F_NA_sink(16, 6) = 1;
  F_NA_sink(17, 7) = 1;
  F_NA_sink(18, 8) = 1;
  F_NA_sink(19, 9) = 1;
  F_NA_sink(20, 10) = 1;
  F_NA_sink(21, 11) = 1;

  % Constant vectors to add dimensions of a proper size to variables without
  % affecting thir values. Similar to add singleton dimensions, but dimensions
  % need to have their actial sizes.
  S_u = MultiDimVar({"t"}, [u_size], indexOrder);
  S_u(1) = 1;

  S_q = MultiDimVar({"q"}, [q_size], indexOrder);
  S_q(1) = 1;

  % Selection matrix for instruments that measure specied related quantities
  S_Nus = MultiDimVar({"N", "u", "S"}, [N_size u_size S_size], indexOrder);
  S_Nus(11, 1, 1) = 1;
  S_Nus(11, 2, 2) = 1;

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
  S_Ap(4, 1) = 1;
  S_Ap(5, 1) = 1;
  S_Ap(6, 1) = 1;
  S_Ap(7, 1) = 1;
  S_Ap(8, 1) = 1;
  S_Ap(9, 1) = 1;
  S_Ap(10, 1) = 1;
  S_Ap(11, 1) = 1;

  % Selection matrix for arcs connected to outputs
  S_Aq = MultiDimVar({"A", "q"}, [A_size q_size], indexOrder);
  S_Aq(1, 1) = 1;
  S_Aq(2, 1) = 1;
  S_Aq(3, 1) = 1;
  S_Aq(4, 1) = 1;
  S_Aq(5, 1) = 1;
  S_Aq(6, 1) = 1;
  S_Aq(7, 1) = 1;
  S_Aq(8, 2) = 1;
  S_Aq(9, 3) = 1;
  S_Aq(10, 1) = 1;
  S_Aq(11, 2) = 1;

  % Unit vectors.
  % Will be replaced when new operations are added.
  % einsum(x_abc, ones_b, {"b"}) --> reduce_sum(x_abc, {"b"})
  ones_q = MultiDimVar({"q"}, [q_size], indexOrder);
  ones_q(1) = 1;
  ones_q(2) = 1;
  ones_q(3) = 1;

  ones_p = MultiDimVar({"p"}, [p_size], indexOrder);
  ones_p(1) = 1;
  ones_p(2) = 1;

  ones_t = MultiDimVar({"t"}, [t_size], indexOrder);
  ones_t(1) = 1;
  ones_t(2) = 1;
  ones_t(3) = 1;

  % Map between input size and output size
  A_Ntu = MultiDimVar({"N", "t", "u"}, [N_size t_size u_size], indexOrder);
  A_Ntu(12, 1, 1) = 1;
  A_Ntu(12, 1, 2) = 1;
  A_Ntu(13, 1, 1) = -131;
  A_Ntu(13, 2, 1) = 131;
  A_Ntu(13, 1, 2) = -132;
  A_Ntu(13, 2, 2) = 132;
  A_Ntu(13, 1, 3) = -133;
  A_Ntu(13, 2, 3) = 133;
  A_Ntu(14, 1, 1) = -141;
  A_Ntu(14, 2, 1) = 141;
  A_Ntu(14, 1, 2) = -142;
  A_Ntu(14, 2, 2) = 142;
  A_Ntu(15, 1, 1) = 1;
  A_Ntu(15, 2, 1) = 1;
  A_Ntu(15, 3, 1) = 1;
  A_Ntu(16, 1, 1) = 1;
  A_Ntu(16, 2, 1) = 1;

  % Map between inputs and outputs
  A_Npq = MultiDimVar({"N", "p", "q"}, [N_size p_size q_size], indexOrder);
  A_Npq(12, 1, 1) = 1;
  A_Npq(12, 2, 1) = 1;
  A_Npq(13, 1, 1) = 1;
  A_Npq(14, 1, 1) = 1;
  A_Npq(15, 1, 1) = 1;
  A_Npq(15, 1, 2) = 1;
  A_Npq(15, 1, 3) = 1;
  A_Npq(16, 1, 1) = 1;
  A_Npq(16, 1, 2) = 1;

  % Map between inputs and output size (act as a mask)
  S_Npu = MultiDimVar({"N", "p", "u"}, [N_size p_size u_size], indexOrder);
  S_Npu(12, 1, 1) = 1;
  S_Npu(12, 2, 2) = 1;

  % Map between input size and outputs (act as a mask)
  S_Nqt = MultiDimVar({"N", "q", "t"}, [N_size q_size t_size], indexOrder);
  S_Nqt(15, 1, 1) = 1;
  S_Nqt(15, 2, 2) = 1;
  S_Nqt(15, 3, 3) = 1;
  S_Nqt(16, 1, 1) = 1;
  S_Nqt(16, 2, 2) = 1;

  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Equations %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  % This indices are always used as a whole
  p = [1 2];
  q = [1 2 3];
  t = [1 2 3];
  u = [1 2 3];
  S = [1 2];

  % Interfaces 1,2 (Single value)
  I = [1, 2];
  N = [1, 2];
  _mv_I(I) = einsum(F_NI_source(N, I), alpha_N(N), {"N"});

  % Interface 3 (Multiple values)
  N = [3];
  I = [3];
  _mw_IS(I, S) = einsum(F_NI_source(N, I), beta_NS(N, S), {"N"});

  % Nodes 9, 10 (Instrument single value)
  N = [9 10];
  I = [1 2];
  y_Nqu(N, q, u) = einsum(einsum(einsum(F_NI_sink(N, I), _mv_I(I), {"I"}), ...
    S_u(u)) , S_q(q));

  % Node 11 (Instrument multiple values)
  N = [11];
  I = [3];
  y_Nqu(N, q, u) = einsum(einsum(einsum(F_NI_sink(N, I), _mw_IS(I, S), {"I"}), ...
    S_Nus(N, u, S), {"S"}) , S_q(q));
  
  % Arcs 1,2,4
  N = [9 10 11];
  A = [1 2 4];
  y_At(A, t) = einsum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), ones_q, {"q"});

  % Node 12 (stacker)
  N = [12];
  A = [1 2];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  y_Nqu(N, q, u) = einsum(einsum(einsum(u_Npt(N, p, t), A_Ntu(N, t, u), {"t"}), ...
    S_Npu(N, p, u)), A_Npq(N, p, q), {"p"});

  % Arc 3
  N = [12];
  A = [3];
  y_At(A, t) = einsum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), ones_q, {"q"});

  % Nodes 13, 14 (controllers)
  N = [13 14];
  A = [3 4];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  y_Nqu(N, q, u) = einsum(einsum(u_Npt(N, p, t), A_Ntu(N, t, u), {"t"}), A_Npq(N, p, q), {"p"});

  % Arcs 5,6
  N = [13 14];
  A = [5 6];
  y_At(A, t) = einsum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), ones_q, {"q"});

  % Nodes 15, 16 (splitters)
  N = [15 16];
  A = [5 6];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  y_Nqu(N, q, u) = einsum(einsum(einsum(u_Npt(N, p, t), A_Npq(N, p, q), {"p"}), ...
    S_Nqt(N, q, t)), A_Ntu(N, t, u), {"t"});

  % Arcs 7,8,9,10,11
  N = [15 16];
  A = [7 8 9 10 11];
  y_At(A, t) = einsum(einsum(einsum(einsum(F_NA_source(N, A), y_Nqu(N, q, u), ...
    {"N"}), I_tu, {"u"}), S_Aq(A, q)), ones_q, {"q"});

  % Nodes 17,18,19,20,21 (not sure about the name, opposite of instruments)
  N = [17 18 19 20 21];
  A = [7 8 9 10 11];
  u_Npt(N, p, t) = einsum(einsum(F_NA_sink(N, A), y_At(A, t)), S_Ap(A, p), {"A"});
  cz_N(N) = einsum(einsum(u_Npt(N, p, t), ones_p(p), {"p"}), ones_t(t), {"t"});

  % Interfaces 4,5,6,7,8
  N = [17 18 19 20 21];
  I = [4 5 6 7 8];
  _cz_I(I) = einsum(F_NI_source(N, I), cz_N(N), {"N"});

  % Nodes 4,5,6
  N = [4 5 6];
  I = [4 5 6];
  gamma_N(N) = einsum(F_NI_sink(N, I), _cz_I(I), {"I"});

  % Nodes 7,8
  N = [7 8];
  I = [7 8];
  epsilon_N(N) = einsum(F_NI_sink(N, I), _cz_I(I), {"I"});
endfunction