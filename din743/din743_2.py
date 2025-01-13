import math as m
from dataclasses import dataclass

import din6885
from . import din743_3


@dataclass
class Kerbe:
    d : float
    """Bauteildurchmesser im Kerbquerschnitt """

    def sigma_zd(self, F_zd : float) -> float:
        return F_zd / (m.pi / 4 * self.d**2)
    def sigma_b(self, M_b : float) -> float:
        return M_b / (m.pi / 32 * self.d**3) * 1000
    def tau_t(self, M_t : float) -> float:
        return M_t / (m.pi / 16 * self.d**3) * 1000

    def __post_init__(self):
        self.msg_zd = str()
        self.msg_b = str()
        self.msg_t = str()
        if hasattr(self, "t"):
            self.D : float = self.d + 2 * self.t

    pass

@dataclass
class _K_F_nach_Welle_Nabe:
    """Tabelle 1"""
    def K_Fsigma(self, **_):
        return 1
    def K_Ftau(self, **_):
        return 1

@dataclass
class _K_F_nach_Formel:
    """Glg 18 & 19 bzw. 20 & 21"""
    def _K_Fsigma(self, Rz, sigma_B_d_eff):
        return 1 - 0.22 * m.log(Rz, 10) * (m.log(sigma_B_d_eff / 20, 10) - 1)
    def _K_Ftau(self, Rz, sigma_B_d_eff):
        return 0.575 * self._K_Fsigma(Rz, sigma_B_d_eff) + 0.425

    def K_Fsigma(self, Rz, sigma_B_d_eff):
        if hasattr(self, "Rz_B"):
           return self._K_Fsigma(Rz, sigma_B_d_eff) / self._K_Fsigma(self.Rz_B, sigma_B_d_eff)
        return self._K_Fsigma(Rz, sigma_B_d_eff)
    def K_Ftau(self, Rz, sigma_B_d_eff):
        if hasattr(self, "Rz_B"):
           return self._K_Ftau(Rz, sigma_B_d_eff) / self._K_Ftau(self.Rz_B, sigma_B_d_eff)
        return self._K_Ftau(Rz, sigma_B_d_eff)


@dataclass
class _ExperimentelleKerbwirkungszahlen(Kerbe):
    def beta_sigmazd(self, **kwargs):
        beta_d_BK = self.beta_sigmazd_d_BK(**kwargs)
        K_3_d = K_3(self.d, beta_d_BK)
        K_3_d_BK = K_3(self.d_BK, beta_d_BK)
        self.msg_zd += f"\tβ_σzd(d_BK) = {beta_d_BK}\n"
        self.msg_zd += f"\tK_3zd(d_BK) = {K_3_d_BK}\n"
        self.msg_zd += f"\tK_3zd(d) = {K_3_d}\n"
        return beta_d_BK * K_3_d_BK / K_3_d
    def beta_sigmab(self, **kwargs):
        beta_d_BK = self.beta_sigmab_d_BK(**kwargs)
        K_3_d = K_3(self.d, beta_d_BK) 
        K_3_d_BK = K_3(self.d_BK, beta_d_BK)
        self.msg_b += f"\tβ_σb(d_BK) = {beta_d_BK}\n"
        self.msg_b += f"\tK_3b(d_BK) = {K_3_d_BK}\n"
        self.msg_b += f"\tK_3b(d) = {K_3_d}\n"
        return beta_d_BK * K_3_d_BK / K_3_d
    def beta_tau(self, **kwargs):
        beta_d_BK = self.beta_tau_d_BK(**kwargs)
        K_3_d = K_3(self.d, beta_d_BK)
        K_3_d_BK = K_3(self.d_BK, beta_d_BK)
        self.msg_t += f"\tβ_τ(d_BK) = {beta_d_BK}\n"
        self.msg_t += f"\tK_3t(d_BK) = {K_3_d_BK}\n"
        self.msg_t += f"\tK_3t(d) = {K_3_d}\n"
        return beta_d_BK * K_3_d_BK / K_3_d

class Passfeder(din6885.Passfeder, _ExperimentelleKerbwirkungszahlen, _K_F_nach_Welle_Nabe):
    """Tabelle 1"""
    umdrehungskerbe = False
    d_BK = 40

    def __init__(self, passfeder : din6885.Passfeder, i : int):
        
        super().__init__(passfeder.d_1, passfeder.l, passfeder.form, passfeder.b, passfeder.h, passfeder.t_1)
        super(_ExperimentelleKerbwirkungszahlen, self).__init__(passfeder.d_1)

        self.i = i
        assert self.i in (1, 2)

        #super().__post_init__()
        pass

    def beta_sigmazd_d_BK(self, sigma_B_d: float, **_):
        return (3 * (sigma_B_d / 1000)**0.38) * (1.15 if self.i == 2 else 1)
    def beta_sigmab_d_BK(self, sigma_B_d: float, **_):
        return self.beta_sigmazd_d_BK(sigma_B_d)
    def beta_tau_d_BK(self, sigma_B_d: float, **_):
        return (0.56 * 3 * (sigma_B_d / 1000)**0.38 + 0.1) * (1.15 if self.i == 2 else 1)

@dataclass
class Presssitz(_ExperimentelleKerbwirkungszahlen, _K_F_nach_Welle_Nabe):
    """Tabelle 1"""
    umdrehungskerbe = True
    d_BK = 40

    def beta_sigmazd_d_BK(self, sigma_B_d: float, **_):
        return 2.7 * (sigma_B_d / 1000)**0.43
    def beta_sigmab_d_BK(self, sigma_B_d: float, **_):
        return self.beta_sigmazd_d_BK(sigma_B_d)
    def beta_tau_d_BK(self, sigma_B_d: float, **_):
        return 0.65 * self.beta_sigmab_d_BK(sigma_B_d)
    
@dataclass
class Spitzkerbe(_ExperimentelleKerbwirkungszahlen, _K_F_nach_Formel):
    """Abschnitt 4.2.3"""
    umdrehungskerbe = True
    r = 0.1
    d_BK = 15
    Rz_B = 20

    t : float

    def __post_init__(self):
        super().__post_init__()
        assert 0.05 <= self.t/self.d <= 0.2

    def beta_sigmazd_d_BK(self, sigma_B_d: float, **_):
        return 0.109 * sigma_B_d / 100 + 1.074
    def beta_sigmab_d_BK(self, sigma_B_d: float, **_):
        return 0.0923 * sigma_B_d / 100 + 0.985
    def beta_tau_d_BK(self, sigma_B_d: float, **_):
        return 0.8 * self.beta_sigmab_d_BK(sigma_B_d)
    
@dataclass
class UmlaufendeRechtecknut(_ExperimentelleKerbwirkungszahlen, _K_F_nach_Formel):
    """Abschnitt 4.2.4"""
    umdrehungskerbe = True
    d_BK = 30
    Rz_B = 20

    t : float
    r : float
    m : float

    def rho_s(self, sigma_S_d):
        return m.pow(10, -(0.514 + 0.00152 - sigma_S_d))

    def beta_s_sigmazd_d_BK(self, sigma_S_d: float):
        r_f = self.r + 2.9 * self.rho_s(sigma_S_d)
        return min(0.9 * (1.27 + 1.17 * m.sqrt(self.t / r_f)), 4)
    def beta_s_sigmab_d_BK(self, sigma_S_d: float):
        r_f = self.r + 2.9 * self.rho_s(sigma_S_d)
        return min(0.9 * (1.14 + 1.08 * m.sqrt(self.t / r_f)), 4)
    def beta_s_tau_d_BK(self, sigma_S_d: float):
        r_f = self.r + self.rho_s(sigma_S_d)
        return min(1.48 + 0.45 * m.sqrt(self.t / r_f), 2.5)

    def beta_sigmazd_d_BK(self, sigma_S_d: float, **_):
        if self.m / self.t >= 1.4:
            beta = self.beta_s_sigmazd_d_BK(sigma_S_d)
        else:
            beta = self.beta_s_sigmazd_d_BK(sigma_S_d) * 1.08 * m.pow(self.m / self.t, -0.2)
        return min(beta, 4)
    def beta_sigmab_d_BK(self, sigma_S_d: float, **_):
        if self.m / self.t >= 1.4:
            beta = self.beta_s_sigmab_d_BK(sigma_S_d)
        else:
            beta = self.beta_s_sigmab_d_BK(sigma_S_d) * 1.08 * m.pow(self.m / self.t, -0.2)
        return min(beta, 4)
    def beta_tau_d_BK(self, sigma_S_d: float, **_):
        if self.m / self.t >= 1.4:
            beta = self.beta_s_tau_d_BK(sigma_S_d)
        else:
            beta = self.beta_s_tau_d_BK(sigma_S_d) * 1.08 * m.pow(self.m / self.t, -0.2)
        return min(beta, 2.5)


@dataclass
class _BekannteFormzahl(Kerbe, _K_F_nach_Formel):
    """4.3.1"""
    def beta_sigmazd(self, **kwargs):
        alpha = self.alpha_sigmazd
        self.msg_zd += f"\tα_σzd = {alpha}\n"
        n = min(self.n_zd(**kwargs), alpha)
        self.msg_zd += f"\tn_zd = {n}\n"
        return alpha / n
    def beta_sigmab(self, **kwargs):
        alpha = self.alpha_sigmab
        self.msg_b += f"\tα_σb = {alpha}\n"
        n = min(self.n_b(**kwargs), alpha)
        self.msg_b += f"\tn_b = {n}\n"
        return alpha / n
    def beta_tau(self, **kwargs):
        alpha = self.alpha_tau
        self.msg_t += f"\tα_τ = {alpha}\n"
        n = min(self.n_t(**kwargs), alpha)
        self.msg_t += f"\tn_t = {n}\n"
        return alpha / n
    
    def n_zd(self, sigma_S_d, harte_randschicht, **_):
        G_s = self.G_s_zd
        self.msg_zd += f"\tG'_zd = {G_s}\n"
        if harte_randschicht:
            return 1 + m.sqrt(G_s) * 10 ** -0.7
        else:
            return 1 + m.sqrt(G_s) * 10 ** -(0.33 + sigma_S_d / 712)
    def n_b(self, sigma_S_d, harte_randschicht, **_):
        G_s = self.G_s_b
        self.msg_b += f"\tG'_b = {G_s}\n"
        if harte_randschicht:
            return 1 + m.sqrt(G_s) * 10 ** -0.7
        else:
            return 1 + m.sqrt(G_s) * 10 ** -(0.33 + sigma_S_d / 712)
    def n_t(self, sigma_S_d, harte_randschicht, **_):
        G_s = self.G_s_t
        self.msg_t += f"\tG'_t = {G_s}\n"
        if harte_randschicht:
            return 1 + m.sqrt(G_s) * 10 ** -0.7
        else:
            return 1 + m.sqrt(G_s) * 10 ** -(0.33 + sigma_S_d / 712)

@dataclass
class _AbsatzUndRundnut(_BekannteFormzahl):
    umdrehungskerbe = True

    def __post_init__(self):
        super().__post_init__()
        if self.d / self.D > 0.67 and self.r > 0:
            self.phi = 1 / (4 * m.sqrt(self.t / self.r) + 2)
        else:
            self.phi = 0.
        
        self.msg_zd += f"\tϕ = {self.phi}\n"
        self.msg_b += f"\tϕ = {self.phi}\n"
        self.msg_t += f"\tϕ = {self.phi}\n"

        self.alpha_sigmazd = self._alpha(self.A_zd, self.B_zd, self.C_zd, self.z_zd)
        self.alpha_sigmab = self._alpha(self.A_b, self.B_b, self.C_b, self.z_b)
        self.alpha_tau = self._alpha(self.A_t, self.B_t, self.C_t, self.z_t)

    def _alpha(self, A, B, C, z):
        alpha = 1 + 1 / m.sqrt(A * self.r / self.t + 2 * B * self.r / self.d * (1 + 2 * self.r / self.d)**2 + C * (self.r / self.t)**z * self.d / self.D)
        assert self.r / self.t >= 0.03
        assert self.d / self.D <= 0.98
        assert alpha <= 6
        return alpha
    
@dataclass
class Rundnut(_AbsatzUndRundnut):
    """Tabelle 2 & 3"""
    
    A_zd = 0.22
    A_b = 0.2
    A_t = 0.7
    B_zd = 1.37
    B_b = 2.75
    B_t = 10.3
    C_zd = 0
    C_b = 0
    C_t = 0
    z_zd = 0
    z_b = 0
    z_t = 0

    r : float
    t : float

    @property
    def G_s_zd(self):
        return 2 * (1 + self.phi) / self.r
    @property
    def G_s_b(self):
        return 2 * (1 + self.phi) / self.r
    @property
    def G_s_t(self):
        return 1 / self.r
    
@dataclass
class Absatz(_AbsatzUndRundnut):
    """Tabelle 2 & 3"""
    
    A_zd = 0.62
    A_b = 0.62
    A_t = 3.4
    B_zd = 3.5
    B_b = 5.8
    B_t = 19
    C_zd = 0
    C_b = 0.2
    C_t = 1
    z_zd = 0
    z_b = 3
    z_t = 2

    r : float
    t : float

    @property
    def G_s_zd(self):
        return 2.3 * (1 + self.phi) / self.r
    @property
    def G_s_b(self):
        return 2.3 * (1 + self.phi) / self.r
    @property
    def G_s_t(self):
        return 1.15 / self.r
    
@dataclass
class Freistrich(Absatz):
    """Abschnitt 5.2.2"""
    pass

@dataclass
class Querbohrung(_BekannteFormzahl):
    """Abschnitt 5.2.3 """
    umdrehungskerbe = False
    
    r : float

    def __post_init__(self):
        super().__post_init__()

        self.G_s_zd = 2.3 / self.r
        self.G_s_b = 2.3 / self.r + 2 / self.d
        self.G_s_t = 1.15 / self.r + 2 / self.d

        self.alpha_sigmazd = 3 - (2 * self.r / self.d)
        self.alpha_sigmab = 3 + 1.4 * (2 * self.r / self.d) - 2.8 * m.sqrt(2 * self.r / self.d)
        self.alpha_tau = 2.023 - 1.125 * m.sqrt(2 * self.r / self.d)

    def sigma_zd(self, F_zd):
        return F_zd / (m.pi * self.d**2 / 4 - 2 * self.r * self.d)
    def sigma_b(self, M_b):
        return M_b / (m.pi * self.d**3 / 32 - self.r * self.d**2 / 3) * 1000
    def tau_t(self, M_t):
        return M_t / (m.pi * self.d**3 / 16 - self.r * self.d**2 / 3) * 1000


def K_1(werkstoff_art: din743_3.Werkstoff.Art, d_eff, zugfestigkeit : bool):
    """
    Glg 10-14
    zugfestigkeit: True für sigma_B, False für sigma_S
    """
    streckgrenze = not zugfestigkeit
    if werkstoff_art == din743_3.Werkstoff.Art.Nitrierstahl or zugfestigkeit and werkstoff_art == din743_3.Werkstoff.Art.Baustahl:
        if d_eff <= 100:
            return 1.
        elif d_eff < 300:
            return 1 - 0.23 * m.log(d_eff / 100, 10)
        elif d_eff <= 500:
            return 0.89
    elif streckgrenze and werkstoff_art == din743_3.Werkstoff.Art.Baustahl:
        if d_eff <= 32:
            return 1.
        elif d_eff < 300:
            d_B = 16
            return 1 - 0.26 * m.log(d_eff / 2 / d_B, 10)
        elif d_eff <= 500:
            return 0.75
    elif werkstoff_art == din743_3.Werkstoff.Art.CrNiMoEinsatzstahl or zugfestigkeit and din743_3.Werkstoff.Art.vergüteterStahl:
        d_B = 16
        if d_eff <= 16:
            return 1.
        elif d_eff < 300:
            return 1 - 0.26 * m.log(d_eff / d_B, 10)
        elif d_eff <= 500:
            return 0.67
    elif werkstoff_art == din743_3.Werkstoff.Art.andererEinsatzstahl:
        if d_eff <= 16:
            return 1.
        elif d_eff < 150:
            d_B = 16
            return 1 - 0.41 * m.log(d_eff / d_B, 10)
        elif d_eff <= 500:
            return 0.6
    elif werkstoff_art == din743_3.Werkstoff.Art.vergüteterStahl:
        d_B = 16
        if d_eff <= 16:
            return 1.
        elif d_eff < 300:
            return 1 - 0.34 * m.log(d_eff / d_B, 10)
        elif d_eff <= 500:
            return 0.57

    raise NotImplementedError

def K_2_zd(d):
    """Glg 15"""
    return 1
def K_2_b(d):
    """Glg 16"""
    if 7.5 <= d < 150:
        return 1 - 0.2 * m.log(d / 7.5, 10) / m.log(20, 10)
    elif d >= 150:
        return 0.8
    raise NotImplementedError
def K_2_t(d):
    """Glg 16"""
    return K_2_b(d)

def K_3(d, alpha):
    if 7.5 <= d < 150:
        return 1 - 0.2 * m.log(alpha, 10) * m.log(d / 7.5, 10) / m.log(20, 10)
    elif d >= 150:
        return 1 - 0.2 * m.log(alpha)
    raise NotImplementedError