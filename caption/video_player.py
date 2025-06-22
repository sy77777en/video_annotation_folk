import streamlit as st
import streamlit.components.v1 as components

def custom_video_player(video_url, aspect_ratio="16:9", autoplay=False, loop=False):
    """Custom video player with responsive design"""
    ratio_parts = aspect_ratio.split(":")
    aspect_ratio_decimal = float(ratio_parts[0]) / float(ratio_parts[1])
    padding_bottom = (1 / aspect_ratio_decimal) * 100
    
    video_attributes = 'preload="metadata"'
    if autoplay:
        video_attributes += ' autoplay muted'
    if loop:
        video_attributes += ' loop'
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            html, body {{ height: 100%; font-family: Arial, sans-serif; overflow: hidden; }}
            
            .video-container {{
                width: 100%; height: 100%; display: flex; flex-direction: column;
                background: #fff; overflow: hidden;
            }}
            
            .video-wrapper {{
                position: relative; width: 100%; flex: 1; background: #000;
                border-radius: 8px 8px 0 0; overflow: hidden; min-height: 200px;
            }}
            
            .video-wrapper::before {{
                content: ''; display: block; padding-bottom: {padding_bottom}%;
            }}
            
            video {{
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                object-fit: contain;
            }}
            
            video::-webkit-media-controls, video::-moz-media-controls {{
                display: none !important;
            }}
            
            .controls-container {{
                width: 100%; background: #f8f9fa; border: 1px solid #e9ecef;
                border-top: none; border-radius: 0 0 8px 8px; padding: 8px 12px;
                flex-shrink: 0; overflow: hidden; min-height: 65px; max-height: 80px;
            }}
            
            .progress-container {{
                width: 100%; height: 6px; background: #ddd; border-radius: 3px;
                margin-bottom: 8px; cursor: pointer; position: relative;
                user-select: none; overflow: hidden;
            }}
            
            .progress-bar {{
                height: 100%; background: #9553FE;
                border-radius: 3px; width: 0%; pointer-events: none; transition: none;
            }}
            
            .progress-handle {{
                position: absolute; top: -5px; width: 16px; height: 16px;
                background: #9553FE; border: 2px solid white; border-radius: 50%;
                cursor: grab; transform: translateX(-50%); opacity: 0;
                transition: opacity 0.2s ease, transform 0.1s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }}
            
            .progress-handle:active {{ cursor: grabbing; transform: translateX(-50%) scale(1.1); }}
            .progress-container:hover .progress-handle {{ opacity: 1; }}
            
            .controls {{
                display: flex; align-items: center; gap: 6px; width: 100%;
                overflow: hidden; min-height: 32px;
            }}
            
            .control-btn {{
                background: none; border: none; font-size: 14px; cursor: pointer;
                padding: 4px 6px; border-radius: 4px; transition: background 0.2s ease;
                display: flex; align-items: center; justify-content: center;
                min-width: 28px; height: 28px; flex-shrink: 0;
            }}
            
            .control-btn:hover {{ background: #e9ecef; }}
            
            .time-display {{
                font-size: 11px; color: #666; margin-left: auto; white-space: nowrap;
                font-family: 'Courier New', monospace; flex-shrink: 0;
                overflow: hidden; text-overflow: ellipsis; max-width: 120px;
            }}
            
            .volume-control {{ display: flex; align-items: center; gap: 4px; flex-shrink: 0; }}
            
            .volume-slider {{
                width: 50px; height: 3px; background: #ddd; outline: none;
                border-radius: 2px; -webkit-appearance: none; flex-shrink: 0;
            }}
            
            .volume-slider::-webkit-slider-thumb {{
                -webkit-appearance: none; width: 12px; height: 12px;
                background: #9553FE; border-radius: 50%; cursor: pointer;
            }}
            
            .volume-slider::-moz-range-thumb {{
                width: 12px; height: 12px; background: #9553FE;
                border-radius: 50%; cursor: pointer; border: none;
            }}
            
            @media (max-width: 600px) {{
                .controls {{ gap: 4px; }}
                .control-btn {{ font-size: 12px; min-width: 24px; height: 24px; padding: 2px 4px; }}
                .time-display {{ font-size: 10px; max-width: 80px; }}
                .volume-slider {{ width: 40px; }}
                .controls-container {{ padding: 6px 8px; min-height: 60px; }}
                .progress-container {{ height: 5px; margin-bottom: 6px; }}
            }}
        </style>
    </head>
    <body>
        <div class="video-container">
            <div class="video-wrapper">
                <video id="customVideo" {video_attributes}>
                    <source src="{video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            
            <div class="controls-container">
                <div class="progress-container" id="progressContainer">
                    <div class="progress-bar" id="progressBar"></div>
                    <div class="progress-handle" id="progressHandle"></div>
                </div>
                
                <div class="controls">
                    <button class="control-btn" id="playPauseBtn" title="Play/Pause">{"⏸️" if autoplay else "▶️"}</button>
                    <button class="control-btn" id="muteBtn" title="Mute/Unmute">🔊</button>
                    <div class="volume-control">
                        <input type="range" class="volume-slider" id="volumeSlider" min="0" max="100" value="100" title="Volume">
                    </div>
                    <div class="time-display" id="timeDisplay">0:00 / 0:00</div>
                    <button class="control-btn" id="downloadBtn" title="Download">📥</button>
                    <button class="control-btn" id="fullscreenBtn" title="Fullscreen">⛶</button>
                </div>
            </div>
        </div>

        <script>
            const video = document.getElementById('customVideo');
            const playPauseBtn = document.getElementById('playPauseBtn');
            const muteBtn = document.getElementById('muteBtn');
            const volumeSlider = document.getElementById('volumeSlider');
            const progressContainer = document.getElementById('progressContainer');
            const progressBar = document.getElementById('progressBar');
            const progressHandle = document.getElementById('progressHandle');
            const timeDisplay = document.getElementById('timeDisplay');
            const downloadBtn = document.getElementById('downloadBtn');
            const fullscreenBtn = document.getElementById('fullscreenBtn');

            let isDragging = false;
            let wasPlaying = false;
            const isAutoplay = {str(autoplay).lower()};
            
            if (isAutoplay) {{
                video.addEventListener('loadeddata', () => {{
                    if (video.paused) {{
                        video.play().catch(e => console.log('Autoplay prevented:', e));
                    }}
                    playPauseBtn.textContent = video.paused ? '▶️' : '⏸️';
                }});
            }}

            playPauseBtn.addEventListener('click', () => {{
                if (video.paused) {{
                    video.play();
                    playPauseBtn.textContent = '⏸️';
                }} else {{
                    video.pause();
                    playPauseBtn.textContent = '▶️';
                }}
            }});

            muteBtn.addEventListener('click', () => {{
                video.muted = !video.muted;
                muteBtn.textContent = video.muted ? '🔇' : '🔊';
            }});

            volumeSlider.addEventListener('input', () => {{
                video.volume = volumeSlider.value / 100;
            }});

            function updateProgress() {{
                if (!isDragging && video.duration) {{
                    const progress = (video.currentTime / video.duration) * 100;
                    progressBar.style.width = progress + '%';
                    progressHandle.style.left = progress + '%';
                    
                    const currentTime = formatTime(video.currentTime);
                    const duration = formatTime(video.duration);
                    timeDisplay.textContent = `${{currentTime}} / ${{duration}}`;
                }}
                requestAnimationFrame(updateProgress);
            }}
            
            updateProgress();

            function getProgressFromMouse(e) {{
                const rect = progressContainer.getBoundingClientRect();
                return Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
            }}

            progressContainer.addEventListener('mousedown', (e) => {{
                isDragging = true;
                wasPlaying = !video.paused;
                if (wasPlaying) video.pause();
                
                const percent = getProgressFromMouse(e);
                const newTime = percent * video.duration;
                
                progressBar.style.width = (percent * 100) + '%';
                progressHandle.style.left = (percent * 100) + '%';
                video.currentTime = newTime;
                
                const currentTime = formatTime(newTime);
                const duration = formatTime(video.duration);
                timeDisplay.textContent = `${{currentTime}} / ${{duration}}`;
                
                e.preventDefault();
            }});

            document.addEventListener('mousemove', (e) => {{
                if (isDragging) {{
                    const percent = getProgressFromMouse(e);
                    const newTime = percent * video.duration;
                    
                    progressBar.style.width = (percent * 100) + '%';
                    progressHandle.style.left = (percent * 100) + '%';
                    video.currentTime = newTime;
                    
                    const currentTime = formatTime(newTime);
                    const duration = formatTime(video.duration);
                    timeDisplay.textContent = `${{currentTime}} / ${{duration}}`;
                }}
            }});

            document.addEventListener('mouseup', () => {{
                if (isDragging) {{
                    isDragging = false;
                    if (wasPlaying) video.play();
                }}
            }});

            progressContainer.addEventListener('click', (e) => {{
                if (!isDragging) {{
                    const percent = getProgressFromMouse(e);
                    video.currentTime = percent * video.duration;
                }}
            }});

            fullscreenBtn.addEventListener('click', () => {{
                if (document.fullscreenElement) {{
                    document.exitFullscreen();
                }} else {{
                    document.querySelector('.video-wrapper').requestFullscreen();
                }}
            }});

            downloadBtn.addEventListener('click', async () => {{
                try {{
                    const response = await fetch('{video_url}');
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '{video_url}'.split('/').pop();
                    a.style.display = 'none';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                }} catch (error) {{
                    console.error('Download failed:', error);
                    // Fallback to direct link
                    const a = document.createElement('a');
                    a.href = '{video_url}';
                    a.download = '{video_url}'.split('/').pop();
                    a.target = '_blank';
                    a.click();
                }}
            }});

            function formatTime(time) {{
                if (isNaN(time)) return '0:00';
                const minutes = Math.floor(time / 60);
                const seconds = Math.floor(time % 60);
                return `${{minutes}}:${{seconds.toString().padStart(2, '0')}}`;
            }}

            video.addEventListener('ended', () => {{ playPauseBtn.textContent = '▶️'; }});
            video.addEventListener('play', () => {{ playPauseBtn.textContent = '⏸️'; }});
            video.addEventListener('pause', () => {{ playPauseBtn.textContent = '▶️'; }});

            video.addEventListener('loadedmetadata', () => {{
                const duration = formatTime(video.duration);
                timeDisplay.textContent = `0:00 / ${{duration}}`;
            }});
        </script>
    </body>
    </html>
    """
    
    estimated_width = 420
    video_height = estimated_width / aspect_ratio_decimal
    controls_height = 90
    total_height = max(500, min(700, int(video_height + controls_height)))
    
    components.html(html_code, height=total_height, scrolling=False)
    return total_height


# Example usage in Streamlit app
def main():
    st.title("Responsive Custom Video Player")
    
    # You can use a local file path or URL
    video_url = st.text_input("Enter video URL:", "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4")
    
    # Aspect ratio selection
    aspect_ratio = st.selectbox("Aspect Ratio:", ["16:9", "4:3", "21:9", "1:1"], index=0)
    
    if video_url:
        st.subheader("Responsive Custom Video Player")
        custom_video_player(video_url, aspect_ratio=aspect_ratio)
        
        st.subheader("Standard Streamlit Video (for comparison)")
        st.video(video_url)
        
        # Demo with columns to show responsiveness
        st.subheader("Responsive Demo in Columns")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("Wide column:")
            custom_video_player(video_url, aspect_ratio=aspect_ratio)
        
        with col2:
            st.write("Narrow column:")
            custom_video_player(video_url, aspect_ratio=aspect_ratio)

if __name__ == "__main__":
    main()