import streamlit as st
import os
import tempfile
import zipfile
import subprocess
import concurrent.futures

# --- ATTEMPT TO FIND FFMPEG AUTOMATICALLY ---
# We try to find the ffmpeg binary that MoviePy already installed
FFMPEG_BINARY = "ffmpeg"

# --- CONFIGURATION ---
LOGO_DIR = "saved_logos"
LOGO_SIZE = (250, 250) 
LOGO_MARGIN = 15

if not os.path.exists(LOGO_DIR):
    os.makedirs(LOGO_DIR)

def get_ffmpeg_overlay_cmd(position_str):
    """Returns the FFmpeg filter string for positioning."""
    # FFmpeg coordinates: 'main_w' is video width, 'overlay_w' is logo width
    
    # Left / Right
    if 'left' in position_str:
        x = f"{LOGO_MARGIN}"
    elif 'right' in position_str:
        x = f"main_w-overlay_w-{LOGO_MARGIN}"
    else: # Center
        x = "(main_w-overlay_w)/2"
        
    # Top / Bottom
    if 'top' in position_str:
        y = f"{LOGO_MARGIN}"
    elif 'bottom' in position_str:
        y = f"main_h-overlay_h-{LOGO_MARGIN}"
    else: # Center
        y = "(main_h-overlay_h)/2"
        
    return f"{x}:{y}"

def process_video_ffmpeg(video_path, logo_path, output_path, position):
    """
    Processes video using raw FFmpeg commands (FASTEST METHOD).
    """
    overlay_cmd = get_ffmpeg_overlay_cmd(position)
    
    # This command scales the logo to 500x500 AND overlays it in one step
    # -c:a copy  --> COPIES audio (super fast) instead of re-encoding
    # -preset ultrafast --> Uses less CPU compression for speed
    command = [
        FFMPEG_BINARY,
        '-y', # Overwrite output if exists
        '-i', video_path,
        '-i', logo_path,
        '-filter_complex', f"[1:v]scale={LOGO_SIZE[0]}:{LOGO_SIZE[1]}[logo];[0:v][logo]overlay={overlay_cmd}",
        '-c:a', 'copy', 
        '-preset', 'ultrafast',
        output_path
    ]
    
    try:
        # Run the command silently
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        st.error("FFmpeg binary not found. Please install FFmpeg on your system.")
        return False

# --- UI SETUP ---
st.set_page_config(page_title="Turbo Video Watermarker", layout="wide")
st.title("⚡ Turbo Batch Logo Adder")

# CSS for better looking buttons
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #00CC00; color: white; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

# STATE
active_logo_path = None

with col1:
    st.subheader("1. Setup")
    
    # Logo Selection
    saved_logos = [f for f in os.listdir(LOGO_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    tab1, tab2 = st.tabs(["📂 Library", "⬆️ Upload"])
    
    with tab1:
        if saved_logos:
            selected_filename = st.selectbox("Select Logo:", saved_logos)
            active_logo_path = os.path.join(LOGO_DIR, selected_filename)
            st.image(active_logo_path, width=150)
        else:
            st.info("No saved logos.")

    with tab2:
        ul_logo = st.file_uploader("New Logo", type=['png', 'jpg'])
        if ul_logo:
            name = st.text_input("Logo Name", value="MyLogo")
            if st.button("Save Logo"):
                clean_name = "".join(x for x in name if x.isalnum())
                with open(os.path.join(LOGO_DIR, f"{clean_name}.png"), "wb") as f:
                    f.write(ul_logo.getbuffer())
                st.success("Saved! Check Library tab.")
                st.rerun()

    st.divider()
    
    # Position Controls
    st.write("Logo Position:")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        pos_v = st.selectbox("Vertical", ["bottom", "top", "center"])
    with col_p2:
        pos_h = st.selectbox("Horizontal", ["left", "right", "center"])
    
    current_pos_str = f"{pos_v}_{pos_h}" # e.g. "bottom_left"

    st.divider()
    
    # Performance Control
    st.write("🚀 **Speed Settings**")
    workers = st.slider("Concurrent Videos (Higher = Faster but uses more CPU)", 1, 5, 3)

with col2:
    st.subheader("2. Videos")
    uploaded_videos = st.file_uploader("Drop videos here (Unlimited)", type=['mp4', 'mov', 'avi'], accept_multiple_files=True)
    
    if uploaded_videos and active_logo_path:
        st.info(f"Ready to process {len(uploaded_videos)} videos with '{os.path.basename(active_logo_path)}' at {pos_v}-{pos_h}.")

st.divider()

if st.button("⚡ START TURBO PROCESS"):
    if not uploaded_videos or not active_logo_path:
        st.error("Missing videos or logo!")
    else:
        # UI Elements for progress
        progress_bar = st.progress(0)
        status_area = st.empty()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "processed_videos.zip")
            processed_paths = []
            
            # Prepare arguments for parallel processing
            tasks = []
            
            # 1. Save all inputs to temp first (Disk I/O)
            status_area.text("Preparing files...")
            
            # Define a helper to package the work
            def prep_and_run(index, vid_file):
                # Input Path
                t_in = os.path.join(temp_dir, f"in_{index}.mp4")
                with open(t_in, "wb") as f:
                    f.write(vid_file.getbuffer())
                
                # Output Path
                t_out = os.path.join(temp_dir, f"branded_{vid_file.name}")
                
                # Run FFmpeg
                success = process_video_ffmpeg(t_in, active_logo_path, t_out, current_pos_str)
                return t_out if success else None

            # 2. Parallel Execution
            status_area.text(f"Processing {len(uploaded_videos)} videos using {workers} CPU cores...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                # Submit all tasks
                future_to_vid = {executor.submit(prep_and_run, i, vid): vid for i, vid in enumerate(uploaded_videos)}
                
                completed_count = 0
                for future in concurrent.futures.as_completed(future_to_vid):
                    result_path = future.result()
                    if result_path:
                        processed_paths.append(result_path)
                    
                    completed_count += 1
                    progress_bar.progress(completed_count / len(uploaded_videos))
            
            # 3. Zipping
            if processed_paths:
                status_area.text("Compressing into ZIP...")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for p in processed_paths:
                        zipf.write(p, os.path.basename(p))
                
                with open(zip_path, "rb") as f:
                    st.success(f"✅ Done! Processed {len(processed_paths)} videos.")
                    st.download_button("📥 Download ZIP", f, "turbo_videos.zip", "application/zip")
            else:
                st.error("Processing failed. Check if FFmpeg is installed.")