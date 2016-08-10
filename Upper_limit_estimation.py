from __future__ import division
import numpy as np
import math

G = 6.67408e-11 # 6.67408 * 10-11 m3 kg-1 s-2
G_cgs = G*(100**3)/(1000)

c = 299792458 # m1 s-2
c_cgs = c*100

pc = 3.0857e16 # m1
pc_cgs = pc*100
kpc_cgs = pc_cgs*1e3

def calc_EGW(frequency, tau, h_squared, distance_kpc):
    energy = np.pi**(5/2)*c_cgs**3*(distance_kpc*kpc_cgs)**2*frequency**2*h_squared/(2**(3/2)*G_cgs)
    return energy, energy*2/5

def calc_EGW_new(frequency, tau, h_squared, distance_kpc):
    #energy = ((c_cgs**3*np.pi**(3/2))/(5*np.sqrt(2)*G_cgs))*h_squared*(distance_kpc*kpc_cgs)**2*frequency**2*tau
    #energy = ((c_cgs**3*np.pi**(3/2))/(10*np.sqrt(2)*G_cgs))*h_squared*(distance_kpc*kpc_cgs)**2*frequency**2*tau
    energy = ((c_cgs**3*np.pi**(5/2))/(10*np.sqrt(2)*G_cgs))*h_squared*(distance_kpc*kpc_cgs)**2*frequency**2*tau
    return energy#, energy*2/5

def calc_hrss(frequency, tau, h_squared, distance_kpc):
    #hrss = np.sqrt(h_squared*tau)*(2*np.pi)**(1/4)/2
    hrss = np.sqrt(h_squared*tau)*(2*np.pi)**(1/4)/np.sqrt(2)
    return hrss

def calc_hrss_exact(frequency, tau, h_squared, distance_kpc, iota):
    #hrss = np.sqrt(h_squared*tau)*(2*np.pi)**(1/4)/2
    hrss = np.sqrt(h_squared*tau)*np.pi**(1/4)*np.sqrt((1 + np.cos(iota))**2/4 + np.cos(iota)**2 + ((1 + np.cos(iota))**2/4 - np.cos(iota)**2)*np.eps(-2*(np.pi*frequency*tau)**2))/(2*2**(1/4))
    return hrss

def str_truncate(number, decimal_values = 2):#"%.2f"):
    power_ten = np.floor(np.log10(number))
    truncated_number = str(int(np.round(number/np.power(10,power_ten)*np.power(10,decimal_values))))
    #truncated_number = truncated_number[0] + "." + truncated_number[1:] + "e" + str(int(power_ten))
    truncated_number = truncated_number[0] + "." + truncated_number[1:] + " \\times 10^{" + str(int(power_ten)) + "}"
    #trunkated_number = decimal_values % number
    #print(trunkated_number)
    return truncated_number

def make_printable_limits(frequency, tau, h_squared, distance_kpc, science_epoch, include_units = False, tau_f_columns = True):
    energy = calc_EGW_new(frequency, tau, h_squared, distance_kpc)
    hrss = calc_hrss(frequency, tau, h_squared, distance_kpc)
    calibration_factor = calculate_calibration_factor(science_epoch, frequency)
    #print("""	\hline
	#$f_0$ = """ + str(frequency) + ", $\\tau$ = " + str(tau) + " s, iota = 0 & " + str_truncate(np.sqrt(h_squared)) +
    #      " ("+str_truncate(h_squared)+") & " + str_truncate(hrss) + " & "+str(distance_kpc)+" kpc & "+ str_truncate(energy) +""" ergs \\\\""")
    if include_units:
        print("""	\hline
	$f_0$ = """ + str(frequency) + ", $\\tau$ = " + str(tau) + " s & $" + str_truncate(np.sqrt(h_squared)) +
          "$ & $" + str_truncate(hrss) + "$ & $" + str_truncate(hrss*np.sqrt(calibration_factor)) + "$ & " + str(distance_kpc)+" kpc & $"+ str_truncate(energy) + " \\ergs$ & $" + str_truncate(energy*calibration_factor) + " \\ergs$ \\\\")
    else:
        if not tau_f_columns:
            print("""	\hline
	$f_0 = \\SI{""" + str(frequency) + "}{\Hz}$ & $" + str_truncate(np.sqrt(h_squared)) +
          "$ & $" + str_truncate(hrss) + "$ & $" + str_truncate(hrss*np.sqrt(calibration_factor)) + "$ & " + str(distance_kpc)+" & $"+ str_truncate(energy) + "$ & $" + str_truncate(energy*calibration_factor) + "$ \\\\")
        else:
            #print("""	\hline
            print("""
	""" + str(frequency) + " & " + str(tau) + " & $" + str_truncate(np.sqrt(h_squared)) +
          "$ & $" + str_truncate(hrss) + "$ & $" + str_truncate(hrss*np.sqrt(calibration_factor)) + "$ & " + str(distance_kpc)+" & $"+ str_truncate(energy) + "$ & $" + str_truncate(energy*calibration_factor) + "$ \\\\")

def calculate_calibration_factor(science_epoch, frequency):
    max_timing_error = 45*1e-6# 45 microseconds
    A_H1 = 1.014
    A_L1 = 1.02
    Aplus_H1 = 0.025
    Aplus_L1 = 0.13
    if science_epoch == "S6B":
        delta_H1 = 0.09
        delta_L1 = 0.14
        phase_error_H1 = np.radians(5)
        phase_error_L1 = np.radians(10)
    elif science_epoch == "S6C":
        delta_H1 = 0.16
        delta_L1 = 0.19
        phase_error_H1 = np.radians(5)
        phase_error_L1 = np.radians(8)

    factor = A_H1*A_L1*(1 + np.sqrt(Aplus_H1**2 + Aplus_L1**2 + delta_H1**2 + delta_L1**2))/np.cos(2*np.pi*frequency*max_timing_error + phase_error_H1 + phase_error_L1)
    return factor

def make_printable_percentage_dif(frequency, tau, h_squared, distance_kpc, science_epoch):
    hrss = calc_hrss(frequency, tau, h_squared, distance_kpc)
    #energy = calc_EGW_new(frequency, tau, h_squared, distance_kpc)
    calibration_factor = calculate_calibration_factor(science_epoch, frequency)
    #factor_of_interest = (calibration_factor - 1)*100
    factor_of_interest = (np.sqrt(calibration_factor) - 1)*100
    #print("""	\hline
	#$f_0$ = """ + str(frequency) + ", $\\tau$ = " + str(tau) + " s & " + str_truncate(np.sqrt(h_squared)) +
    #      " & " + str(distance_kpc)+" kpc & "+ str_truncate(energy) + " ergs & " + str_truncate(energy*calibration_factor) + " ergs & " +
    #      str(math.floor(factor_of_interest+0.5)) + "% \\\\")
    #print("""	\hline
	#$f_0$ = """ + str(frequency) + ", $\\tau$ = " + str(tau) + " s & $" + str_truncate(np.sqrt(h_squared)) +
    #      "$ & " + str(distance_kpc)+" kpc & $"+ str_truncate(hrss) + "$ & $" + str_truncate(hrss*np.sqrt(calibration_factor)) + "$ & " +
    #      str(math.floor(factor_of_interest+0.5)) + "\\% \\\\")

    print("""
	""" + str(frequency) + " & " + str(tau) + " & $" + str_truncate(np.sqrt(h_squared)) +
          "$ & " + str(distance_kpc)+" & $"+ str_truncate(hrss) + "$ & $" + str_truncate(hrss*np.sqrt(calibration_factor)) + "$ & " +
          str(math.floor(factor_of_interest+0.5)) + " \\\\")

print("trigger 2469")
print("tau 400 s")
print(calc_EGW(150, 400, 1.14e-44, 10))
print(calc_EGW_new(150, 400, 1.14e-44, 10))

print("tau 150 s")
print(calc_EGW(150, 150, 6.49980768946e-44, 10))
print(calc_EGW_new(150, 150, 6.49980768946e-44, 10))

print("trigger 2471")
print("tau 400 s")
x = calc_EGW(150, 400, 2.48613120488e-44, 10)
print(x)
#print(x)
print(calc_EGW_new(150, 400, 2.48613120488e-44, 10))

print("tau 150 s")
print(calc_EGW(150, 150, 5.7986417149e-44, 10))
print(calc_EGW_new(150, 150, 5.7986417149e-44, 10))

print("trigger 2475")
print("tau 400 s")
print(calc_EGW(150, 400, 8.43190929288e-45, 10))
print(calc_EGW_new(150, 400, 8.43190929288e-45, 10))

print("tau 150 s")
print(calc_EGW(150, 150, 1.6e-43, 10))
print(calc_EGW_new(150, 150, 1.6e-43, 10))

#column_detail = " & & & & \\\\"
column_detail = " & & & & & & \\\\"
column_detail_2 = " & & & & & \\\\"

"""
2469

150
400
8.8e-45, 1.14e-44
150
6.45e-44, 8.2e-44

450
400
2.26e-44, 3.1125e-44
150
1.05470374987e-43, 1.5e-43

750
400
3.776e-44, 5.12551824228e-44
150
1.75e-43, 2.3e-43
"""
print("90% CL")
print("""	\\hline
	\multicolumn{8}{| c |}{SGR trigger 2469} \T \B \\\\
	\hline""")
make_printable_limits(150, 400, 1.14e-44, 8.7, "S6B")
#make_printable_limits(150, 150, 6.49980768946e-44, 8.7)
make_printable_limits(450, 400, 3.1125e-44, 8.7, "S6B")
make_printable_limits(750, 400, 5.12551824228e-44, 8.7, "S6B")
make_printable_limits(150, 150, 8.1e-44, 8.7, "S6B")
make_printable_limits(450, 150, 1.5e-43, 8.7, "S6B")
make_printable_limits(750, 150, 2.3e-43, 8.7, "S6B")
print("""	\\hline
	\multicolumn{8}{| c |}{SGR trigger 2471} \T \B \\\\
	\hline""")
make_printable_limits(150, 400, 2.48613120488e-44, 8.7, "S6C")
make_printable_limits(450, 400, 1.09e-43, 8.7, "S6C")
make_printable_limits(750, 400, 1.5e-43, 8.7, "S6C")
make_printable_limits(150, 150, 4.5e-43, 8.7, "S6C")
make_printable_limits(450, 150, 1.2e-42, 8.7, "S6C")
make_printable_limits(750, 150, 1.8e-42, 8.7, "S6C")
print("""	\\hline
	\multicolumn{8}{| c |}{SGR trigger 2475} \T \B \\\\
	\hline""")
make_printable_limits(150, 400, 7.5e-45, 8.5, "S6C")
make_printable_limits(450, 400, 1.992741788e-44, 8.5, "S6C")
make_printable_limits(750, 400, 4.3e-44, 8.5, "S6C")
make_printable_limits(150, 150, 1.45e-43, 8.5, "S6C")
make_printable_limits(450, 150, 1.681e-43, 8.5, "S6C")
make_printable_limits(750, 150, 3.45e-43, 8.5, "S6C")
print("50% CL")

print("""	\hline
	\multicolumn{8}{| c |}{SGR trigger 2469} \T \B \\\\
	\hline""")
make_printable_limits(150, 400, 8.8e-45, 8.7, "S6B")
#make_printable_limits(150, 150, 4.64158883361e-44, 8.7)
make_printable_limits(450, 400, 2.26e-44, 8.7, "S6B")
make_printable_limits(750, 400, 3.776e-44, 8.7, "S6B")
make_printable_limits(150, 150, 5.03e-44, 8.7, "S6B")
make_printable_limits(450, 150, 1.05470374987e-43, 8.7, "S6B")
make_printable_limits(750, 150, 1.75e-43, 8.7, "S6B")
print("""	\hline
	\multicolumn{8}{| c |}{SGR trigger 2471} \T \B \\\\
	\hline""")
make_printable_limits(150, 400, 1.365e-44, 8.7, "S6C")
make_printable_limits(450, 400, 7.25e-44, 8.7, "S6C")
make_printable_limits(750, 400, 9e-44, 8.7, "S6C")
make_printable_limits(150, 150, 1.75e-43, 8.7, "S6C")
make_printable_limits(450, 150, 5.1e-43, 8.7, "S6C")
make_printable_limits(750, 150, 8.6e-43, 8.7, "S6C")
print("""	\hline
	\multicolumn{8}{| c |}{SGR trigger 2475} \T \B \\\\
	\hline""")
make_printable_limits(150, 400, 5.75e-45, 8.5, "S6C")
make_printable_limits(450, 400, 1.255e-44, 8.5, "S6C")
make_printable_limits(750, 400, 2.705e-44, 8.5, "S6C")
make_printable_limits(150, 150, 6e-44, 8.5, "S6C")
make_printable_limits(450, 150, 9.3e-44, 8.5, "S6C")
make_printable_limits(750, 150, 2.325e-43, 8.5, "S6C")

print("percentage plot")

print("""	\\hline
	2469""" + column_detail_2)
make_printable_percentage_dif(150, 400, 8.8e-45, 8.7, "S6B")
#make_printable_limits(150, 150, 4.64158883361e-44, 8.7)
make_printable_percentage_dif(450, 400, 2.26e-44, 8.7, "S6B")
make_printable_percentage_dif(750, 400, 3.776e-44, 8.7, "S6B")
make_printable_percentage_dif(150, 150, 5.03e-44, 8.7, "S6B")
make_printable_percentage_dif(450, 150, 1.05470374987e-43, 8.7, "S6B")
make_printable_percentage_dif(750, 150, 1.75e-43, 8.7, "S6B")
print("""	\\hline
	2471""" + column_detail_2)
make_printable_percentage_dif(150, 400, 1.365e-44, 8.7, "S6C")
make_printable_percentage_dif(450, 400, 7.25e-44, 8.7, "S6C")
make_printable_percentage_dif(750, 400, 9e-44, 8.7, "S6C")
make_printable_percentage_dif(150, 150, 1.75e-43, 8.7, "S6C")
make_printable_percentage_dif(450, 150, 5.1e-43, 8.7, "S6C")
make_printable_percentage_dif(750, 150, 8.6e-43, 8.7, "S6C")
print("""	\\hline
	2475""" + column_detail_2)
make_printable_percentage_dif(150, 400, 5.75e-45, 8.5, "S6C")
make_printable_percentage_dif(450, 400, 1.255e-44, 8.5, "S6C")
make_printable_percentage_dif(750, 400, 2.705e-44, 8.5, "S6C")
make_printable_percentage_dif(150, 150, 6e-44, 8.5, "S6C")
make_printable_percentage_dif(450, 150, 9.3e-44, 8.5, "S6C")
make_printable_percentage_dif(750, 150, 2.325e-43, 8.5, "S6C")


print("alternate polarizations")

print("90% CL")
print("""	\\hline
	2469 ($\iota = 120\\angulardegree$)""" + column_detail)
#make_printable_limits(150, 400, 6.34554803193e-44, 8.7, "S6B")
#make_printable_limits(750, 400, 1.8e-42, 8.7, "S6B")
make_printable_limits(150, 400, 6.52852114113e-44, 8.7, "S6B")
make_printable_limits(750, 400, 2.25e-42, 8.7, "S6B")
print("""	\\hline
	2471 ($\iota = 103\\angulardegree$)""" + column_detail)
make_printable_limits(150, 400, 5.03563546991e-43, 8.7, "S6C")
make_printable_limits(750, 400, 5.52317264129e-42, 8.7, "S6C")
print("""	\\hline
	2475 ($\iota = 120\\angulardegree$)""" + column_detail)
make_printable_limits(150, 400, 8.43190929284e-44, 8.5, "S6C")
make_printable_limits(750, 400, 3.33620107607e-42, 8.5, "S6C")
print("50% CL")

print("""	\\hline
	2469 ($\iota = 120\\angulardegree$)""" + column_detail)
#make_printable_limits(150, 400, 4.22948505376e-44, 8.7, "S6B")
#make_printable_limits(750, 400, 8.43190929287e-43, 8.7, "S6B")
make_printable_limits(150, 400, 4.73039186739e-44, 8.7, "S6B")
make_printable_limits(750, 400, 1.06560223677e-42, 8.7, "S6B")
print("""	\\hline
	2471 ($\iota = 103\\angulardegree$)""" + column_detail)
make_printable_limits(150, 400, 2.35363649312e-43, 8.7, "S6C")
make_printable_limits(750, 400, 2.7704304425e-42, 8.7, "S6C")
print("""	\\hline
	2475 ($\iota = 120\\angulardegree$)""" + column_detail)
make_printable_limits(150, 400, 5.54102033e-44, 8.5, "S6C")
make_printable_limits(750, 400, 7.74263682681e-43, 8.5, "S6C")

print(calc_EGW_new(150, 400, 7.5e-45, 8.5))
print(((c_cgs**3*np.pi**(3/2))/(10*np.sqrt(2)*G_cgs))*7.5e-45*(8.5*kpc_cgs)**2*150**2*400)
print(c_cgs**3*np.pi**(3/2))
print(10*np.sqrt(2)*G_cgs)
print(7.5e-45*(8.5*kpc_cgs)**2*150**2*400)
print(kpc_cgs)

print(7.5e-45*150**2*400)

print("\nUpper limits based on background")

print("90% CL")
print("""	\\hline
	\multicolumn{8}{| c |}{SGR trigger 2471} \T \B \\\\
	\hline""")
make_printable_limits(150, 400, 3.55161600697e-44, 8.7, "S6C")
make_printable_limits(450, 400, 1.56911731872e-43, 8.7, "S6C")
make_printable_limits(750, 400, 2.15443469003e-43, 8.7, "S6C")
make_printable_limits(150, 150, 1e-42, 8.7, "S6C")
make_printable_limits(450, 150, 2.51984209979e-42, 8.7, "S6C")
make_printable_limits(750, 150, 3.42897593141e-42, 8.7, "S6C")
print("50% CL")

print("""	\hline
	\multicolumn{8}{| c |}{SGR trigger 2471} \T \B \\\\
	\hline""")
make_printable_limits(150, 400, 2.09131794525e-44, 8.7, "S6C")
make_printable_limits(450, 400, 1.10134889618e-43, 8.7, "S6C")
make_printable_limits(750, 400, 1.36718891834e-43, 8.7, "S6C")
make_printable_limits(150, 150, 3.67606766238e-43, 8.7, "S6C")
make_printable_limits(450, 150, 1e-42, 8.7, "S6C")
make_printable_limits(750, 150, 1.72578961327e-42, 8.7, "S6C")


print("alternate polarizations")

print("90% CL")
print("""	\\hline
	2471 ($\iota = 103\\angulardegree$)""" + column_detail)
make_printable_limits(150, 400, 7.32217323526e-43, 8.7, "S6C")
make_printable_limits(750, 400, 8.46712113469e-42, 8.7, "S6C")
print("50% CL")

print("""	\\hline
	2471 ($\iota = 103\\angulardegree$)""" + column_detail)
make_printable_limits(150, 400, 7.32217323526e-43, 8.7, "S6C")
make_printable_limits(750, 400, 4.77059392848e-42, 8.7, "S6C")
