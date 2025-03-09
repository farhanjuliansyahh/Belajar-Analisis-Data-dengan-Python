import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

#data yang di import adalah day.csv karena sudah bisa mewakili daya yang di eksplorasi
def read_data(file='dashboard/day.csv'):
    try:
        data = pd.read_csv(file)
        data['dteday'] = pd.to_datetime(data['dteday'])
        return data
    except:
        st.error('file .csv tidak ditemukan!')
        return None

def hitung_stats_musim(data):
    nama_musim = {1:'Musim Semi', 2:'Musim Panas', 3:'Musim Gugur', 4:'Musim Dingin'}
    data['nama_musim'] = data['season'].map(nama_musim)
    
    urutan = ['Musim Semi', 'Musim Panas', 'Musim Gugur', 'Musim Dingin']
    
    hasil = data.groupby('nama_musim').agg({
        'cnt': ['min', 'max', 'mean', 'sum']
    }).round(2).reset_index()
    
    hasil['nama_musim'] = pd.Categorical(hasil['nama_musim'], categories=urutan, ordered=True)
    hasil = hasil.sort_values('nama_musim').reset_index(drop=True)
    hasil.index = hasil.index + 1
    return hasil

def hitung_stats_bulanan(data):
    data['bulan_tahun'] = data['dteday'].dt.strftime('%B %Y')
    
    hasil = data.groupby('bulan_tahun').agg({
        'cnt': ['min', 'max', 'mean', 'sum']
    }).round(2).reset_index()
    
    hasil['tgl_urut'] = pd.to_datetime(hasil['bulan_tahun'], format='%B %Y')
    hasil = hasil.sort_values('tgl_urut')
    hasil = hasil.drop('tgl_urut', axis=1).reset_index(drop=True)
    hasil.index = hasil.index + 1
    return hasil

# Read data aplikasi
data_mentah = read_data()

st.title("📊 Dashboard Penyewaan Sepeda")

# Logo di sidebar
st.sidebar.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=100)

# Filter tanggal
st.sidebar.header("📅 Pilih Rentang Waktu")
tgl_awal = data_mentah['dteday'].min().date()
tgl_akhir = data_mentah['dteday'].max().date()

mulai = st.sidebar.date_input("Dari:", tgl_awal, min_value=tgl_awal, max_value=tgl_akhir)
sampai = st.sidebar.date_input("Sampai:", tgl_akhir, min_value=tgl_awal, max_value=tgl_akhir)

# Filter data
data = data_mentah[(data_mentah['dteday'].dt.date >= mulai) & (data_mentah['dteday'].dt.date <= sampai)]

# Pilihan tampilan
st.sidebar.header("🔍 Tampilkan Data")
pilihan = st.sidebar.radio("Berdasarkan:", ("Musim", "Bulan"))

st.write(f"Data Penyewaan sepeda dari {mulai.strftime('%d %B %Y')} - {sampai.strftime('%d %B %Y')}")

if pilihan == "Musim":
    st.header("🌤️ Statistik per Musim")
    stats = hitung_stats_musim(data)
    st.dataframe(stats)
    
    # Buat visualisasi data
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=stats, x="nama_musim", y=("cnt", "sum"), palette="Set2", ax=ax)
    plt.xlabel("Musim")
    plt.ylabel("Total Penyewaan")
    plt.title("Jumlah Penyewaan per Musim")
    plt.xticks(rotation=45)
    st.pyplot(fig)

else:
    st.header("📅 Statistik per Bulan")
    stats = hitung_stats_bulanan(data)
    st.dataframe(stats)
    
    # Buat visualisasi data
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=stats, x="bulan_tahun", y=("cnt", "sum"), marker="o", ax=ax)
    plt.xticks(rotation=45)
    plt.xlabel("Bulan")
    plt.ylabel("Total Penyewaan")
    plt.title("Performa Penyewaan Sepeda")
    st.pyplot(fig)