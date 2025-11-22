import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import os
import json

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate


# --------------------------------------------------------------
# Initialize Session State
# --------------------------------------------------------------
if "mapping" not in st.session_state:
    st.session_state.mapping = []

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0   # to clear canvas


# --------------------------------------------------------------
# Title
# --------------------------------------------------------------
st.title("✍️ Unknown Script → ITRANS → Bengali | Mapper with Image Save + Delete + Clear")


st.write("""
Draw a symbol, type its **ITRANS**, and the system will:
- Convert ITRANS → Bengali  
- Save the image  
- Store mapping  
You can **clear the drawing**, **delete any saved mapping**, and **export JSON**.
""")


# --------------------------------------------------------------
# Drawing Canvas
# --------------------------------------------------------------
canvas = st_canvas(
    fill_color="rgba(255,255,255,1)",
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=300,
    width=300,
    drawing_mode="freedraw",
    stroke_width=6,
    key=f"canvas_{st.session_state.canvas_key}",
)


itrans_input = st.text_input("Enter ITRANS (max 10 chars)", max_chars=10)


# Create saved image folder
os.makedirs("symbols", exist_ok=True)


# --------------------------------------------------------------
# Save mapping
# --------------------------------------------------------------
if st.button("Save Symbol"):
    if canvas.image_data is None:
        st.error("Please draw something first.")
    elif not itrans_input.strip():
        st.error("Please enter ITRANS text.")
    else:
        # Convert drawing to image
        img = Image.fromarray(canvas.image_data.astype("uint8"))

        # Auto-map to Bengali
        try:
            bengali = transliterate(itrans_input, sanscript.ITRANS, sanscript.BENGALI)
        except:
            bengali = "?"

        # Save as PNG
        file_path = f"symbols/{itrans_input}.png"
        img.save(file_path)

        # Create mapping entry
        entry = {
            "itrans": itrans_input,
            "bengali": bengali,
            "image_path": file_path
        }

        st.session_state.mapping.append(entry)

        st.success(f"Saved: {itrans_input} → {bengali}")
        st.image(img, caption=f"Saved: {itrans_input}", width=150)


# --------------------------------------------------------------
# Clear Canvas
# --------------------------------------------------------------
if st.button("Clear Drawing Area"):
    st.session_state.canvas_key += 1
    st.rerun()


# --------------------------------------------------------------
# Show All Mappings
# --------------------------------------------------------------
st.write("### 🔎 Saved Mappings")
if not st.session_state.mapping:
    st.info("No symbols saved yet.")
else:
    for index, item in enumerate(st.session_state.mapping):
        col1, col2, col3 = st.columns([2, 3, 2])

        with col1:
            st.image(item["image_path"], width=80)

        with col2:
            st.write(f"**ITRANS:** {item['itrans']}")
            st.write(f"**Bengali:** {item['bengali']}")

        with col3:
            if st.button("Delete", key=f"del_{index}"):
                # Delete image file
                if os.path.exists(item["image_path"]):
                    os.remove(item["image_path"])

                # Remove from mapping
                st.session_state.mapping.pop(index)
                st.rerun()


# --------------------------------------------------------------
# Download JSON
# --------------------------------------------------------------
if st.session_state.mapping:
    json_output = json.dumps(st.session_state.mapping, ensure_ascii=False, indent=4)
    st.download_button(
        "⬇️ Download Mapping JSON",
        data=json_output,
        file_name="unknown_itrans_bengali_mapping.json",
        mime="application/json"
    )
