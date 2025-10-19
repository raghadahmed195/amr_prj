import streamlit as st
import json
import os
from PyPDF2 import PdfMerger
import io
import base64

# ================================================================
# PAGE SETTINGS
# ================================================================
st.set_page_config(page_title="PDF Viewer & Merger", layout="centered")
st.title("📘 Fischer Product PDF Viewer & Merger")

# ================================================================
# PATHS
# ================================================================
BASE_PATH = r"C:\Users\user\Desktop\myfawry\amr - Copy\amr_prj\prj\data"
JSON_PATH = os.path.join(BASE_PATH, "names.json")
DATA_PATH = os.path.join(BASE_PATH, "data")
PREQUAL_PATH = os.path.join(DATA_PATH, "Pre-q.pdf")

# ================================================================
# LOAD JSON FILE
# ================================================================
try:
    with open(JSON_PATH, "r") as f:
        category_data = json.load(f)
except Exception as e:
    st.error(f"❌ Error loading JSON file: {e}")
    st.stop()

# ================================================================
# STEP 1: Choose Category
# ================================================================
st.header("Step 1: Select Product Category")
selected_category = st.selectbox("Select SBU Category", list(category_data.keys()))

# ================================================================
# STEP 2: Choose Multiple Products
# ================================================================
selected_products = []
if selected_category:
    st.header("Step 2: Select Products")
    product_list = category_data[selected_category]

    # Create checkboxes for each product
    st.write("✅ Choose one or more products:")
    for product in product_list:
        if st.checkbox(product):
            selected_products.append(product)

# ================================================================
# STEP 3: Display and Download Each Selected Product PDF
# ================================================================
if selected_products:
    for selected_product in selected_products:
        pdf_path = os.path.join(DATA_PATH, f"{selected_product}.pdf")

        if os.path.exists(pdf_path):
            st.subheader(f"📄 Viewing PDF for: {selected_product}")

            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            # Download button for each
            st.download_button(
                label=f"📥 Download {selected_product}.pdf",
                data=pdf_bytes,
                file_name=f"{selected_product}.pdf",
                mime="application/pdf"
            )

            # Display inline
            base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_display = f"""
                <iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error(f"⚠️ PDF not found: {pdf_path}")

# ================================================================
# STEP 4: Merge Selected PDFs with Pre-Qualification
# ================================================================
if selected_products and os.path.exists(PREQUAL_PATH):
    st.header("Step 3: Merge with Pre-Qualification PDF")

    if st.button("🔀 Merge Selected PDFs with Pre-Qualification"):
        merger = PdfMerger()

        try:
            # ✅ Append all selected products first, then Pre-Qualification
            for product in selected_products:
                pdf_path = os.path.join(DATA_PATH, f"{product}.pdf")
                if os.path.exists(pdf_path):
                    merger.append(pdf_path)

            merger.append(PREQUAL_PATH)

            # Write to memory
            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            merger.close()
            output_buffer.seek(0)

            # Read merged content for viewing
            merged_bytes = output_buffer.getvalue()
            merged_name = f"{'_'.join(selected_products)}_with_PreQualification.pdf"

            st.success("✅ Merged PDF created successfully!")

            # ✅ Display merged PDF inline
            base64_merged = base64.b64encode(merged_bytes).decode("utf-8")
            merged_display = f"""
                <iframe src="data:application/pdf;base64,{base64_merged}" width="700" height="900" type="application/pdf"></iframe>
            """
            st.markdown(merged_display, unsafe_allow_html=True)

            # ✅ Download button for merged PDF
            st.download_button(
                label=f"📥 Download {merged_name}",
                data=merged_bytes,
                file_name=merged_name,
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"❌ Error merging PDFs: {e}")
