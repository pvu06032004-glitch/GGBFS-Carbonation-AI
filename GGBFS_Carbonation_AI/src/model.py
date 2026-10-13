"""ML pipeline for carbonation-depth research/demo. Synthetic data is not experimental evidence."""
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

NUMERIC = ["W_B", "Cement_kg_m3", "GGBFS_pct", "FA_pct", "SF_pct", "fc_28_MPa", "Curing_days", "CO2_pct", "RH_pct", "Temperature_C", "Exposure_days"]
CATEGORICAL = ["Curing_type", "Exposure_condition", "CO2_type"]
FEATURES = NUMERIC + CATEGORICAL
TARGET = "Carbonation_depth_mm"
DEFAULTS = {"W_B": .45, "Cement_kg_m3": 320, "GGBFS_pct": 40, "FA_pct": 0, "SF_pct": 0, "fc_28_MPa": 40, "Curing_days": 7, "Curing_type": "Water", "CO2_pct": .04, "RH_pct": 65, "Temperature_C": 25, "Exposure_days": 3652.5, "Exposure_condition": "Natural", "CO2_type": "Natural"}

def generate_synthetic_dataset(n=1500, seed=42):
    """Generate synthetic demo rows. Never describe these as laboratory measurements."""
    rng = np.random.default_rng(seed)
    wb = rng.uniform(.30, .65, n); cement = rng.uniform(180, 450, n)
    slag = rng.uniform(0, 70, n); fa = rng.uniform(0, 30, n); sf = rng.choice([0, 0, 0, 2, 4, 6, 8, 10], n)
    fc = np.clip(82 - 72*wb + .035*cement - .10*slag + .18*sf + rng.normal(0, 4, n), 15, 80)
    cure_days = rng.choice([3, 7, 14, 28, 56], n); cure_type = rng.choice(["Water", "Sealed", "Air"], n, p=[.55, .25, .20])
    co2 = rng.uniform(.03, 5, n); rh = rng.uniform(40, 95, n); temp = rng.uniform(10, 40, n)
    exposure = np.exp(rng.uniform(np.log(8), np.log(34000), n)); condition = np.where(co2 > .5, "Accelerated", "Natural")
    moisture = np.maximum(.18, 1 - ((rh - 62)/48)**2)
    binder = np.clip(1 + .005*(slag - 25) + .003*fa - .025*sf, .45, 1.6)
    curing = np.where(cure_type == "Water", .84, np.where(cure_type == "Sealed", .94, 1.12))
    co2factor = np.sqrt(np.maximum(co2, .01)/.04)
    k = (2 + 9*np.maximum(wb - .25, 0) + 16/np.sqrt(np.maximum(fc, 10))) * moisture * binder * curing * co2factor
    depth = np.clip(k*np.sqrt(exposure/365) + rng.normal(0, 1.5, n), .1, 100)
    return pd.DataFrame({"W_B":wb,"Cement_kg_m3":cement,"GGBFS_pct":slag,"FA_pct":fa,"SF_pct":sf,"fc_28_MPa":fc,"Curing_days":cure_days,"Curing_type":cure_type,"CO2_pct":co2,"RH_pct":rh,"Temperature_C":temp,"Exposure_days":exposure,"Exposure_condition":condition,"CO2_type":condition,TARGET:depth,"Data_source":"SYNTHETIC_DEMO"})

def validate_dataset(df):
    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing: raise ValueError("Thiếu cột bắt buộc: " + ", ".join(missing))
    if len(df) < 20: raise ValueError("Cần ít nhất 20 hàng dữ liệu.")
    out = df.copy()
    for c in NUMERIC + [TARGET]: out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=[TARGET])
    if len(out) < 20: raise ValueError("Còn dưới 20 hàng có nhãn hợp lệ.")
    if (out[TARGET] < 0).any(): raise ValueError("Chiều sâu không được âm.")
    return out

def train_and_evaluate(df):
    df = validate_dataset(df); X = df[FEATURES]; y = df[TARGET].astype(float)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42)
    pre = ColumnTransformer([("num", SimpleImputer(strategy="median"), NUMERIC), ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL)])
    model = Pipeline([("pre", pre), ("model", ExtraTreesRegressor(n_estimators=220, min_samples_leaf=2, random_state=42, n_jobs=-1))])
    model.fit(Xtr, ytr); pred = np.maximum(0, model.predict(Xte))
    metrics = {"R2":float(r2_score(yte,pred)),"MAE_mm":float(mean_absolute_error(yte,pred)),"RMSE_mm":float(np.sqrt(mean_squared_error(yte,pred))),"n_train":len(Xtr),"n_test":len(Xte)}
    model.fit(X, y)
    source = "SYNTHETIC_DEMO" if "Data_source" in df and df["Data_source"].astype(str).str.contains("SYNTHETIC",case=False).all() else "USER_DATA_CHECK_REQUIRED"
    return {"pipeline":model,"metrics":metrics,"data_source":source,"n_rows":len(df)}

def predict_depth(bundle, inputs):
    x = pd.DataFrame([inputs]) if isinstance(inputs, dict) else inputs.copy()
    missing = [c for c in FEATURES if c not in x.columns]
    if missing: raise ValueError("Thiếu biến đầu vào: " + ", ".join(missing))
    return np.maximum(0, bundle["pipeline"].predict(x[FEATURES]))
