"""Screening estimate only, based on x = K*sqrt(t), not a complete service-life model."""
import math

def estimate_lifetime(depth_mm, exposure_days, cover_mm, propagation_years=0):
    if depth_mm <= 0 or exposure_days <= 0 or cover_mm <= 0 or propagation_years < 0:
        raise ValueError("Chiều sâu, thời gian phơi nhiễm và lớp bảo vệ phải > 0; thời gian lan truyền phải >= 0.")
    k = depth_mm / math.sqrt(exposure_days / 365.25)
    initiation = (cover_mm / k) ** 2
    return {"k_mm_sqrt_year":k,"t_init_years":initiation,"t_total_years":initiation+propagation_years,"cover_mm":cover_mm}
