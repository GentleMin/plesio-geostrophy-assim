# -*- coding: utf-8 -*-
"""
Expansion configuration file - 
Daria's expansion for Malkus background field, with only
coupling in equatorial components implemented, consistent
with `quad_malkus_reg_diff.nb`

.. warning:: This is now a historical version of the code, and will 
    no longer be actively maintained.
    For the current implementation of the original expansion
    as documented in Daria's MM code `quad_malkus_reg_diff.nb`, 
    use :py:mod:`~pg_utils.pg_model.expand_daria_mm_malkus` instead.

Jingtao Min @ ETH Zurich 2023
"""

import numpy as np
from sympy import *
from .core import s, p, t, H, H_s, pgvar_ptb
from .expansion import n, m, xi, xi_s, s_xi
from . import expansion, base

identifier = "expand_daria_malkus"


# Which equations to use
field_names = base.CollectionPG.pg_field_names[:14]
field_indexer = np.full(pgvar_ptb.n_fields, False, dtype='?')
field_indexer[:14] = True
subscript_str = [
    r"\Psi", "ss", r"\phi\phi", r"s\phi", "sz", r"\phi z",
    "zss", r"z\phi\phi", r"zs\phi", "es", r"e\phi", "ez", "es,z", r"e\phi,z"]


"""Fourier expansion"""

# fields
fields = pgvar_ptb.generate_collection(field_indexer)

# Fourier expansion
fourier_expand = expansion.FourierExpansions(
    expansion.omega*t + expansion.m*p, fields, 
    expansion.pgvar_s.generate_collection(field_indexer))


"""Radial expansion"""

# bases (placeholder)
bases_s = base.LabeledCollection(field_names,
    **{fname: Function(r"\Phi_{%s}^{mn}" % subscript_str[idx])(s) 
       for idx, fname in enumerate(field_names)})

# explicit expression for the radial bases
m_abs = Abs(m)
# prefactor_m = Piecewise(
#     (1, Eq(m, 0)), 
#     (s, Eq(m_abs, 1)), 
#     (s**(m_abs - 2), m_abs > 1))
prefactor_m = s**Abs(Abs(m_abs - S.One) - S.One)
# beta_m = Piecewise(
#     (-Rational(1, 2), Eq(m, 0)), 
#     (Rational(1, 2), Eq(m_abs, 1)), 
#     (m_abs - Rational(5, 2), m_abs > 1))
beta_m = Abs(Abs(m_abs - S.One) - S.One) - Rational(1, 2)
coupling_p = Piecewise(
    (S.Zero, Eq(m, 0)),
    (S.One, m_abs > 0)
)
bases_s_expression = base.LabeledCollection(field_names,
    Psi = H_s**3*s**m_abs*jacobi(n, Rational(3, 2), m_abs, xi_s),
    # No coupling implemented for moments
    Mss = H_s*prefactor_m*jacobi(n, 1, beta_m, xi_s),
    Mpp = H_s*prefactor_m*jacobi(n, 1, beta_m, xi_s), 
    # Msp expr not consistent with thesis or new notebook (H_s)
    Msp = H_s**2*s**(Abs(m_abs - 2))*jacobi(n, 2, Abs(m_abs - 2) - Rational(1, 2), xi_s),
    Msz = H_s**2*s**(Abs(m_abs - 1))*jacobi(n, 2, Abs(m_abs - 1) - Rational(1, 2), xi_s),
    Mpz = H_s**2*s**(Abs(m_abs - 1))*jacobi(n, 2, Abs(m_abs - 1) - Rational(1, 2), xi_s),
    zMss = H_s**2*prefactor_m*jacobi(n, 2, beta_m, xi_s),
    zMpp = H_s**2*prefactor_m*jacobi(n, 2, beta_m, xi_s),
    zMsp = H_s**2*s**(Abs(m_abs - 2))*jacobi(n, 2, Abs(m_abs - 2) - Rational(1, 2), xi_s),
    # Coupling implemented for Bs_e, Bp_e,
    Bs_e = H_s**2*s**(Abs(m_abs - 1))*jacobi(n, 2, Abs(m_abs - 1) - Rational(1, 2), xi_s),
    Bp_e = s**(Abs(m_abs - 1) + 2*coupling_p)*jacobi(n, 0, Abs(m_abs - 1) + 2*coupling_p - Rational(1, 2), xi_s),
    Bz_e = H_s**2*s**m_abs*jacobi(n, 2, m_abs - Rational(1, 2), xi_s),
    dBs_dz_e = H_s**2*s**(Abs(m_abs - 1))*jacobi(n, 2, Abs(m_abs - 1) - Rational(1, 2), xi_s),
    dBp_dz_e = H_s**2*s**(Abs(m_abs - 1))*jacobi(n, 2, Abs(m_abs - 1) - Rational(1, 2), xi_s)
)

# coefficients
coeff_s = base.LabeledCollection(field_names,
    **{fname: Symbol(r"C_{%s}^{mn}" % subscript_str[idx])
       for idx, fname in enumerate(field_names)})

rad_expand = expansion.RadialExpansions(fourier_expand.coeffs, bases_s, coeff_s,
    Psi = coeff_s.Psi*bases_s.Psi,
    Mss = coeff_s.Mss*bases_s.Mss,
    Mpp = coeff_s.Mpp*bases_s.Mpp,
    Msp = coeff_s.Msp*bases_s.Msp,
    Msz = coeff_s.Msz*bases_s.Msz,
    Mpz = coeff_s.Mpz*bases_s.Mpz,
    zMss = coeff_s.zMss*bases_s.zMss,
    zMpp = coeff_s.zMpp*bases_s.zMpp,
    zMsp = coeff_s.zMsp*bases_s.zMsp,
    # For future reference, this is how the coupling can be implemented
    Bs_e = coeff_s.Bs_e*bases_s.Bs_e,
    Bp_e = coeff_s.Bp_e*bases_s.Bp_e + I*sign(m)*coupling_p*coeff_s.Bs_e*bases_s.Bs_e,
    Bz_e = coeff_s.Bz_e*bases_s.Bz_e,
    dBs_dz_e = coeff_s.dBs_dz_e*bases_s.dBs_dz_e,
    dBp_dz_e = coeff_s.dBp_dz_e*bases_s.dBp_dz_e
)

"""Test functions"""

# test_s = expansion.RadialTestFunctions(field_names,
#     Psi = bases_s.Psi,
#     Mss = bases_s.Mss,
#     Mpp = bases_s.Mpp,
#     Msp = bases_s.Msp,
#     Msz = bases_s.Msz,
#     Mpz = bases_s.Mpz,
#     zMss = bases_s.zMss,
#     zMpp = bases_s.zMpp,
#     zMsp = bases_s.zMsp,
#     Bs_e = bases_s.Bs_e,
#     Bp_e = bases_s.Bp_e,
#     Bz_e = bases_s.Bz_e,
#     dBs_dz_e = bases_s.dBs_dz_e,
#     dBp_dz_e = bases_s.dBp_dz_e
# )

# Even when the test functions are the same with the trial functions
# It is required that they use different indices (or different placeholders)
# so that the two can be distinguished.
test_s = base.LabeledCollection(field_names,
    **{fname: Function(r"\Phi_{%s}^{mn'}" % subscript_str[idx])(s) 
       for idx, fname in enumerate(field_names)})


"""Inner products"""

inner_prod_op = expansion.RadialInnerProducts(field_names,
    Psi = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    Mss = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    Mpp = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    Msp = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    Msz = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    Mpz = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    zMss = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    zMpp = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    zMsp = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    Bs_e = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    Bp_e = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    Bz_e = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    dBs_dz_e = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One)),
    dBp_dz_e = expansion.InnerProductOp1D(s, S.One, (S.Zero, S.One))
)

recipe = expansion.ExpansionRecipe(
    identifier=identifier,
    fourier_expand=fourier_expand,
    rad_expand=rad_expand,
    rad_test=test_s,
    inner_prod_op=inner_prod_op,
    base_expr=bases_s_expression.subs({n: expansion.n_trial}),
    test_expr=bases_s_expression.subs({n: expansion.n_test})
)

