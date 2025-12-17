import streamlit as st
import os
import tempfile
import zipfile
import subprocess
import concurrent.futures
from moviepy.config import get_setting

# --- CONFIGURATION ---
LOGO_DIR = "saved_logos"

# Create logo directory
if not os.path.exists(LOGO_DIR):
    os.makedirs(LOGO_DIR)

# --- FFMPEG SETUP ---
try:
    FFMPEG_BINARY = get_setting("FFMPEG_BINARY")
except:
    FFMPEG_BINARY = "ffmpeg" 

def get_ffmpeg_position_cmd(mode, pos_v, pos_h, margin, custom_x, custom_y):
    """Returns the FFmpeg overlay coordinates based on mode."""
    if mode == "Custom (Manual X/Y)":
        return f"{custom_x}:{custom_y}"
    
    # Standard Presets Logic
    # X Coordinate
    if pos_h == 'left':
        x = f"{margin}"
    elif pos_h == 'right':
        x = f"main_w-overlay_w-{margin}"
    else: # center
        x = "(main_w-overlay_w)/2"
        
    # Y Coordinate
    if pos_v == 'top':
        y = f"{margin}"
    elif pos_v == 'bottom':
        y = f"main_h-overlay_h-{margin}"
    else: # center
        y = "(main_h-overlay_h)/2"
        
    return f"{x}:{y}"

def generate_preview_frame(video_path, logo_path, size_w, overlay_cmd):
    """Generates a single frame preview."""
    output_image = os.path.join(tempfile.gettempdir(), "preview_debug.jpg")
    
    # Scale width to user input, height auto (-1)
    command = [
        FFMPEG_BINARY, '-y',
        '-ss', '00:00:01',      # Seek to 1 second
        '-i', video_path,
        '-i', logo_path,
        '-filter_complex', f"[1:v]scale={size_w}:-1[logo];[0:v][logo]overlay={overlay_cmd}",
        '-frames:v', '1',
        '-q:v', '2',
        output_image
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_image
    except subprocess.CalledProcessError:
        return None

def process_video_ffmpeg(video_path, logo_path, output_path, size_w, overlay_cmd):
    """Batch process video using FFmpeg."""
    command = [
        FFMPEG_BINARY, '-y',
        '-i', video_path,
        '-i', logo_path,
        '-filter_complex', f"[1:v]scale={size_w}:-1[logo];[0:v][logo]overlay={overlay_cmd}",
        '-c:a', 'copy',          
        '-preset', 'ultrafast',  
        output_path
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

# --- UI SETUP ---
st.set_page_config(page_title="Turbo Video Watermarker", layout="wide")
st.title("⚡ Turbo Batch Logo Adder")

# Custom CSS
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    div[data-testid="stButton"]:last-child > button { background-color: #00CC00; color: white; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])
active_logo_path = None

with col1:
    st.subheader("1. Logo Settings")
    
    # --- LOGO LIBRARY ---
    saved_logos = [f for f in os.listdir(LOGO_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    tab1, tab2 = st.tabs(["📂 Select Logo", "⬆️ Upload New"])
    
    with tab1:
        if saved_logos:
            selected_filename = st.selectbox("Choose from Library:", saved_logos)
            active_logo_path = os.path.join(LOGO_DIR, selected_filename)
            st.image(active_logo_path, width=150)
            
            # --- NEW: DELETE BUTTON ---
            st.write("") # Spacer
            if st.button("🗑️ Delete Selected Logo", type="primary"):
                try:
                    os.remove(active_logo_path)
                    st.warning(f"Deleted '{selected_filename}'")
                    st.rerun() # Refresh the page immediately
                except Exception as e:
                    st.error(f"Error deleting: {e}")
            # --------------------------
            
        else:
            st.info("Library empty. Upload a logo first.")

    with tab2:
        ul_logo = st.file_uploader("Upload New", type=['png', 'jpg'])
        if ul_logo:
            name = st.text_input("Name", value="NewLogo")
            if st.button("💾 Save to Library"):
                clean_name = "".join(x for x in name if x.isalnum())
                with open(os.path.join(LOGO_DIR, f"{clean_name}.png"), "wb") as f:
                    f.write(ul_logo.getbuffer())
                st.success("Saved! Switch to Library tab.")
                st.rerun()

    st.divider()
    
    # --- CUSTOM SIZER & ARRANGER ---
    st.write("📏 **Size & Position**")
    
    # 1. SIZE SLIDER
    logo_width_px = st.slider("Logo Width (px)", min_value=50, max_value=1000, value=250, step=10)
    
    # 2. POSITION MODE
    pos_mode = st.radio("Position Mode:", ["Standard Presets", "Custom (Manual X/Y)"], horizontal=True)
    
    # Variables to hold final settings
    p_v, p_h, p_margin = "bottom", "left", 20
    custom_x, custom_y = 10, 10
    
    if pos_mode == "Standard Presets":
        c_v, c_h = st.columns(2)
        with c_v: p_v = st.selectbox("Vertical", ["bottom", "top", "center"])
        with c_h: p_h = st.selectbox("Horizontal", ["left", "right", "center"])
        p_margin = st.slider("Margin (Padding)", 0, 100, 20)
    else:
        c_x, c_y = st.columns(2)
        with c_x: custom_x = st.number_input("X Position (px)", value=10)
        with c_y: custom_y = st.number_input("Y Position (px)", value=10)

    st.divider()
    
    # --- SPEED SETTINGS (RESTORED) ---
    st.write("🚀 **Speed Settings**")
    workers = st.slider("Concurrent Videos (Higher = Faster)", 1, 5, 3)

with col2:
    st.subheader("2. Preview & Process")
    uploaded_videos = st.file_uploader("Drop Videos Here", type=['mp4', 'mov', 'avi'], accept_multiple_files=True)

    # Calculate the exact FFmpeg command string based on current UI settings
    final_overlay_cmd = get_ffmpeg_position_cmd(pos_mode, p_v, p_h, p_margin, custom_x, custom_y)

    # --- PREVIEW SECTION ---
    if uploaded_videos and active_logo_path:
        st.write("---")
        col_prev_btn, col_prev_img = st.columns([1, 2])
        
        with col_prev_btn:
            st.write("### Check Alignment")
            if st.button("👁️ Generate Preview"):
                with st.spinner("Generating preview..."):
                    # Save temp video
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as t_vid:
                        t_vid.write(uploaded_videos[0].getbuffer())
                        temp_vid_path = t_vid.name
                    
                    # Generate Image with NEW SIZE and NEW POS
                    prev_img = generate_preview_frame(temp_vid_path, active_logo_path, logo_width_px, final_overlay_cmd)
                    
                    if prev_img:
                        st.session_state['preview_image'] = prev_img
                    else:
                        st.error("Preview failed.")
                    
                    os.remove(temp_vid_path)
        
        with col_prev_img:
            if 'preview_image' in st.session_state:
                st.image(st.session_state['preview_image'], caption="Preview Result", use_column_width=True)

st.divider()

# --- BATCH PROCESS ---
if st.button("⚡ START TURBO PROCESSING"):
    if not uploaded_videos or not active_logo_path:
        st.error("Please select a logo and videos first.")
    else:
        progress_bar = st.progress(0)
        status_area = st.empty()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "processed_videos.zip")
            processed_paths = []
            
            # Helper for threading
            def process_single(args):
                idx, vid_file = args
                t_in = os.path.join(temp_dir, f"in_{idx}.mp4")
                with open(t_in, "wb") as f:
                    f.write(vid_file.getbuffer())
                
                t_out = os.path.join(temp_dir, f"branded_{vid_file.name}")
                
                # Use the dynamic width and overlay command
                ok = process_video_ffmpeg(t_in, active_logo_path, t_out, logo_width_px, final_overlay_cmd)
                return t_out if ok else None

            # Execute Parallel with SELECTED WORKERS
            status_area.text(f"Processing {len(uploaded_videos)} videos using {workers} threads...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                args_list = [(i, v) for i, v in enumerate(uploaded_videos)]
                completed = 0
                for result in executor.map(process_single, args_list):
                    if result:
                        processed_paths.append(result)
                    completed += 1
                    progress_bar.progress(completed / len(uploaded_videos))

            # Zip and Download
            if processed_paths:
                status_area.text("Zipping...")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for p in processed_paths:
                        zipf.write(p, os.path.basename(p))
                
                with open(zip_path, "rb") as f:
                    st.success("✅ Done!")
                    st.download_button("📥 Download ZIP", f, "branded_videos.zip", "application/zip")
            else:
                st.error("Processing failed.")