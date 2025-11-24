import requests
import pandas as pd

# PATIENT DEMOGRAPHICS from the web. Includes key demographics about patients such as their age, sex, height and weight.
demographics_url = (
    "https://ruby.ils.unc.edu/~ahhardin/chip690_335_2025_fall/patient_demographics.csv"
)

dem_df = pd.read_csv(demographics_url, dtype=str)
dem_df["age"] = pd.to_numeric(dem_df["age"], errors="coerce")
dem_df["height_inches"] = pd.to_numeric(dem_df["height_inches"], errors="coerce")
dem_df["weight_lbs"] = pd.to_numeric(dem_df["weight_lbs"], errors="coerce")

# COMPREHENSIVE METABOLIC PANEL (CMP) from the web, a lab test that measures a number of substances in the blood used to assess overall health and metabolism.
cmp_data_url = "https://ruby.ils.unc.edu/~ahhardin/chip690_335_2025_fall/cmp.json"

# all creatinine rows for all patients as a dataframe
cmp_data = requests.get(cmp_data_url).json()
rows = []
for patient_id, measurements in cmp_data.items():
    for m in measurements:
        m["patient_id"] = patient_id
        rows.append(m)
df = pd.DataFrame(rows)
creatinine_df = df[df["measure"] == "Creatinine"].copy()


# patient creatine with results
def get_creatinine(patient_id):
    entries = cmp_data.get(str(patient_id), [])
    for m in entries:
        if m.get("measure") == "Creatinine":
            variable = m.get("patient_measure")
            try:
                return float(variable)
            except Exception:
                return None
    return None


# calculate Estimated Glomerular Filtration Rate (eGFR)
def eGFR_result(scr, sex, age):
    try:
        scr = float(scr)
        age = int(age)
    except Exception:
        return None
    c = 142
    if sex == "M":
        k = 0.9
        a = -0.302
        multiplier = 1
    elif sex == "F":
        k = 0.7
        a = -0.241
        multiplier = 1.012
    else:
        return None
    low = min(scr / k, 1)
    high = max(scr / k, 1)
    return c * (low**a) * (high**-1.200) * (0.9938**age) * multiplier


# calculation = eGFR_result(scr, sex, age)


# check against a THRESHOLD to identify patients who may be experiencing CKD
def eGFR_below_65(value):
    if value <= 65:
        return True
    else:
        return False


# calculate BMI
def bmi_result(weight_lbs, height_inches):
    try:
        weight_lbs = float(weight_lbs)
        height_inches = float(height_inches)
        if height_inches <= 0:
            return None
        return (weight_lbs * 703) / (height_inches * height_inches)
    except (ValueError, ZeroDivisionError, TypeError):
        return None


# Converting your final output to a Pandas DataFrame.

output_rows = []
for x, row in dem_df.iterrows():
    patient_id = row["patient_id"]
    age = row["age"]
    height = row["height_inches"]
    weight = row["weight_lbs"]
    sex = row["sex"]
    scr = get_creatinine(patient_id)
    eGFR = eGFR_result(scr, sex, age)
    bmi = bmi_result(weight, height)
    output_rows.append(
        {
            "Patient Age": age,
            "Patient Height": height,
            "Patient Weight": weight,
            "Patient BMI": bmi,
            "Patient Sex": sex,
            "Patient eGFR": eGFR,
        }
    )

output_df = pd.DataFrame(output_rows)
output_df.to_csv("results.csv", index=False)

print("Results saved to results.csv with requested columns only.")
# Print only results with only the requested columns to results.csv
# requested_cols = [
#     "Patient Age",
#     "Patient Height",
#     "Patient Weight",
#     "Patient BMI",
#     "Patient Sex",
#     "Patient eGFR",
# ]
# # df[requested_cols].to_csv("results.csv", index=False)
# print("Results saved to results.csv with requested columns only.")
