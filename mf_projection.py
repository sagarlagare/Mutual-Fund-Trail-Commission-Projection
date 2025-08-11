import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mutual Fund AUM & Trail Projection", layout="wide")

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

# Main projection calculation (returns numeric results + formatted display columns)
def aum_projection(current_aum, monthly_sip, monthly_new_sip,
                   annual_lump_sum, annual_growth_rate,
                   trail_commission_rate, years):
    annual_growth_rate /= 100.0
    trail_commission_rate /= 100.0

    rows = []
    # We'll keep working copies so we don't modify the inputs outside the function
    aum = float(current_aum)
    sip = float(monthly_sip)

    for year in range(1, int(years) + 1):
        # Monthly SIP additions (sip increases month-by-month)
        for month in range(1, 13):
            aum += sip
            sip += monthly_new_sip

        # Annual lump sum added at year end
        aum += annual_lump_sum

        # Apply annual market growth
        aum *= (1 + annual_growth_rate)

        # Commission calculation
        commission = aum * trail_commission_rate

        rows.append({
            "Year": year,
            "AUM_value": aum,                                  # numeric for plotting
            "Commission_value": commission,                    # numeric for plotting
            "SIP_month_EoY_value": sip,                        # numeric
            "AUM": format_in_lakh_crore(aum),                  # formatted for display
            "Trail Commission": format_in_lakh_crore(commission),
            "SIP/month EoY": format_in_lakh_crore(sip)
        })

    df = pd.DataFrame(rows)
    return df

# -------- Streamlit UI --------
st.title("📈 Mutual Fund AUM & Trail Commission Projection")

with st.sidebar:
    st.header("Inputs")
    current_aum = st.number_input("Current AUM (₹)", min_value=0.0, value=500000.0, step=10000.0, format="%.2f")
    monthly_sip = st.number_input("Current Monthly SIP (₹)", min_value=0.0, value=10000.0, step=500.0, format="%.2f")
    monthly_new_sip = st.number_input("Increase in SIP per Month (₹)", min_value=0.0, value=500.0, step=100.0, format="%.2f")
    annual_lump_sum = st.number_input("Annual Lump Sum Investment (₹)", min_value=0.0, value=100000.0, step=10000.0, format="%.2f")
    annual_growth_rate = st.number_input("Expected Annual Market Growth Rate (%)", min_value=0.0, value=12.0, step=0.1, format="%.2f")
    trail_commission_rate = st.number_input("Trail Commission Rate (%)", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    years = st.number_input("Number of Years for Projection", min_value=1, value=10, step=1)

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("Calculate Projection"):
        df = aum_projection(
            current_aum,
            monthly_sip,
            monthly_new_sip,
            annual_lump_sum,
            annual_growth_rate,
            trail_commission_rate,
            years
        )

        st.subheader("Projection Table (formatted)")
        display_df = df[["Year", "AUM", "Trail Commission", "SIP/month EoY"]]
        st.dataframe(display_df, use_container_width=True)

        st.subheader("AUM and Commission Trend")
        # Prepare numeric series for chart
        chart_df = df[["Year", "AUM_value", "Commission_value"]].set_index("Year")
        st.line_chart(chart_df)

        # Download CSV (include numeric values too)
        download_df = df.rename(columns={
            "AUM_value": "AUM_numeric",
            "Commission_value": "Commission_numeric",
            "SIP_month_EoY_value": "SIP_month_EoY_numeric"
        })
        csv = download_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download results as CSV", csv, "aum_projection.csv", "text/csv")

with col2:
    st.markdown("### Quick notes")
    st.markdown("""
- SIP is increased by `Increase in SIP per Month` **every month** (compounded monthly SIP growth).
- `Annual Lump Sum` is added once **at the end of each year** before applying the yearly market growth.
- `Trail Commission` is calculated on the **year-end AUM after growth and lump sum**.
- Chart uses numeric values (not the formatted L/Cr strings).
    """)
    st.markdown("### Example values")
    st.write({
        "Current AUM": 500000,
        "Monthly SIP": 10000,
        "Increase per month": 500,
        "Annual lump sum": 100000,
        "Annual growth %": 12,
        "Trail commission %": 1
    })

# Show footer
st.write("---")
st.write("If you want additional features (detailed monthly schedule, separate plots for SIP additions, or an export to Excel), tell me and I will add them.")
