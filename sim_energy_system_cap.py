# sim_energy_system_cap.py - Simulation of a capacitor-based energy storage system
#
# python3 sim_energy_system_cap.py sa_m2 eff voc c_f r_esr q0_c p_on_w v_thresh drun_time_track dur_s
# This script models energy storage and consumption for a solar-powered system.
#
# Input Details:
#  sa_m2: Area of the solar panel (m²)
#  eff: Efficiency of the solar cells (%)
#  voc: Open-circuit voltage of the solar array (V)
#  c_f: Capacitance of the energy storage unit (F)
#  r_esr: Internal resistance of the capacitor (Ω)
#  q0_c: Initial electric charge in the capacitor (C)
#  p_on_w: Power consumption when the system is active (W)
#  v_thresh: Minimum voltage required for power-on (V)
#  drun_time_track: Simulation time step (s)
#  dur_s: Total simulation duration (s)
#
# Result:
# Outputs the simulation data (time, voltage data) to a CSV file.
#
# Author: Vineet Keshavamurthy
# Contributors: None
# License: See LICENSE file for terms.

# Load necessary modules
import math  
import csv   
import sys  
# Fixed solar irradiance parameter in W/m^2
irrad = 1336.1  # Incoming solar radiation intensity (W/m²)

# Initialize all system parameters as placeholders
sa_m2 = float('nan')
eff = float('nan')
voc = float('nan')
c_f = float('nan')
r_esr = float('nan')
q0_c = float('nan')
p_on_w = float('nan')
v_thresh = float('nan')
drun_time_track = float('nan')
dur_s = float('nan')

# Check and parse command-line arguments
if len(sys.argv) == 11:
    sa_m2 = float(sys.argv[1])
    eff = float(sys.argv[2])
    voc = float(sys.argv[3])
    c_f = float(sys.argv[4])
    r_esr = float(sys.argv[5])
    q0_c = float(sys.argv[6])
    p_on_w = float(sys.argv[7])
    v_thresh = float(sys.argv[8])
    drun_time_track = float(sys.argv[9])
    dur_s = float(sys.argv[10])
else:
    print("Incorrect amount of arguments passed through. Recheck command line to ensure the command was entered properly.")
    exit()

# Calculation of solar current ########################
power_generated = irrad * sa_m2
effective_power = power_generated * eff
short_circ_current = effective_power / voc
i_resultant_a = short_circ_current
q_resultant = q0_c
p_consumption = p_on_w
run_time_track = 0.0

# Discriminant calculation ########################
expr1 = q_resultant / c_f + i_resultant_a * r_esr
discriminant_value = expr1**2 - 4 * p_consumption * r_esr

# Handle invalid discriminant scenario
if discriminant_value < 0.0:
    p_consumption = 0.0
    expr1 = q_resultant/c_f + i_resultant_a * r_esr
    discriminant_value=expr1**2 - p_consumption * r_esr*4

# Calculate initial voltage ########################
expr2 = q_resultant / c_f + i_resultant_a * r_esr
capacit_term_volt = (expr2 + math.sqrt(discriminant_value)) / 2
log = [[run_time_track, capacit_term_volt]]

# Apply system constraints
if voc <= capacit_term_volt and i_resultant_a != 0.0:
    i_resultant_a = 0.0

if capacit_term_volt < v_thresh:
    p_consumption = 0.0

# Run the simulation loop ########################
while log[-1][0] < dur_s:
    # Load power and adjust charge
    i3_a = p_consumption / capacit_term_volt
    q_resultant += (i_resultant_a - i3_a) * drun_time_track
    q_resultant = max(q_resultant, 0.0)

    # Determine solar array behavior
    i_resultant_a = short_circ_current if 0 <= capacit_term_volt < voc else 0.0

    # Re-enable power mode if voltage is sufficient
    if p_consumption == 0.0 and capacit_term_volt >= voc:
        p_consumption = p_on_w

    # Recalculate node voltage 
    expr1 = q_resultant / c_f + i_resultant_a * r_esr
    discriminant_value = expr1**2 - 4 * p_consumption * r_esr
    if discriminant_value < 0.0:
        p_consumption = 0.0
        expr1 = q_resultant / c_f + i_resultant_a * r_esr
        discriminant_value = expr1**2 - 4 * p_consumption * r_esr

    expr2 = q_resultant / c_f + i_resultant_a * r_esr
    capacit_term_volt = (expr2 + math.sqrt(discriminant_value)) / 2

    # Apply power limitations using conditional check
    if voc <= capacit_term_volt and i_resultant_a != 0.0:
        i_resultant_a = 0.0

    if capacit_term_volt < v_thresh:
        p_consumption = 0.0

    # Store simulation state
    log.append([run_time_track, capacit_term_volt])
    run_time_track += drun_time_track

# Write results to CSV file ########################
with open('./log.csv', mode='w', newline='') as outfile:
    csvwriter = csv.writer(outfile)
    csvwriter.writerow(['Time (s)', 'Voltage (V)'])
    for entry in log:
        csvwriter.writerow(entry)