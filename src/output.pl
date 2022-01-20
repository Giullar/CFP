q(1).
not(tt, ff).
not(ff, tt).
and(tt, tt, tt).
and(tt, ff, ff).
and(ff, tt, ff).
and(ff, ff, ff).
or(tt, tt, tt).
or(tt, ff, tt).
or(ff, tt, tt).
or(ff, ff, ff).
query(ans(B,1)).
0.5::probatom(1).
0.5::probatom(2).
q(2):-q(1).
ans(B,1):-ans(B,2).
q(8):-q(3).
ans(B,3):-ans(B,8).
q(4):-q(2).
ans(B,2):-ans(B,4).
q(3):-q(5).
ans(B,5):-ans(B,3).
q(7):-q(6).
ans(B,6):-ans(B,7).
q(5):-q(4).
q(6):-q(4).
ans(X,4):-ans(A,5), ans(B,6), and(A,B,X).
ans(tt,7):-q(7), probatom(1).
ans(ff,7):-q(7), \+probatom(1).
ans(tt,8):-q(8), probatom(2).
ans(ff,8):-q(8), \+probatom(2).
