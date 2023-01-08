1;
m = modcode;
function mod_out = modcode
  global WTBAR mod_out mod_int par
  mod_out = [];
  mod_in = [];  
  par = [];

  massCons(1,:) = [4,1];   % m01
  massCons(2,:) = [1,5];   % m02
  massCons(3,:) = [6,2];   % m03
  massCons(4,:) = [7,2];   % m04
  massCons(5,:) = [8,3];   % m05
  massCons(6,:) = [2,9];   % m06
  massCons(7,:) = [3,10];  % m07
  massCons(8,:) = [2,3];   % m08
  
  heatCons(1,:) = [1,2];   % h01
  
  par.m08_PermOr = SelectionMatrix(4,[4]);
  par.m08_PermTar = SelectionMatrix(2, [1]);

  num = 3;    % Number of Lump + Steady state systems
  
  A_mass = StreamMatrix(num, massCons);
  A_heat = StreamMatrix(num, heatCons);
 
  numSpec = 6; % Number of Species
  I = speye(numSpec);
  Ak = kron(A_mass, I);
  
  GammaS = [];   % Initialize System Selection Matrix
  GammaS = blkdiag(GammaS,SelectionMatrix(numSpec,[1]));          % System 1
  GammaS = blkdiag(GammaS,SelectionMatrix(numSpec,[2,3,4,5]));    % System 2
  GammaS = blkdiag(GammaS,SelectionMatrix(numSpec,[5,6]));        % System 3
  
  S = [];        % Initialize Stochiometric Matrix
  S = blkdiag(S, sparse(0,1*numSpec));  
  S = blkdiag(S, sparse([0 -2 0 -3 8 0]));                        % System 2
  S = blkdiag(S, sparse(0,1*numSpec));

  GammaM = [];   % Initialize Mass Connection Selection Matrix
  GammaM = blkdiag(GammaM, SelectionMatrix(numSpec, [1]));        % m01
  GammaM = blkdiag(GammaM, SelectionMatrix(numSpec, [1]));        % m02
  GammaM = blkdiag(GammaM, SelectionMatrix(numSpec, [2,3]));      % m03
  GammaM = blkdiag(GammaM, SelectionMatrix(numSpec, [3,4]));      % m04
  GammaM = blkdiag(GammaM, SelectionMatrix(numSpec, [6]));        % m05
  GammaM = blkdiag(GammaM, SelectionMatrix(numSpec, [2,3,4,5]));  % m06
  GammaM = blkdiag(GammaM, SelectionMatrix(numSpec, [5,6]));      % m07
  GammaM = blkdiag(GammaM, SelectionMatrix(numSpec, [5]));        % m08
  
  A_n = GammaS*Ak*GammaM';
  B_n = GammaS*S';
  
  % Global variables
  par.A = A_n;
  par.B = B_n;
  par.Am = A_mass;
  par.Aq = A_heat;
  par.Tref = 0.0;
  par.tspan = 100; 
  
  % Initial conditions
  xx(1:1,1) = [0.1];                                              % n_sys01
  xx(2:5,1) = [0.5;20.0;1.0;0.0];                                 % n_sys02
  xx(6:7,1) = [0.0;21.0]                                          % n_sys03
  xx(8,1) = HFromT(xx(1:1,1),[5.0E+5],[1.0E+3],300,par.Tref);     % H_sys01
  xx(9,1) = HFromT(xx(2:5,1),[5.0E+5,5.0E+5,6.0E+5,-5.0E+6],[1.0E+3,1.0E+3,8E+2,1.2E+3],300,par.Tref); % H_sys02 
  xx(10,1) = HFromT(xx(6:7,1),[-5.0E+6,5.0E+5],[1.2E+3,1.0E+3],300,par.Tref); % H_sys03
  
  % Call solver
  WTBAR = waitbar(0,'Solving DAEs ......');
  options = odeset('OutputFcn', @OutputBuild,'MStateDependence','none','AbsTol', ...
  1E-10,'RelTol', 0.001);
  [t1,x1] = ode15s(@f,[0;par.tspan],xx,options);
  close(WTBAR) 
endfunction

function status = OutputBuild(t,xx,flag)
  global mod_out mod_int
  status = 0;
  if nargin < 3 | isempty(flag)
    i = length(mod_out.t) + 1;
    
    mod_out.t(i,1) = t;
  
    mod_out.sys01.n(i,:) = xx(1:1,1);
    mod_out.sys01.H(i,:) = xx(8,1);
    mod_out.sys01.c(i,:) = mod_int.c_sys01;
    mod_out.sys01.T(i,:) = mod_int.T_sys01;
    mod_out.sys01.hs(i,:) = mod_int.hs_sys01;
  
    mod_out.sys02.n(i,:) = xx(2:5,1);
    mod_out.sys02.H(i,:) = xx(9,1);
    mod_out.sys02.c(i,:) = mod_int.c_sys02;
    mod_out.sys02.T(i,:) = mod_int.T_sys02;
    mod_out.sys02.hs(i,:) = mod_int.hs_sys02;
    mod_out.sys02.reaction1.r(i,:) = mod_int.r(1)  
  
    mod_out.sys03.n(i,:) = xx(6:7,1);
    mod_out.sys03.H(i,:) = xx(10,1);
    mod_out.sys03.c(i,:) = mod_int.c_sys03;
    mod_out.sys03.T(i,:) = mod_int.T_sys03;
    mod_out.sys03.hs(i,:) = mod_int.hs_sys03;
  
    mod_out.sys04.hs(i,:) = mod_int.hs_sys04;
    mod_out.sys06.hs(i,:) = mod_int.hs_sys06;
    mod_out.sys07.hs(i,:) = mod_int.hs_sys07;
    mod_out.sys08.hs(i,:) = mod_int.hs_sys08;
  
    mod_out.con_m01.nhat(i,:) = mod_int.nhat(1:1,1)';
    mod_out.con_m01.Hhat(i,:) = mod_int.Hhat(1);
  
    mod_out.con_m02.nhat(i,:) = mod_int.nhat(2:2,1)';
    mod_out.con_m02.Hhat(i,:) = mod_int.Hhat(2);
  
    mod_out.con_m03.nhat(i,:) = mod_int.nhat(3:4,1)';
    mod_out.con_m03.Hhat(i,:) = mod_int.Hhat(3);
  
    mod_out.con_m04.nhat(i,:) = mod_int.nhat(5:6,1)';
    mod_out.con_m04.Hhat(i,:) = mod_int.Hhat(4);
  
    mod_out.con_m05.nhat(i,:) = mod_int.nhat(7:7,1)';
    mod_out.con_m05.Hhat(i,:) = mod_int.Hhat(5);
  
    mod_out.con_m06.nhat(i,:) = mod_int.nhat(8:11,1)';
    mod_out.con_m06.Hhat(i,:) = mod_int.Hhat(6);
  
    mod_out.con_m07.nhat(i,:) = mod_int.nhat(12:13,1)';
    mod_out.con_m07.Hhat(i,:) = mod_int.Hhat(7);
  
    mod_out.con_m08.nhat(i,:) = mod_int.nhat(14:14,1)';
    mod_out.con_m08.Hhat(i,:) = mod_int.Hhat(8);
  
    mod_out.con_h01.q(i,:) = mod_int.q(1);
  else
    switch(flag)
      case 'init'
        mod_out.t = []
        OutputBuild(t(1),xx,'');
    otherwise
      end  
  endif  
endfunction

function dxdt = f(t,xx)
  global WTBAR mod_int par;
  waitbar(t/par.tspan, WTBAR);
  
  % Initialize rate variables
  mod_int.nhat = zeros(14,1);
  mod_int.Hhat = zeros(8,1);
  mod_int.q = zeros(1,1);
  mod_int.r = zeros(1,1);
  
  % System equations
  % System 1 (  =8.1 Cooler)
  mod_int.c_sys01 = xx(1:1,1)/0.1;
  mod_int.T_sys01 = (xx(8,1) - xx(1:1,1)'*[5.0E+5])/(xx(1:1,1)'[1.0E+3]) + par.Tref;
  mod_int.hs_sys01 = [5.0E+5] + [1.0E+3]*(mod_int.T_sys01 - par.Tref);
  % System 2 ( )
  % System 3 ( )
  % System 4 ( )
  % System 6 ( )
  % System 7 ( )
  % System 8 ( )
  
  % Connection equations
  % Connection m01
  mod_int.nhat(1:1.1) = [1.0]*1.0;
  mod_int.Hhat(1,1) = mod_int.hs_sys04'*mod_int.nhat(1:1,1);
  % Connection m02
  % Connection m03
  % Connection m04
  % Connection m05
  % Connection m06
  % Connection m07
  % Connection m08
  
  % Connection h01
  mod_int.q(1,1) = 1.0E+3*1.0*(mod_int.T_sys01 - mod_int.T_sys02);
  
  % Reaction equations
  # Reaction 1: 2A + 3B => 8C
  mod_int.r(1) = 0.11*mod_int.c_sys02(1)^2*mod_int.c_sys028
  
  
  
endfunction

function P = SelectionMatrix(nS,S)
  if size(S,1)==1 & length(nS)==1
    P = sparse(size(S,2),nS);
    S = sort(S);
    for i=1:size(S,2)
      P(i,S(1,i))=1;
    endfor
  elseif isempty(S);
    P = sparse(0,nS);
  else
    error('Input should be a row vector')
  endif
endfunction

function A = StreamMatrix(num, con)
  if size(con,1) > 0
    A = sparse(num, size(con,1));
    for i=1:size(con,1)
      for j=1:2
        if con(i,j) <=num
          A(con(i,j),i) = (-1)^j;
        endif
      endfor
    endfor
  else
    A = 0;
  endif
endfunction

function H = HFromT(n,h0,cp,T,Tref)
  H = n'*(h0 + cp*(T-Tref);
endfunction

  
