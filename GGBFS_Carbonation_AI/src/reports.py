from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

def excel_report(inputs, prediction, lifetime, curve):
    b=BytesIO()
    with pd.ExcelWriter(b,engine="openpyxl") as w:
        pd.DataFrame([inputs]).to_excel(w,index=False,sheet_name="Inputs")
        pd.DataFrame([{"Predicted_depth_mm":prediction,**lifetime}]).to_excel(w,index=False,sheet_name="Prediction")
        curve.to_excel(w,index=False,sheet_name="Time_curve")
        pd.DataFrame([{"Data_status":"SYNTHETIC DEMO unless trained on verified experimental data","Caution":"Not for design or structural safety decisions"}]).to_excel(w,index=False,sheet_name="Limitations")
    return b.getvalue()

def pdf_report(inputs, prediction, lifetime, curve, data_status):
    b=BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=16*mm); s=getSampleStyleSheet()
    story=[Paragraph("BÁO CÁO CACBONAT HÓA BÊ TÔNG GGBFS",s["Title"]),Spacer(1,4*mm),Paragraph("Trạng thái dữ liệu: "+data_status,s["BodyText"]),Spacer(1,4*mm),Paragraph("Thông số đầu vào",s["Heading2"])]
    t=Table([["Thông số","Giá trị"]]+[[str(k),str(v)] for k,v in inputs.items()],colWidths=[75*mm,85*mm],repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#16324F")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.4,colors.grey),("FONTSIZE",(0,0),(-1,-1),8)])); story += [t,Spacer(1,4*mm),Paragraph("Kết quả",s["Heading2"])]
    rt=Table([["Chỉ tiêu","Giá trị"],["Chiều sâu dự đoán (mm)",f"{prediction:.3f}"],["K (mm/√năm)",f"{lifetime['k_mm_sqrt_year']:.3f}"],["Thời điểm chạm lớp bảo vệ (năm)",f"{lifetime['t_init_years']:.2f}"],["Tổng thời gian gồm lan truyền (năm)",f"{lifetime['t_total_years']:.2f}"]],colWidths=[100*mm,60*mm])
    rt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#16324F")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.4,colors.grey),("FONTSIZE",(0,0),(-1,-1),8)])); story += [rt,Spacer(1,4*mm),Paragraph("Đường cong theo thời gian",s["Heading2"])]
    fig,ax=plt.subplots(figsize=(6.2,2.8)); ax.plot(curve.Years,curve.Predicted_depth_mm,marker="o"); ax.axhline(lifetime["cover_mm"],linestyle="--",label="Lớp bảo vệ"); ax.set_xlabel("Năm"); ax.set_ylabel("Chiều sâu (mm)"); ax.grid(True,alpha=.3); ax.legend(); im=BytesIO(); fig.tight_layout(); fig.savefig(im,format="png",dpi=140); plt.close(fig); im.seek(0)
    story += [Image(im,width=155*mm,height=70*mm),Spacer(1,3*mm),Paragraph("Giới hạn: dùng quan hệ đơn giản x=K√t, giả định điều kiện không đổi. Không mô hình hóa đầy đủ ăn mòn, nứt, tải trọng hay xác suất hư hỏng. Không dùng làm căn cứ thiết kế/an toàn.",s["BodyText"])]
    doc.build(story); return b.getvalue()
