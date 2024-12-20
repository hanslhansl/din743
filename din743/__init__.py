"""
Implementiert die DIN 743 zur Tragfähigkeitsberechnung von Wellen und Achsen.

Siehe https://github.com/hanslhansl/din743.
"""


from typing import Literal, Optional
from .din743_1 import *
from .din743_2 import *
from .din743_3 import *

# enable colored console output on windows
import colorama
colorama.just_fix_windows_console()


class Calculator:
    """Führt alle 3 Teile der DIN 743 in einer Klasse zusammen"""

    @staticmethod
    def _check_safety(val, min_or_interv, name, full_name, _print):
        is_safe = True
        if val == float("inf"):
            _print("\033[33m", full_name, " nicht berechnet\033[0m", sep="")
        else:
            if isinstance(min_or_interv, tuple):
                res = min_or_interv[0] <= val <= min_or_interv[1]
                if res:
                    _print("\033[32m", name, " = ", val, " in ", min_or_interv, "\033[0m", sep="")
                else:
                    _print("\033[31m", name, " = ", val, " not in ", min_or_interv, ", ", full_name, " ist nicht erfüllt\033[0m", sep="")
                    is_safe = False
            else:
                res = min_or_interv <= val
                if res:
                    _print("\033[32m", name, " = ", val, " >= ", min_or_interv, "\033[0m", sep="")
                else:
                    _print("\033[31m", name, " = ", val, " < ", min_or_interv, ", ", full_name, " ist nicht erfüllt\033[0m", sep="")
                    is_safe = False
        return is_safe

    def __init__(self,
                fall : Literal[1, 2],
                werkstoff : Werkstoff,
                kerbe : Kerbe,
                d_eff : float,
                F_zdm : float, F_zda : float, F_zdmax : float, M_bm : float, M_ba : float, M_bmax : float, M_tm : float, M_ta : float, M_tmax : float,
                Rz : float,
                K_V : float,
                harte_randschicht : bool,
                hohlwelle : bool = False,

                K_1B_d_eff : Optional[float] = None,
                K_1S_d_eff : Optional[float] = None,
                K_2zd_d : Optional[float] = None,
                K_2b_d : Optional[float] = None,
                K_2t_d : Optional[float] = None,
                K_Fsigma : Optional[float] = None,
                K_Ftau : Optional[float] = None,
                beta_sigmazd : Optional[float] = None,
                beta_sigmab : Optional[float] = None,
                beta_tau : Optional[float] = None,
                K_sigmazd : Optional[float] = None,
                K_sigmab : Optional[float] = None,
                K_tau : Optional[float] = None,
                S_min : float | tuple[float, float] = 1.2,

                _print = print,
                _assert = False,
                print_all = False):
        """
        Im Druckbereich sind sigma_zdm und sigma_bm negativ
        - d_eff: für die Wärmebehandlung maßgebender Durchmesser
        """
        assert(fall in (1, 2))

        self.fall = fall
        self.werkstoff = werkstoff
        self.kerbe = kerbe
        self.d_eff = d_eff
        self.Rz = Rz
        self.K_V = K_V
        self.harte_randschicht = harte_randschicht
        self.hohlwelle = hohlwelle

        self.K_1B_d_eff = K_1B_d_eff
        self.K_1S_d_eff = K_1S_d_eff
        self.K_2zd_d = K_2zd_d
        self.K_2b_d = K_2b_d
        self.K_2t_d = K_2t_d
        self.K_Fsigma = K_Fsigma
        self.K_Ftau = K_Ftau
        self.beta_sigmazd = beta_sigmazd
        self.beta_sigmab = beta_sigmab
        self.beta_tau = beta_tau
        self.K_sigmazd = K_sigmazd
        self.K_sigmab = K_sigmab
        self.K_tau = K_tau

        [_print(key, "=", value) for key, value in vars(self).items() if value != None]

        self.sigma_zdm = self.kerbe.sigma_zd(F_zdm)
        self.sigma_zda = self.kerbe.sigma_zd(F_zda)
        self.sigma_zdmax = self.kerbe.sigma_zd(F_zdmax)
        _print("σ_zdm =", self.sigma_zdm)
        _print("σ_zda =", self.sigma_zda)
        _print("σ_zdmax =", self.sigma_zdmax)

        self.sigma_bm = self.kerbe.sigma_b(M_bm)
        self.sigma_ba = self.kerbe.sigma_b(M_ba)
        self.sigma_bmax = self.kerbe.sigma_b(M_bmax)
        _print("σ_bm =", self.sigma_bm)
        _print("σ_ba =", self.sigma_ba)
        _print("σ_bmax =", self.sigma_bmax)

        self.tau_tm = self.kerbe.tau_t(M_tm)
        self.tau_ta = self.kerbe.tau_t(M_ta)
        self.tau_tmax = self.kerbe.tau_t(M_tmax)
        _print("τ_tm =", self.tau_tm)
        _print("τ_ta =", self.tau_ta)
        _print("τ_tmax =", self.tau_tmax)

        self.sigma_B_d_B = self.werkstoff.sigma_B_d_B
        self.sigma_S_d_B = self.werkstoff.sigma_S_d_B
        _print("σ_B(d_B) =", self.sigma_B_d_B)
        _print("σ_S(d_B) }", self.sigma_S_d_B)

        zda = self.sigma_zda != 0 or print_all
        ba = self.sigma_ba != 0 or print_all
        ta = self.tau_ta != 0 or print_all
        zdmax = self.sigma_zdmax != 0 or print_all
        bmax = self.sigma_bmax != 0 or print_all
        tmax = self.tau_tmax != 0 or print_all

        self.sigma_zdW_d_B = self.werkstoff.sigma_zdW_d_B
        self.sigma_bW_d_B = self.werkstoff.sigma_bW_d_B
        self.tau_tW_d_B = self.werkstoff.tau_tW_d_B
        if zda:
            _print("σ_zdW(d_B) =", self.sigma_zdW_d_B)
        if ba:
            _print("σ_bW(d_B) =", self.sigma_bW_d_B)
        if ta:
            _print("τ_tW(d_B) =", self.tau_tW_d_B)

        if self.K_1B_d_eff == None:
            self.K_1B_d_eff = K_1(werkstoff_art=self.werkstoff.art, d_eff=self.d_eff, zugfestigkeit=True)
        if self.K_1S_d_eff == None:
            self.K_1S_d_eff = K_1(werkstoff_art=self.werkstoff.art, d_eff=self.d_eff, zugfestigkeit=False)
        _print("K_1B(d_eff) =", self.K_1B_d_eff)
        _print("K_1S(d_eff) =", self.K_1S_d_eff)

        if self.K_2zd_d == None:
            self.K_2zd_d = K_2_zd(d=self.kerbe.d)
        if self.K_2b_d == None:
            self.K_2b_d = K_2_b(d=self.kerbe.d)
        if self.K_2t_d == None:
            self.K_2t_d = K_2_t(d=self.kerbe.d)
        if zda:
            _print("K_2zd(d) =", self.K_2zd_d)
        if ba:
            _print("K_2b(d) =", self.K_2b_d)
        if ta:
            _print("K_2t(d) =", self.K_2t_d)

        self.sigma_B_d_eff = sigma_B_d_eff(self.K_1B_d_eff, self.sigma_B_d_B)
        _print("σ_B(d_eff) =", self.sigma_B_d_eff)
        self.sigma_B_d = sigma_B_d(self.sigma_B_d_B, self.K_1B_d_eff)
        _print("σ_B(d) =", self.sigma_B_d)
        self.sigma_S_d = sigma_S_d(self.sigma_S_d_B, self.K_1S_d_eff)
        _print("σ_S(d) =", self.sigma_S_d)

        if self.K_Fsigma == None:
            self.K_Fsigma = self.kerbe.K_Fsigma(Rz=self.Rz, sigma_B_d_eff=self.sigma_B_d_eff)
        if self.K_Ftau == None:
            self.K_Ftau = self.kerbe.K_Ftau(Rz=self.Rz, sigma_B_d_eff=self.sigma_B_d_eff)
        if zda or ba:
            _print("K_Fσ =", self.K_Fsigma)
        if ta:
            _print("K_Fτ =", self.K_Ftau)

        if self.beta_sigmazd == None:
            self.beta_sigmazd = kerbe.beta_sigmazd(sigma_B_d=self.sigma_B_d, sigma_S_d=self.sigma_S_d, harte_randschicht=self.harte_randschicht)
        if self.beta_sigmab == None:
            self.beta_sigmab = kerbe.beta_sigmab(sigma_B_d=self.sigma_B_d, sigma_S_d=self.sigma_S_d, harte_randschicht=self.harte_randschicht)
        if self.beta_tau == None:
            self.beta_tau = kerbe.beta_tau(sigma_B_d=self.sigma_B_d, sigma_S_d=self.sigma_S_d, harte_randschicht=self.harte_randschicht)
        if zda:
            _print(kerbe.msg_zd, end="")
            _print("β_σzd =", self.beta_sigmazd)
        if ba:
            _print(kerbe.msg_b, end="")
            _print("β_σb =", self.beta_sigmab)
        if ta:
            _print(kerbe.msg_t, end="")
            _print("β_τ =", self.beta_tau)
  
        if self.K_sigmazd == None:
            self.K_sigmazd = din743_1.K_sigmazd(self.beta_sigmazd, self.K_2zd_d, self.K_Fsigma, self.K_V)
        if self.K_sigmab == None:
            self.K_sigmab = din743_1.K_sigmab(self.beta_sigmab, self.K_2b_d, self.K_Fsigma, self.K_V)
        if self.K_tau == None:
            self.K_tau = din743_1.K_tau(self.beta_tau, self.K_2t_d, self.K_Ftau, self.K_V)
        if zda:
            _print("K_σzd =", self.K_sigmazd)
        if ba:
            _print("K_σb =", self.K_sigmab)
        if ta:
            _print("K_τ =", self.K_tau)

        self.sigma_zdWK = sigma_zdWK(self.sigma_zdW_d_B, self.K_1B_d_eff, self. K_sigmazd)
        self.sigma_bWK = sigma_bWK(self.sigma_bW_d_B, self.K_1B_d_eff, self.K_sigmab)
        self.tau_tWK = tau_tWK(self.tau_tW_d_B, self.K_1B_d_eff, self.K_tau)
        if zda:
            _print("σ_zdWK =", self.sigma_zdWK)
        if ba:
            _print("σ_bWK =", self.sigma_bWK)
        if ta:
            _print("τ_tWK =", self.tau_tWK)

        self.psi_zdsigmaK = psi_zdsigmaK(self.sigma_zdWK, self.K_1B_d_eff, self.sigma_B_d_B)
        self.psi_bsigmaK = psi_bsigmaK(self.sigma_bWK, self.K_1B_d_eff, self.sigma_B_d_B)
        self.psi_tauK = psi_tauK(self.tau_tWK, self.K_1B_d_eff, self.sigma_B_d_B)
        if zda:
            _print("ψ_zdσK =", self.psi_zdsigmaK)
        if ba:
            _print("ψ_bσK =", self.psi_bsigmaK)
        if ta:
            _print("ψ_τK =", self.psi_tauK)
            
        self.gamma_Fzd = gamma_Fzd(self.kerbe.alpha_sigmazd if hasattr(self.kerbe, "alpha_sigmazd") else self.beta_sigmazd, self.kerbe.umdrehungskerbe, self.harte_randschicht)
        self.gamma_Fb = gamma_Fb(self.kerbe.alpha_sigmab if hasattr(self.kerbe, "alpha_sigmab") else self.beta_sigmab, self.kerbe.umdrehungskerbe, self.harte_randschicht)
        self.gamma_Ft = gamma_Ft()
        if zda or zdmax:
            _print("γ_Fzd =", self.gamma_Fzd)
        if ba or bmax:
            _print("γ_Fb =", self.gamma_Fb)
        if ta or tmax:
            _print("γ_Ft =", self.gamma_Ft)

        self.K_2Fzd = K_2Fzd()
        self.K_2Fb = K_2Fb(self.harte_randschicht, self.hohlwelle)
        self.K_2Ft = K_2Ft(self.harte_randschicht, self.hohlwelle)
        if zda or zdmax:
            _print("K_2Fzd =", self.K_2Fzd)
        if ba or bmax:
            _print("K_2Fb =", self.K_2Fb)
        if ta or tmax:
            _print("K_2Ft =", self.K_2Ft)
        
        self.sigma_zdFK = sigma_zd_bFK(self.K_1S_d_eff, self.K_2Fzd, self.gamma_Fzd, self.sigma_S_d_B)
        self.sigma_bFK = sigma_zd_bFK(self.K_1S_d_eff, self.K_2Fb, self.gamma_Fb, self.sigma_S_d_B)
        self.tau_tFK = tau_tFK(self.K_1S_d_eff, self.K_2Ft, self.gamma_Ft, self.sigma_S_d_B)
        if zda or zdmax:
            _print("σ_zdFK =", self.sigma_zdFK)
        if ba or bmax:
            _print("σ_bFK =", self.sigma_bFK)
        if ta or tmax:
            _print("τ_tFK =", self.tau_tFK)
    
        self.sigma_mv, self.tau_mv, self.sigma_zdADK, self.sigma_bADK, self.tau_tADK = ADK(self.fall, self.sigma_zdm, self.sigma_bm, self.tau_tm,
                                                                                                     self.sigma_zda, self.sigma_ba, self.tau_ta,
                                                                                                     self.sigma_zdFK, self.sigma_bFK, self.tau_tFK,
                                                                                                     self.sigma_zdWK, self.sigma_bWK, self.tau_tWK,
                                                                                                     self.psi_zdsigmaK, self.psi_bsigmaK, self.psi_tauK,
                                                                                                     _print)
        if zda or ba or ta:
            _print("σ_mv =", self.sigma_mv)
        if ta:
            _print("τ_mv =", self.tau_mv)
        if zda:
            _print("σ_zdADK =", self.sigma_zdADK)
        if ba:
            _print("σ_bADK =", self.sigma_bADK)
        if ta:
            _print("τ_tADK =", self.tau_tADK)

        self.S_Dauer = S_Dauer(self.sigma_zda, self.sigma_ba, self.tau_ta, self.sigma_zdADK, self.sigma_bADK, self.tau_tADK)
        self.S_Verform = S_Verform(self.sigma_zdmax, self.sigma_bmax, self.tau_tmax, self.sigma_zdFK, self.sigma_bFK, self.tau_tFK)

        assert self._check_safety(self.S_Dauer, S_min, "S_Dauer", "Sicherheit gegen Dauerbruch", _print) or not _assert
        assert self._check_safety(self.S_Verform, S_min, "S_Verform", "Sicherheit gegen bleibende Verformungen", _print) or not _assert

        _print()
        return
    
    pass
