"""Measurement tag definitions and Modbus read blocks.

The offsets below reproduce the register map used in the user's current test.
Current THD uses references 400049, 400051 and 400053.
The two tariff-energy values still require validation against the meter display.
"""

# (tag_name, SCADA_reference, engineering_unit)
TAGS = [
    ("Voltage_L_N_L1", 400001, "V"),
    ("Voltage_L_N_L2", 400003, "V"),
    ("Voltage_L_N_L3", 400005, "V"),
    ("Voltage_L_L_L12", 400007, "V"),
    ("Voltage_L_L_L23", 400009, "V"),
    ("Voltage_L_L_L31", 400011, "V"),
    ("Current_L1", 400013, "A"),
    ("Current_L2", 400015, "A"),
    ("Current_L3", 400017, "A"),
    ("Apparent_Power_L1", 400019, "VA"),
    ("Apparent_Power_L2", 400021, "VA"),
    ("Apparent_Power_L3", 400023, "VA"),
    ("Active_Power_L1", 400025, "W"),
    ("Active_Power_L2", 400027, "W"),
    ("Active_Power_L3", 400029, "W"),
    ("Reactive_Power_L1", 400031, "var"),
    ("Reactive_Power_L2", 400033, "var"),
    ("Reactive_Power_L3", 400035, "var"),
    ("Power_Factor_L1", 400037, ""),
    ("Power_Factor_L2", 400039, ""),
    ("Power_Factor_L3", 400041, ""),
    ("Voltage_THD_L1", 400043, "%"),
    ("Voltage_THD_L2", 400045, "%"),
    ("Voltage_THD_L3", 400047, "%"),
    ("Current_THD_L1", 400049, "%"),
    ("Current_THD_L2", 400051, "%"),
    ("Current_THD_L3", 400053, "%"),
    ("Frequency", 400055, "Hz"),
    ("Voltage_L_N_Avg", 400057, "V"),
    ("Voltage_L_L_Avg", 400059, "V"),
    ("Current_Avg", 400061, "A"),
    ("Apparent_Power_Avg", 400063, "VA"),
    ("Active_Power_Avg", 400065, "W"),
    ("Reactive_Power_Avg", 400067, "var"),
    ("Power_Factor_Avg", 400069, ""),
    ("Tariff_1_Import_kWh", 402801, "kWh"),
    ("Tariff_1_Import_kVARh", 402809, "kVARh"),
]

# Each tuple is (starting protocol offset, number of 16-bit registers).
# These are the three blocks used in the successful 37-tag communication test.
REGISTER_BLOCKS = [
    (1, 70),
    (2801, 2),
    (2809, 2),
]

UNVERIFIED_TAGS = {
    "Tariff_1_Import_kWh",
    "Tariff_1_Import_kVARh",
}
