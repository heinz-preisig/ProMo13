
NKS = [-1 1 0; 0 -1 1];
xNS = [2 1 0 ; 0 0.5 1.5];
PNK = diag([1,1]);


[N,S] = size(xNS)
[K,S] = size(NKS)

y = zeros(n,s);

for k = 1:K
  for s = 1:S
    for n = 1:N
      y(n,s,k) = PNK(n,k) .* xNS(n,s);
    endfor
  endfor  
endfor

y

