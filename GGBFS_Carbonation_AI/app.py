from pathlib import Path
import sys
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT))
from src.model import DEFAULTS, FEATURES, TARGET, generate_synthetic_dataset, train_and_evaluate, predict_depth
from src.lifetime import estimate_lifetime
from src.reports import excel_report, pdf_report
st.set_page_config(page_title="Phần mềm dự đoán tuổi thọ công trình BTCT trên cơ sở độ bền chống Carbonate hóa của Bê tông sử dụng xỉ lò cao",page_icon="🧱",layout="wide")
st.title("🧱 Phần mềm dự đoán tuổi thọ công trình BTCT trên cơ sở độ bền chống Carbonate hóa của Bê tông sử dụng xỉ lò cao")
st.caption("Công cụ nghiên cứu minh họa; không thay thế thiết kế hoặc đánh giá an toàn kết cấu.")
with st.sidebar:
    st.header("Nguồn dữ liệu")
    mode=st.radio("Chọn dữ liệu",["Dữ liệu mô phỏng (demo)","Tải CSV thực nghiệm"])
    uploaded=st.file_uploader("Tải CSV",type=["csv"]) if mode=="Tải CSV thực nghiệm" else None
    st.warning("Dữ liệu mô phỏng chỉ để kiểm thử phần mềm, không phải kết quả thí nghiệm.")
@st.cache_resource
def demo_bundle(): return train_and_evaluate(generate_synthetic_dataset(1500))
try:
    if mode=="Tải CSV thực nghiệm" and uploaded is not None: bundle=train_and_evaluate(pd.read_csv(uploaded))
    else: bundle=demo_bundle()
except Exception as e:
    st.error(f"Không thể huấn luyện: {e}"); st.stop()
if bundle["data_source"]=="SYNTHETIC_DEMO": st.error("ĐANG DÙNG DỮ LIỆU MÔ PHỎNG. Kết quả và chỉ số không đại diện độ chính xác trên bê tông thật.")
else: st.warning("Dữ liệu tải lên chưa được xác minh độc lập. Hãy kiểm tra nguồn, đơn vị và cách chia tập kiểm định.")
t1,t2,t3,t4=st.tabs(["Dự đoán","So sánh kịch bản","Đánh giá mô hình","Dữ liệu CSV"])
with t1:
    st.subheader("Thông số đầu vào")
    with st.form("predict"):
        a,b,c=st.columns(3)
        with a:
            wb=st.number_input("W/B",.2,.9,.45,.01); cement=st.number_input("Xi măng (kg/m³)",100.,600.,320.,5.); slag=st.slider("Xỉ lò cao (%)",0,70,40); fa=st.slider("Tro bay FA (%)",0,50,0); sf=st.slider("Silica fume SF (%)",0,15,0)
        with b:
            fc=st.number_input("Cường độ nén 28 ngày (MPa)",10.,100.,40.); curing_days=st.selectbox("Dưỡng hộ (ngày)",[3,7,14,28,56],index=1); curing=st.selectbox("Loại dưỡng hộ",["Water","Sealed","Air"]); rh=st.slider("RH (%)",30,100,65); temp=st.slider("Nhiệt độ (°C)",0,60,25)
        with c:
            co2=st.number_input("CO₂ (%)",.01,20.,.04,.01,format="%.3f"); years=st.number_input("Phơi nhiễm (năm)",.02,100.,10.,.5); condition=st.selectbox("Điều kiện",["Natural","Accelerated"]); co2type=st.selectbox("Loại CO₂",["Natural","Accelerated"]); cover=st.number_input("Lớp bảo vệ (mm)",10.,100.,30.); propagation=st.number_input("Thời gian lan truyền giả định (năm)",0.,100.,0.)
        submit=st.form_submit_button("Dự đoán",type="primary",use_container_width=True)
    if submit:
        inputs={"W_B":wb,"Cement_kg_m3":cement,"GGBFS_pct":slag,"FA_pct":fa,"SF_pct":sf,"fc_28_MPa":fc,"Curing_days":curing_days,"Curing_type":curing,"CO2_pct":co2,"RH_pct":rh,"Temperature_C":temp,"Exposure_days":years*365.25,"Exposure_condition":condition,"CO2_type":co2type}
        try:
            pred=float(predict_depth(bundle,inputs)[0]); life=estimate_lifetime(max(pred,.001),inputs["Exposure_days"],cover,propagation); st.session_state["result"]={"inputs":inputs,"pred":pred,"life":life,"cover":cover,"years":years}
        except Exception as e: st.error(str(e))
    if "result" in st.session_state:
        r=st.session_state["result"]; pred=r["pred"]; life=r["life"]
        x,y,z=st.columns(3); x.metric("Chiều sâu dự đoán",f"{pred:.2f} mm"); y.metric("Thời điểm chạm lớp bảo vệ (ước tính)",f"{life['t_init_years']:.1f} năm"); z.metric("Tổng gồm lan truyền giả định",f"{life['t_total_years']:.1f} năm")
        if r["inputs"]["CO2_pct"]>.1 or r["inputs"]["CO2_type"]=="Accelerated": st.warning("Không ngoại suy thử gia tốc sang môi trường tự nhiên nếu chưa hiệu chuẩn.")
        curve=pd.DataFrame({"Years":np.linspace(0,max(1,r["years"]*1.5),30)}); curve["Predicted_depth_mm"]=life["k_mm_sqrt_year"]*np.sqrt(curve["Years"])
        fig,ax=plt.subplots(figsize=(9,4)); ax.plot(curve.Years,curve.Predicted_depth_mm,label="x = K√t"); ax.axhline(r["cover"],linestyle="--",label="Lớp bảo vệ"); ax.set_xlabel("Năm"); ax.set_ylabel("Chiều sâu (mm)"); ax.grid(alpha=.25); ax.legend(); st.pyplot(fig); plt.close(fig)
        status="DỮ LIỆU MÔ PHỎNG — minh họa" if bundle["data_source"]=="SYNTHETIC_DEMO" else "Dữ liệu người dùng tải lên — chưa xác minh độc lập"
        st.download_button("Tải Excel",excel_report(r["inputs"],pred,life,curve),"bao_cao_xi_lo_cao.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.download_button("Tải PDF",pdf_report(r["inputs"],pred,life,curve,status),"bao_cao_xi_lo_cao.pdf","application/pdf")
with t2:
    st.subheader("So sánh tỷ lệ xỉ lò cao")
    w=st.slider("W/B",.25,.70,.45,.01,key="swb"); rh2=st.slider("RH (%)",40,95,65,key="srh"); co22=st.number_input("CO₂ (%)",.01,5.,.04,.01,key="sco2"); cover2=st.slider("Lớp bảo vệ (mm)",15,70,30,key="scov")
    rows=[]
    for slag2 in [0,20,40,60,70]:
        inp={**DEFAULTS,"W_B":w,"GGBFS_pct":slag2,"RH_pct":rh2,"CO2_pct":co22,"Exposure_days":10*365.25}
        d=float(predict_depth(bundle,inp)[0]); l=estimate_lifetime(max(d,.001),inp["Exposure_days"],cover2)
        rows.append({"Xỉ lò cao (%)":slag2,"Chiều sâu sau 10 năm (mm)":d,"Thời điểm chạm lớp bảo vệ (năm)":l["t_init_years"]})
    df=pd.DataFrame(rows); st.dataframe(df,use_container_width=True,hide_index=True); fig,ax=plt.subplots(); ax.plot(df["Xỉ lò cao (%)"],df["Chiều sâu sau 10 năm (mm)"],marker="o"); ax.set_xlabel("Xỉ lò cao (%)"); ax.set_ylabel("Chiều sâu (mm)"); ax.grid(alpha=.3); st.pyplot(fig); plt.close(fig)
    st.caption("So sánh kịch bản của mô hình hiện tại; không chứng minh quan hệ nhân quả.")
with t3:
    m=bundle["metrics"]; a,b,c=st.columns(3); a.metric("R²",f"{m['R2']:.3f}"); b.metric("MAE (mm)",f"{m['MAE_mm']:.2f}"); c.metric("RMSE (mm)",f"{m['RMSE_mm']:.2f}"); st.write(f"Train: {m['n_train']} hàng; test: {m['n_test']} hàng.")
    if bundle["data_source"]=="SYNTHETIC_DEMO": st.error("Các chỉ số chỉ đánh giá trên dữ liệu tổng hợp, không phải hiệu năng thực tế.")
    st.markdown("Nghiên cứu chính thức cần kiểm định độc lập, kiểm tra rò rỉ dữ liệu và chia nhóm theo mẻ/nghiên cứu khi phù hợp.")
with t4:
    st.write("CSV phải có các cột sau:"); st.code(", ".join(FEATURES+[TARGET]))
    sample=generate_synthetic_dataset(10); st.dataframe(sample,use_container_width=True)
    st.download_button("Tải CSV mẫu (MÔ PHỎNG)",sample.to_csv(index=False).encode("utf-8-sig"),"sample_synthetic_data.csv","text/csv")
    st.markdown("`CO2_pct` dùng phần trăm, ví dụ 0.04 nghĩa là 0.04%. `Exposure_days` là ngày; `Carbonation_depth_mm` là chiều sâu đo mm. Dữ liệu thực nghiệm cần được kiểm tra nguồn, đơn vị, phương pháp đo và chất lượng trước khi dùng.")
