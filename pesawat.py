import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Realtime Flight Tracker", layout="wide")

st.title("✈️ Realtime Flight Tracker (OpenSky API)")
st.caption("Menampilkan data penerbangan realtime dari [OpenSky Network](https://opensky-network.org/api/states/all)")

# --- Fungsi untuk ambil data dari API ---
@st.cache_data(ttl=30)
def fetch_flights():
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url).json()

    columns = [
        "icao24", "callsign", "origin_country", "time_position", "last_contact",
        "longitude", "latitude", "baro_altitude", "on_ground", "velocity", "true_track",
        "vertical_rate", "sensors", "geo_altitude", "squawk", "spi", "position_source"
    ]

    if "states" not in response or not response["states"]:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(response["states"], columns=columns)
    df = df.dropna(subset=["longitude", "latitude"])  # hanya yang punya posisi
    return df

# --- Ambil data ---
with st.spinner("Mengambil data penerbangan..."):
    df = fetch_flights()

if df.empty:
    st.error("Gagal mengambil data dari API. Coba lagi nanti.")
    st.stop()

# --- Info ringkas ---
st.success(f"Berhasil memuat {len(df)} data penerbangan pada {datetime.now().strftime('%H:%M:%S')}")

# --- Peta Realtime ---
st.subheader("🌍 Peta Posisi Pesawat Realtime")

fig_map = px.scatter_geo(
    df,
    lon="longitude",
    lat="latitude",
    hover_name="callsign",
    hover_data=["origin_country", "baro_altitude", "velocity"],
    color="origin_country",
    projection="natural earth",
    title="Lokasi Pesawat (Realtime)"
)
fig_map.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig_map, use_container_width=True)

# --- Statistik Per Negara ---
st.subheader("📊 Jumlah Pesawat Aktif per Negara")
country_count = df["origin_country"].value_counts().reset_index()
country_count.columns = ["Negara", "Jumlah Pesawat"]

fig_bar = px.bar(country_count.head(10), x="Negara", y="Jumlah Pesawat", color="Negara")
st.plotly_chart(fig_bar, use_container_width=True)

# --- Data Tabel ---
st.subheader("📋 Data Detail Penerbangan")
st.dataframe(df[["callsign", "origin_country", "longitude", "latitude", "baro_altitude", "velocity"]])

# --- Ekspor ke CSV ---
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("💾 Download CSV", csv, "flight_data.csv", "text/csv")
