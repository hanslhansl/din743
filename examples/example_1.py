import din743
import din6885

werkstoff = din743.din743_3.S500
K_A = 1.75
K_S = 2.5



lamellenkupplung = din743.Calculator(fall = 2,
    werkstoff = werkstoff,
    kerbe = din743.din743_2.Passfeder(din6885.PassfederHoheForm(30, 0, din6885.Passfeder.Form.A), 2),
    d_eff = 56,
    F_zdm = 0,
    F_zda = 0,
    F_zdmax = 0,
    M_bm = 0,
    M_ba = 0,
    M_bmax = 0,
    M_tm = 535.93,
    M_ta = 0,
    M_tmax = 535.93 * K_S,
    Rz = 16,
    K_V = 1,
    harte_randschicht = False)
print()

ritzel = din743.Calculator(fall = 2,
    werkstoff = lamellenkupplung.werkstoff,
    kerbe = din743.din743_2.Passfeder(din6885.PassfederHoheForm(50, 0, din6885.Passfeder.Form.A), 1),
    d_eff = 56,
    F_zdm = 0,
    F_zda = 0,
    F_zdmax = 0,
    M_bm = 0,
    M_ba = 450.256 * K_A,
    M_bmax = 450.256 * K_S,
    M_tm = 535.93,
    M_ta = 0,
    M_tmax = 535.93 * K_S,
    Rz = 16,
    K_V = 1,
    harte_randschicht = False)
print()

rad = din743.Calculator(fall = 2,
    werkstoff = werkstoff,
    kerbe = din743.din743_2.Passfeder(din6885.PassfederHoheForm(70, 0, din6885.Passfeder.Form.A), 2),
    d_eff = 78,
    F_zdm = 0,
    F_zda = 0,
    F_zdmax = 0,
    M_bm = 0,
    M_ba = 313.678 * K_A, 
    M_bmax = 313.678 * K_S,
    M_tm = 2933.511,
    M_ta = 0, 
    M_tmax = 2933.511 * K_S,
    Rz = 16,
    K_V = 1,
    harte_randschicht = False)
print()

drehstarr = din743.Calculator(fall = 2,
    werkstoff = rad.werkstoff,
    kerbe = din743.din743_2.Passfeder(din6885.PassfederHoheForm(55, 0, din6885.Passfeder.Form.A), 2),
    d_eff = 78,
    F_zdm = 0, 
    F_zda = 0, 
    F_zdmax = 0,
    M_bm = 0,
    M_ba = 0, 
    M_bmax = 0,
    M_tm = 2933.511,
    M_ta = 0, 
    M_tmax = 2933.511 * K_S,
    Rz = 16,
    K_V = 1,
    harte_randschicht = False)
print()

absatz1 = din743.Calculator(fall = 2,
    werkstoff = werkstoff,
    kerbe = din743.din743_2.Absatz(d = 60, r = 1, t = 5),
    d_eff = 78,
    F_zdm = 0, 
    F_zda = 0,
    F_zdmax = 0,
    M_bm = 0,
    M_ba = 135.977 * K_A,
    M_bmax = 135.977 * K_S,
    M_tm = 2933.511,
    M_ta = 0,
    M_tmax = 2933.511 * K_S,
    Rz = 16,
    K_V = 1,
    harte_randschicht = False)
print()

absatz2 = din743.Calculator(fall = 2,
    werkstoff = werkstoff,
    kerbe = din743.din743_2.Absatz(d = 70, r = 1, t = 4),
    d_eff = 78,
    F_zdm = 0,
    F_zda = 0,
    F_zdmax = 0,
    M_bm = 0,
    M_ba = 131.175 * K_A,
    M_bmax = 131.175 * K_S,
    M_tm = 2933.511,
    M_ta = 0, 
    M_tmax = 2933.511 * K_S,
    Rz = 16,
    K_V = 1,
    harte_randschicht = False)
print()

absatz3 = din743.Calculator(fall = 2,
    werkstoff = werkstoff,
    kerbe = din743.din743_2.Absatz(d = 60, r = 1, t = 9),
    d_eff = 78,
    F_zdm = 0,
    F_zda = 0,
    F_zdmax = 0,
    M_bm = 0,
    M_ba = 6.003 * K_A,
    M_bmax = 6.003 * K_S,
    M_tm = 2933.511,
    M_ta = 0,
    M_tmax = 2933.511 * K_S,
    Rz = 16,
    K_V = 1,
    harte_randschicht = False)
print()

freistrich1 = din743.Calculator(fall = 2,
    werkstoff = werkstoff,
    kerbe = din743.din743_2.Freistrich(d = 55.4, r = 1, t = 2.3),
    d_eff = 78,
    F_zdm = 0,
    F_zda = 0,
    F_zdmax = 0,
    M_bm = 0,
    M_ba = 0,
    M_bmax = 0,
    M_tm = 2933.511,
    M_ta = 0, 
    M_tmax = 2933.511 * K_S,
    Rz = 16,
    K_V = 1,
    harte_randschicht = False)
print()