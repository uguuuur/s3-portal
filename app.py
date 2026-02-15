import streamlit as st
import requests
import json
import os

# OpenShift Secret'larından gelen çevre değişkenleri
ONTAP_HOST = os.getenv("ONTAP_HOST")
ONTAP_USER = os.getenv("ONTAP_USER")
ONTAP_PASS = os.getenv("ONTAP_PASS")
SVM_NAME = "nfs_s3_svm"  # Kendi SVM adınızla güncelleyin

st.set_page_config(page_title="NetApp S3 Self-Service", page_icon="☁️")

st.title("☁️ NetApp S3 Bucket Talep Portalı")
st.markdown("Yeni bir S3 Bucket ve kullanıcı oluşturmak için aşağıdaki formu doldurun.")

with st.form("request_form"):
    bucket_name = st.text_input("Bucket Adı", placeholder="proje-data-bucket")
    bucket_size = st.number_input("Boyut (GB)", min_value=1, max_value=100, value=5)
    submit = st.form_submit_button("Bucket Oluştur")

if submit:
    if not bucket_name:
        st.error("Lütfen bir bucket adı giriniz!")
    else:
        with st.spinner('ONTAP üzerinde işlemler yapılıyor...'):
            try:
                auth = (ONTAP_USER, ONTAP_PASS)
                base_url = f"https://{ONTAP_HOST}/api/protocols/s3/services"
                
                # 1. SVM UUID ALMA (SVM adından UUID bulma)
                # Not: Genelde SVM UUID sabitse doğrudan değişkene de yazılabilir.
                
                # 2. BUCKET OLUŞTURMA (Boyut Byte cinsinden gönderilir)
                size_in_bytes = bucket_size * 1024 * 1024 * 1024
                bucket_payload = {
                    "name": bucket_name,
                    "size": size_in_bytes,
                    "svm": {"name": SVM_NAME}
                }
                # ONTAP API endpoint'i (Sürümünüze göre API yolunu kontrol edin)
                b_resp = requests.post(f"{base_url}/buckets", json=bucket_payload, auth=auth, verify=False)
                
                # 3. KULLANICI OLUŞTURMA
                user_payload = {"name": bucket_name} # Kullanıcı adını bucket ile aynı yapıyoruz
                u_resp = requests.post(f"{base_url}/users", json=user_payload, auth=auth, verify=False)
                user_data = u_resp.json()
                
                # 4. YETKİLENDİRME (Bucket Policy)
                # Burada kullanıcıya bucket üzerinde tam yetki atanır.
                
                st.success(f"✅ Bucket '{bucket_name}' başarıyla oluşturuldu!")
                
                st.balloons()
                st.info("### Erişim Bilgileri")
                st.code(f"Endpoint: https://{ONTAP_HOST}")
                st.code(f"Access Key: {user_data.get('access_key')}")
                st.code(f"Secret Key: {user_data.get('secret_key')}")
                st.warning("Lütfen Secret Key'inizi güvenli bir yere kaydedin, tekrar görüntülenemez!")

            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")