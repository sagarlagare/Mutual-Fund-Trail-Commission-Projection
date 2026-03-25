# Mutual Fund Projection App

# 📈 Mutual Fund AUM & Monthly Trail Commission Projection

A simple **Streamlit web app** to project **Mutual Fund AUM growth** and **monthly trail commission earnings** over multiple years.

This tool helps visualize how **SIPs, monthly SIP increases, annual lump-sum investments, market growth, and trail commissions** impact long-term portfolio growth and revenue.

Built from the project logic in your uploaded file :contentReference[oaicite:0]{index=0}

---

## 🚀 Features

- Project **AUM growth year by year**
- Add **monthly SIP contributions**
- Increase SIP amount every month
- Include **annual lump sum investments**
- Apply **monthly compounded market growth**
- Calculate **monthly trail commission**
- Deduct commission from AUM for realistic net projections
- View:
  - **Yearly projection table**
  - **AUM & commission trend chart**
  - **Detailed monthly breakdown**
- Download results as:
  - **Yearly CSV**
  - **Monthly CSV**

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Pandas**

---

## 📂 Project Structure

```bash
.
├── app.py
└── README.md

## 🚀 Deployment

1. Push this repo to GitHub.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) → "New App".
3. Connect your GitHub repo, select `mf_projection.py`, and deploy.

## 📦 Install Locally
```bash
pip install -r requirements.txt
streamlit run mf_projection.py
