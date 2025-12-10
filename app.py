"""
批量圖片文字浮水印工具（升級版）
使用 Streamlit 和 Pillow 實現批量圖片浮水印添加功能
支援即時預覽、全版鋪滿、透明度、旋轉等功能
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io
import zipfile
from datetime import datetime
import os
import math

# 設定頁面配置
st.set_page_config(
    page_title="批量圖片浮水印工具",
    page_icon="💧",
    layout="wide"
)

# 初始化 session_state
if 'preview_image' not in st.session_state:
    st.session_state.preview_image = None
if 'original_image' not in st.session_state:
    st.session_state.original_image = None


def load_font(font_size, font_path=None):
    """
    載入字體
    
    參數:
        font_size: 字體大小
        font_path: 字體檔案路徑（可選，如果提供則優先使用）
    
    返回:
        font: PIL ImageFont 物件
    """
    try:
        # 如果提供了字體路徑，優先使用
        if font_path and os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                return font
            except:
                # 如果載入失敗，繼續嘗試系統字體
                pass
        
        # 嘗試使用系統字體（Windows 常見路徑）
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",  # 微軟雅黑
            "C:/Windows/Fonts/simhei.ttf",  # 黑體
            "C:/Windows/Fonts/arial.ttf",  # Arial
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, font_size)
                    break
                except:
                    continue
        
        # 如果找不到字體，使用預設字體
        if font is None:
            font = ImageFont.load_default()
    except:
        # 如果載入字體失敗，使用預設字體
        font = ImageFont.load_default()
    
    return font


def calculate_position(img_width, img_height, text_width, text_height, position_key):
    """
    根據選擇的位置計算浮水印的座標
    
    參數:
        img_width: 圖片寬度
        img_height: 圖片高度
        text_width: 文字寬度
        text_height: 文字高度
        position_key: 位置鍵值（bottom_right, bottom_left, top_right, top_left, center）
    
    返回:
        (x, y): 浮水印文字的左上角座標
    """
    padding = 20  # 距離邊緣的間距
    
    if position_key == "bottom_right":
        x = img_width - text_width - padding
        y = img_height - text_height - padding
    elif position_key == "bottom_left":
        x = padding
        y = img_height - text_height - padding
    elif position_key == "top_right":
        x = img_width - text_width - padding
        y = padding
    elif position_key == "top_left":
        x = padding
        y = padding
    elif position_key == "center":
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
    else:
        # 預設為右下角
        x = img_width - text_width - padding
        y = img_height - text_height - padding
    
    return (x, y)


def create_text_image(text, font, color_rgb, opacity_value, rotation_angle):
    """
    創建帶有旋轉和透明度的文字圖片
    
    參數:
        text: 文字內容
        font: PIL ImageFont 物件
        color_rgb: RGB 顏色元組
        opacity_value: 透明度值（0-255）
        rotation_angle: 旋轉角度（-180 到 180 度，負數為逆時針，正數為順時針）
    
    返回:
        rotated_text_img: 旋轉後的文字圖片（RGBA 模式）
    """
    # 創建一個臨時繪圖物件來測量文字大小
    temp_img = Image.new('RGBA', (1000, 1000), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # 創建文字圖片（RGBA 模式以支援透明度）
    text_img = Image.new('RGBA', (int(text_width * 1.5), int(text_height * 1.5)), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)
    
    # 計算文字在圖片中的位置（置中）
    text_x = (text_img.width - text_width) // 2
    text_y = (text_img.height - text_height) // 2
    
    # 繪製文字（使用 RGBA 顏色）
    text_draw.text(
        (text_x, text_y),
        text,
        fill=(color_rgb[0], color_rgb[1], color_rgb[2], opacity_value),
        font=font
    )
    
    # 旋轉文字圖片
    if rotation_angle != 0:
        rotated_text_img = text_img.rotate(rotation_angle, expand=True, fillcolor=(0, 0, 0, 0))
    else:
        rotated_text_img = text_img
    
    return rotated_text_img


def add_single_watermark(image, text, font_size, color, opacity_value, rotation_angle, position_key, font_path=None):
    """
    在圖片上添加單一文字浮水印
    
    參數:
        image: PIL Image 物件
        text: 浮水印文字
        font_size: 字體大小
        color: 文字顏色（十六進制字串，如 "#FFFFFF"）
        opacity_value: 透明度值（0-255）
        rotation_angle: 旋轉角度（-180 到 180 度，負數為逆時針，正數為順時針）
        position_key: 位置鍵值
        font_path: 字體檔案路徑（可選）
    
    返回:
        處理後的 PIL Image 物件
    """
    # 創建一個可繪製的圖片副本（轉換為 RGBA 以支援透明度）
    if image.mode != 'RGBA':
        img_with_watermark = image.convert('RGBA')
    else:
        img_with_watermark = image.copy()
    
    # 載入字體
    font = load_font(font_size, font_path)
    
    # 將十六進制顏色轉換為 RGB
    color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    
    # 創建旋轉後的文字圖片
    rotated_text_img = create_text_image(text, font, color_rgb, opacity_value, rotation_angle)
    
    # 計算浮水印位置
    img_width, img_height = img_with_watermark.size
    text_width, text_height = rotated_text_img.size
    
    x, y = calculate_position(img_width, img_height, text_width, text_height, position_key)
    
    # 確保座標在圖片範圍內
    x = max(0, min(x, img_width - text_width))
    y = max(0, min(y, img_height - text_height))
    
    # 將文字圖片貼到主圖片上（使用 alpha 合成）
    img_with_watermark.paste(rotated_text_img, (x, y), rotated_text_img)
    
    # 轉換回 RGB 模式（如果原始圖片是 RGB）
    if image.mode == 'RGB':
        rgb_img = Image.new('RGB', img_with_watermark.size, (255, 255, 255))
        rgb_img.paste(img_with_watermark, mask=img_with_watermark.split()[3])
        return rgb_img
    
    return img_with_watermark


def add_tiled_watermark(image, text, font_size, color, opacity_value, rotation_angle, density, font_path=None):
    """
    在圖片上添加全版鋪滿的文字浮水印
    
    參數:
        image: PIL Image 物件
        text: 浮水印文字
        font_size: 字體大小
        color: 文字顏色（十六進制字串，如 "#FFFFFF"）
        opacity_value: 透明度值（0-255）
        rotation_angle: 旋轉角度（-180 到 180 度，負數為逆時針，正數為順時針）
        density: 間距密度（200-1000，數值越大間距越大）
        font_path: 字體檔案路徑（可選）
    
    返回:
        處理後的 PIL Image 物件
    """
    # 創建一個可繪製的圖片副本（轉換為 RGBA 以支援透明度）
    if image.mode != 'RGBA':
        img_with_watermark = image.convert('RGBA')
    else:
        img_with_watermark = image.copy()
    
    # 載入字體
    font = load_font(font_size, font_path)
    
    # 將十六進制顏色轉換為 RGB
    color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    
    # 創建旋轉後的文字圖片
    rotated_text_img = create_text_image(text, font, color_rgb, opacity_value, rotation_angle)
    
    # 計算間距（density 越大，間距越大）
    # density 100 對應字體大小的 1.5 倍間距
    spacing_x = int(font_size * (density / 100) * 1.5)
    spacing_y = int(font_size * (density / 100) * 1.5)
    
    text_width, text_height = rotated_text_img.size
    
    # 使用雙層迴圈鋪滿整張圖片
    img_width, img_height = img_with_watermark.size
    
    # 從左上角開始，以間距為步長鋪滿
    y = 0
    while y < img_height + text_height:
        x = 0
        # 交錯排列：偶數行正常，奇數行偏移一半間距
        row_offset = (spacing_x // 2) if ((y // spacing_y) % 2 == 1) else 0
        x = -row_offset
        
        while x < img_width + text_width:
            # 將文字圖片貼到主圖片上
            img_with_watermark.paste(rotated_text_img, (int(x), int(y)), rotated_text_img)
            x += spacing_x
        y += spacing_y
    
    # 轉換回 RGB 模式（如果原始圖片是 RGB）
    if image.mode == 'RGB':
        rgb_img = Image.new('RGB', img_with_watermark.size, (255, 255, 255))
        rgb_img.paste(img_with_watermark, mask=img_with_watermark.split()[3])
        return rgb_img
    
    return img_with_watermark


def add_watermark(image, text, font_size, color, opacity_value, rotation_angle, mode, position_key=None, density=None, font_path=None):
    """
    在圖片上添加浮水印（統一入口函數）
    
    參數:
        image: PIL Image 物件
        text: 浮水印文字
        font_size: 字體大小
        color: 文字顏色（十六進制字串）
        opacity_value: 透明度值（0-255）
        rotation_angle: 旋轉角度（-180 到 180 度，負數為逆時針，正數為順時針）
        mode: 模式（"單一浮水印" 或 "全版鋪滿 (Tiled)"）
        position_key: 位置鍵值（僅單一模式需要）
        density: 間距密度（僅全版模式需要）
        font_path: 字體檔案路徑（可選）
    
    返回:
        處理後的 PIL Image 物件
    """
    if mode == "單一浮水印":
        return add_single_watermark(image, text, font_size, color, opacity_value, rotation_angle, position_key, font_path)
    else:
        return add_tiled_watermark(image, text, font_size, color, opacity_value, rotation_angle, density, font_path)


def process_images(uploaded_files, watermark_text, font_size, text_color, opacity_value, rotation_angle, mode, position_key=None, density=None, font_path=None):
    """
    批量處理圖片，添加浮水印
    
    參數:
        uploaded_files: 上傳的檔案列表
        watermark_text: 浮水印文字
        font_size: 字體大小
        text_color: 文字顏色
        opacity_value: 透明度值（0-255）
        rotation_angle: 旋轉角度（-180 到 180 度，負數為逆時針，正數為順時針）
        mode: 模式
        position_key: 位置鍵值（僅單一模式需要）
        density: 間距密度（僅全版模式需要）
        font_path: 字體檔案路徑（可選）
    
    返回:
        processed_images: 處理後的圖片字典 {檔名: PIL Image}
    """
    processed_images = {}
    
    # 進度條
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(uploaded_files)
    
    for idx, uploaded_file in enumerate(uploaded_files):
        try:
            # 更新進度
            progress = (idx + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"正在處理: {uploaded_file.name} ({idx + 1}/{total_files})")
            
            # 讀取圖片
            image = Image.open(io.BytesIO(uploaded_file.read()))
            
            # 如果是 RGBA 模式，轉換為 RGB（避免某些格式問題）
            if image.mode == 'RGBA':
                # 創建白色背景
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])  # 使用 alpha 通道作為遮罩
                image = rgb_image
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 添加浮水印
            watermarked_image = add_watermark(
                image, watermark_text, font_size, text_color,
                opacity_value, rotation_angle, mode, position_key, density, font_path
            )
            
            # 儲存處理後的圖片
            processed_images[uploaded_file.name] = watermarked_image
            
        except Exception as e:
            st.error(f"處理 {uploaded_file.name} 時發生錯誤: {str(e)}")
            continue
    
    # 完成進度條
    progress_bar.progress(1.0)
    status_text.text("處理完成！")
    
    return processed_images


def create_zip_file(processed_images):
    """
    將處理後的圖片打包成 ZIP 檔案
    
    參數:
        processed_images: 處理後的圖片字典 {檔名: PIL Image}
    
    返回:
        zip_buffer: ZIP 檔案的 BytesIO 物件
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, image in processed_images.items():
            # 將圖片轉換為位元組
            img_buffer = io.BytesIO()
            
            # 根據原始檔名決定儲存格式
            if filename.lower().endswith('.png'):
                image.save(img_buffer, format='PNG')
                ext = '.png'
            else:
                image.save(img_buffer, format='JPEG', quality=95)
                ext = '.jpg'
            
            # 生成新的檔名（添加 _watermarked 後綴）
            base_name = os.path.splitext(filename)[0]
            new_filename = f"{base_name}_watermarked{ext}"
            
            # 將圖片寫入 ZIP
            zip_file.writestr(new_filename, img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer


def update_preview(watermark_text, font_size, text_color, opacity, rotation_angle, watermark_mode, position=None, density=None, font_path=None):
    """
    更新預覽圖片
    當側邊欄參數改變時，即時更新預覽圖
    
    參數:
        watermark_text: 浮水印文字
        font_size: 字體大小
        text_color: 文字顏色
        opacity: 透明度（0-100%）
        rotation_angle: 旋轉角度（-180 到 180 度）
        watermark_mode: 模式
        position: 位置（僅單一模式）
        density: 間距（僅全版模式）
        font_path: 字體檔案路徑（可選）
    
    返回:
        預覽圖片或 None
    """
    if st.session_state.original_image is None:
        return None
    
    # 轉換透明度（0-100% 轉換為 0-255）
    opacity_value = int(opacity * 255 / 100)
    
    # 獲取位置或間距
    if watermark_mode == "單一浮水印":
        position_options = {
            "右下角": "bottom_right",
            "左下角": "bottom_left",
            "右上角": "top_right",
            "左上角": "top_left",
            "置中": "center"
        }
        position_key = position_options.get(position, "bottom_right")
        density = None
    else:
        # 全版鋪滿模式：確保 density 有值
        position_key = None
        if density is None:
            density = 400  # 預設值
    
    # 添加浮水印
    try:
        preview_image = add_watermark(
            st.session_state.original_image.copy(),
            watermark_text,
            font_size,
            text_color,
            opacity_value,
            rotation_angle,
            watermark_mode,
            position_key,
            density,
            font_path
        )
        return preview_image
    except Exception as e:
        st.error(f"預覽更新失敗: {str(e)}")
        return None


# 主程式邏輯
def main():
    # 標題
    st.title("💧 極速批量圖片浮水印工具")
    st.markdown("---")
    
    # 側邊欄設定區
    with st.sidebar:
        st.header("⚙️ 浮水印設定")
        
        # 模式選擇
        watermark_mode = st.radio(
            "浮水印模式",
            options=["單一浮水印", "全版鋪滿 (Tiled)"],
            index=0,
            help="選擇浮水印的顯示模式"
        )
        
        # 浮水印文字輸入
        watermark_text = st.text_input(
            "浮水印文字",
            value="浮水印",
            help="輸入要顯示在圖片上的文字"
        )
        
        # --- 字體選擇器 (精選版) ---
        font_options = {
            # === 中文精選 ===
            "中文 - 標準黑體 (Noto Sans Regular)": "fonts/NotoSansTC-Regular.ttf",
            "中文 - 粗黑體 (Noto Sans Bold)": "fonts/NotoSansTC-Bold.ttf",
            "中文 - 特粗黑體 (Noto Sans Black)": "fonts/NotoSansTC-Black.ttf",
            "中文 - 優雅宋體 (Noto Serif Regular)": "fonts/NotoSerifTC-Regular.ttf",
            "中文 - 粗宋體 (Noto Serif Bold)": "fonts/NotoSerifTC-Bold.ttf",
            "中文 - 志莽行書 (書法風格)": "fonts/ZhiMangXing-Regular.ttf",
            
            # === 英文精選 (Modern) ===
            "EN - Modern (Montserrat Regular)": "fonts/Montserrat-Regular.ttf",
            "EN - Modern Bold (Montserrat Bold)": "fonts/Montserrat-Bold.ttf",
            "EN - Modern Heavy (Montserrat ExtraBold)": "fonts/Montserrat-ExtraBold.ttf",
            
            # === 英文精選 (Elegant) ===
            "EN - Elegant (Playfair Regular)": "fonts/PlayfairDisplay-Regular.ttf",
            "EN - Elegant Italic (Playfair Italic)": "fonts/PlayfairDisplay-Italic.ttf",
            "EN - Elegant Bold (Playfair Bold)": "fonts/PlayfairDisplay-Bold.ttf",
            
            # === 英文精選 (Creative) ===
            "EN - Handwriting (Dancing Script)": "fonts/DancingScript-Regular.ttf",
            "EN - Signature (Great Vibes)": "fonts/GreatVibes-Regular.ttf",
            "EN - Street Style (Bebas Neue)": "fonts/BebasNeue-Regular.ttf"
        }
        
        selected_font_name = st.selectbox(
            "字體選擇",
            options=list(font_options.keys()),
            index=0,
            help="選擇浮水印文字的字體"
        )
        selected_font_path = font_options[selected_font_name]
        
        # 字體大小設定
        font_size = st.slider(
            "字體大小",
            min_value=10,
            max_value=200,
            value=50,
            step=5,
            help="調整浮水印文字的大小"
        )
        
        # 顏色選擇器
        text_color = st.color_picker(
            "文字顏色",
            value="#FFFFFF",
            help="選擇浮水印文字的顏色"
        )
        
        # 透明度設定（0-100%）
        opacity = st.slider(
            "透明度",
            min_value=0,
            max_value=100,
            value=100,
            step=5,
            help="調整浮水印的透明度（0% 為完全透明，100% 為完全不透明）"
        )
        
        # 旋轉角度設定
        rotation_angle = st.slider(
            "旋轉角度",
            min_value=-180,
            max_value=180,
            value=0,
            step=15,
            help="調整浮水印文字的旋轉角度（-180 到 180 度，負數為逆時針，正數為順時針）"
        )
        
        # 初始化變數
        density = None
        position = None
        
        # 如果是全版鋪滿模式，顯示間距設定
        if watermark_mode == "全版鋪滿 (Tiled)":
            density = st.slider(
                "間距 (Density)",
                min_value=200,
                max_value=1000,
                value=400,
                step=50,
                help="控制文字之間的疏密程度（數值越大，間距越大）"
            )
        else:
            # 單一浮水印模式：顯示位置選擇
            position_options = {
                "右下角": "bottom_right",
                "左下角": "bottom_left",
                "右上角": "top_right",
                "左上角": "top_left",
                "置中": "center"
            }
            
            position = st.selectbox(
                "浮水印位置",
                options=list(position_options.keys()),
                index=0,
                help="選擇浮水印在圖片上的位置"
            )
        
        st.markdown("---")
        st.markdown("### 📝 使用說明")
        st.markdown("""
        1. 上傳多張圖片（支援 JPG、PNG 格式）
        2. 在側邊欄設定浮水印參數
        3. 即時預覽第一張圖片的浮水印效果
        4. 調整滿意後，點擊「開始批量處理」按鈕
        5. 處理完成後下載 ZIP 檔案
        """)

        # Buy Me a Coffee 按鈕
        st.markdown(
            """
            <a href="https://buymeacoffee.com/shin91723y" target="_blank">
                <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" height="45">
            </a>
            """,
            unsafe_allow_html=True,
        )
    
    # 檔案上傳區
    st.subheader("📤 上傳圖片")
    uploaded_files = st.file_uploader(
        "選擇圖片檔案",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="支援 JPG、PNG 格式，可同時上傳多張圖片",
        key="file_uploader"
    )
    
    # 如果沒有上傳檔案，清除預覽
    if not uploaded_files:
        st.session_state.original_image = None
        st.session_state.preview_file_name = None
    
    # 處理上傳的檔案
    if uploaded_files:
        st.success(f"已上傳 {len(uploaded_files)} 張圖片")
        
        # 檢查是否需要更新預覽圖片（當檔案改變時）
        current_first_file_name = uploaded_files[0].name if uploaded_files else None
        stored_file_name = st.session_state.get('preview_file_name', None)
        
        # 如果檔案改變了，重新讀取第一張圖片
        if current_first_file_name != stored_file_name or st.session_state.original_image is None:
            try:
                first_file = uploaded_files[0]
                # 重置檔案指標（因為可能已經被讀取過）
                first_file.seek(0)
                first_image = Image.open(io.BytesIO(first_file.read()))
                
                # 如果是 RGBA 模式，轉換為 RGB
                if first_image.mode == 'RGBA':
                    rgb_image = Image.new('RGB', first_image.size, (255, 255, 255))
                    rgb_image.paste(first_image, mask=first_image.split()[3])
                    first_image = rgb_image
                elif first_image.mode != 'RGB':
                    first_image = first_image.convert('RGB')
                
                # 儲存原始圖片到 session_state
                st.session_state.original_image = first_image.copy()
                st.session_state.preview_file_name = current_first_file_name
                
            except Exception as e:
                st.error(f"讀取圖片失敗: {str(e)}")
                st.session_state.original_image = None
        
        # 顯示上傳的檔案列表
        with st.expander("查看上傳的檔案"):
            for file in uploaded_files:
                st.write(f"📷 {file.name} ({file.size / 1024:.2f} KB)")
    
    st.markdown("---")
    
    # 預覽區域
    if st.session_state.original_image is not None:
        st.subheader("👁️ 即時預覽")
        st.caption("調整側邊欄參數即可即時查看浮水印效果")
        
        # 更新預覽圖（直接使用側邊欄的變數值）
        if watermark_mode == "單一浮水印":
            preview_image = update_preview(
                watermark_text, font_size, text_color, opacity,
                rotation_angle, watermark_mode, position=position, font_path=selected_font_path
            )
        else:
            preview_image = update_preview(
                watermark_text, font_size, text_color, opacity,
                rotation_angle, watermark_mode, density=density, font_path=selected_font_path
            )
        
        if preview_image:
            # 顯示預覽圖
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**原始圖片**")
                st.image(st.session_state.original_image, use_container_width=True)
            
            with col2:
                st.markdown("**浮水印預覽**")
                st.image(preview_image, use_container_width=True)
        
        st.markdown("---")
    
    # 處理按鈕
    if st.button("🚀 開始批量處理", type="primary", use_container_width=True):
        # 驗證輸入
        if not uploaded_files:
            st.error("❌ 請先上傳至少一張圖片！")
            return
        
        if not watermark_text.strip():
            st.error("❌ 請輸入浮水印文字！")
            return
        
        # 轉換透明度（0-100% 轉換為 0-255）
        opacity_value = int(opacity * 255 / 100)
        
        # 獲取位置或間距
        if watermark_mode == "單一浮水印":
            position_options = {
                "右下角": "bottom_right",
                "左下角": "bottom_left",
                "右上角": "top_right",
                "左上角": "top_left",
                "置中": "center"
            }
            position_key = position_options.get(position, "bottom_right")
            density = None
        else:
            # 全版鋪滿模式：確保 density 有值
            position_key = None
            if density is None:
                density = 400  # 預設值
        
        # 批量處理圖片
        with st.spinner("正在處理圖片，請稍候..."):
            processed_images = process_images(
                uploaded_files,
                watermark_text,
                font_size,
                text_color,
                opacity_value,
                rotation_angle,
                watermark_mode,
                position_key,
                density,
                selected_font_path
            )
        
        # 如果處理成功，創建 ZIP 檔案
        if processed_images:
            st.success(f"✅ 成功處理 {len(processed_images)} 張圖片！")
            
            # 創建 ZIP 檔案
            zip_buffer = create_zip_file(processed_images)
            
            # 生成下載檔名（包含時間戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"watermarked_images_{timestamp}.zip"
            
            # 下載按鈕
            st.download_button(
                label="📥 下載 ZIP 檔案",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )

    # Footer
    st.markdown(
        """
        <div style="text-align:center; margin-top: 2rem;">
            Made with ❤️ by Astrid | 關注我的
            <a href="https://www.instagram.com/_astrid.slowly/" target="_blank">Instagram</a>
            和
            <a href="https://www.threads.com/@_astrid.slowly" target="_blank">Threads</a>
            獲取更多實用工具
        </div>
        """,
        unsafe_allow_html=True,
    )


# 執行主程式
if __name__ == "__main__":
    main()
