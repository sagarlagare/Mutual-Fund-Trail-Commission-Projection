import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mutual Fund AUM & Trail Projection (Monthly Trail)", layout="wide")

# Helper function to format values in Lakh/Crore style
def format_in_lakh_crore(value):
    try:
        value = float(value)
    except Exception:
        return str(value)
    if value >= 1e7:
        return f"{value / 1e7:.2f} Cr"
    elif value >= 1e5:
        return f"{value / 1e5:.2f} L"
    else:
        return f"{value:,.2f}"

# Main projection calculation with monthly compounding and monthly trail commission
def aum_projection(current_aum, monthly_sip, monthly_new_sip,
                   annual_lump_sum, annual_growth_rate,
                   trail_commission_rate, years):
    """
    Returns a DataFrame with yearly aggregates.
    - Monthly growth uses monthly compounding: (1+annual)^(1/12)-1
    - Monthly commission = month_end_aum * (trail_rate / 12)
    - Commission is deducted from AUM (net AUM)
    - Annual lump-sum added at end of Dec BEFORE that month's growth
    """
    annual_growth_rate /= 100.0
    trail_commission_rate /= 100.0

    # Convert to monthly equivalents
    monthly_growth_rate = (1 + annual_growth_rate) ** (1 / 12.0) - 1.0
    monthly_trail_rate = trail_commission_rate / 12.0

    rows = []
    aum = float(current_aum)  # net AUM that evolves month-by-month
    sip = float(monthly_sip)

    # Optional detailed monthly rows (if user wants monthly breakdown later)
    monthly_rows = []

    for year in range(1, int(years) + 1):
        total_commission_year = 0.0

        for month in range(1, 13):
            # 1) Add this month's SIP contribution (use current sip for this month)
            aum += sip

            # record monthly pre-growth AUM if needed
            pre_growth_aum = aum

            # 2) If December, add annual lump sum BEFORE applying that month's growth
            if month == 12 and annual_lump_sum:
                aum += annual_lump_sum

            # 3) Apply monthly market growth (monthly compounding)
            aum *= (1 + monthly_growth_rate)

            # 4) Compute monthly commission on month-end AUM (after growth)
            commission_month = aum * monthly_trail_rate

            # 5) Deduct commission from AUM (commissions paid out reduce AUM)
            aum -= commission_month

            total_commission_year += commission_month

            # 6) Increase SIP for next month
            sip += monthly_new_sip

            # Save monthly row (optional for a monthly table)
            monthly_rows.append({
                "Year": year,
                "Month": month,
                "Pre_Growth_AUM": pre_growth_aum,
                "AUM_after_growth_before_commission": aum + commission_month,  # useful reference
                "Commission_month": commission_month,
                "AUM_after_commission": aum,
                "SIP_used_this_month": (sip - monthly_new_sip)  # the SIP that was used this month
            })

        # End of year aggregates
        rows.append({
            "Year": year,
            "AUM_value": aum,                                  # numeric (net AUM at year end)
            "Commission_value": total_commission_year,         # numeric (sum of 12 monthly commissions)
            "SIP_month_EoY_value": sip,                        # numeric (SIP for next month)
            "AUM": format_in_lakh_crore(aum),                  # formatted for display
            "Trail Commission": format_in_lakh_crore(total_commission_year),
            "SIP/month EoY": format_in_lakh_crore(sip)
        })

    df = pd.DataFrame(rows)
    monthly_df = pd.DataFrame(monthly_rows)
    return df, monthly_df

# -------- Streamlit UI --------
st.title("📈 Mutual Fund AUM & Monthly Trail Commission Projection")

with st.sidebar:
    st.header("Inputs")
    current_aum = st.number_input("Current AUM (₹)", min_value=0.0, value=500000.0, step=10000.0, format="%.2f")
    monthly_sip = st.number_input("Current Monthly SIP (₹)", min_value=0.0, value=10000.0, step=500.0, format="%.2f")
    monthly_new_sip = st.number_input("Increase in SIP per Month (₹)", min_value=0.0, value=500.0, step=100.0, format="%.2f")
    annual_lump_sum = st.number_input("Annual Lump Sum Investment (₹)", min_value=0.0, value=100000.0, step=10000.0, format="%.2f")
    annual_growth_rate = st.number_input("Expected Annual Market Growth Rate (%)", min_value=0.0, value=12.0, step=0.1, format="%.2f")
    trail_commission_rate = st.number_input("Trail Commission Rate (%) (annual)", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    years = st.number_input("Number of Years for Projection", min_value=1, value=10, step=1)

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("Calculate Projection"):
        df, monthly_df = aum_projection(
            current_aum,
            monthly_sip,
            monthly_new_sip,
            annual_lump_sum,
            annual_growth_rate,
            trail_commission_rate,
            years
        )

        st.subheader("Projection Table (formatted, yearly aggregates)")
        display_df = df[["Year", "AUM", "Trail Commission", "SIP/month EoY"]]
        st.dataframe(display_df, use_container_width=True)

        st.subheader("AUM and Commission Trend (year-end)")
        chart_df = df[["Year", "AUM_value", "Commission_value"]].set_index("Year")
        st.line_chart(chart_df)

        # Option: show monthly breakdown if desired
        if st.checkbox("Show monthly breakdown (detailed)"):
            # format monthly dataframe for display (some columns formatted)
            monthly_display = monthly_df.copy()
            monthly_display["AUM_after_commission_fmt"] = monthly_display["AUM_after_commission"].apply(format_in_lakh_crore)
            monthly_display["Commission_month_fmt"] = monthly_display["Commission_month"].apply(format_in_lakh_crore)
            monthly_display["SIP_used_this_month_fmt"] = monthly_display["SIP_used_this_month"].apply(format_in_lakh_crore)
            st.write("Monthly breakdown (first 200 rows shown):")
            st.dataframe(monthly_display.head(200), use_container_width=True)

        # Download CSV (include numeric values too)
        download_df = df.rename(columns={
            "AUM_value": "AUM_numeric",
            "Commission_value": "Commission_numeric",
            "SIP_month_EoY_value": "SIP_month_EoY_numeric"
        })
        csv = download_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download yearly results as CSV", csv, "aum_projection_yearly.csv", "text/csv")

        # Monthly CSV as separate download
        csv_monthly = monthly_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download monthly breakdown (CSV)", csv_monthly, "aum_projection_monthly.csv", "text/csv")

with col2:
    st.markdown("### Quick notes")
    st.markdown("""
- SIP is **added each month**; `Increase in SIP per Month` is applied **after** the month's SIP (so next month's SIP increases).
- Annual lump sum is added at the **end of December** (before that month's growth).
- Market growth is applied **monthly** using monthly compounding derived from the annual growth rate.
- Trail commission is computed **every month** as `(month_end_aum_after_growth) * (annual_trail_rate / 12)` and deducted from AUM.
- Yearly Trail Commission is the **sum of the 12 monthly commissions**.
    """)
    st.markdown("### Example values")
    st.write({
        "Current AUM": 500000,
        "Monthly SIP": 10000,
        "Increase per month": 500,
        "Annual lump sum": 100000,
        "Annual growth %": 12,
        "Trail commission % (annual)": 1
    })

st.write("---")
st.write("If you want a version where commissions are NOT deducted from AUM (i.e., commission tracked only as separate revenue), or if you want an Excel export with formatted columns, tell me and I'll adapt the code.")
