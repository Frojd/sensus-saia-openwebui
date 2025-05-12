from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os
import re
from pathlib import Path

from open_webui.utils.auth import get_admin_user

router = APIRouter()

# Define the theme settings model
class ThemeSettings(BaseModel):
    primaryColor: str
    secondaryColor: str
    accentColor: str
    logoUrl: str = ""
    faviconUrl: str = ""

# Path to store theme settings
THEME_SETTINGS_PATH = Path("data/theme_settings.json")

# Ensure the directory exists
os.makedirs(THEME_SETTINGS_PATH.parent, exist_ok=True)

# Initialize theme settings file if it doesn't exist
if not THEME_SETTINGS_PATH.exists():
    with open(THEME_SETTINGS_PATH, "w") as f:
        json.dump({
            "primaryColor": "#3B82F6",
            "secondaryColor": "#10B981",
            "accentColor": "#8B5CF6",
            "logoUrl": "",
            "faviconUrl": ""
        }, f)

@router.get("/theme")
async def get_theme_settings():
    """Get the current theme settings"""
    try:
        with open(THEME_SETTINGS_PATH, "r") as f:
            theme_settings = json.load(f)
        return theme_settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading theme settings: {str(e)}")

@router.post("/theme")
async def save_theme_settings(
    theme_settings: ThemeSettings,
    user = Depends(get_admin_user)
):
    """Save theme settings (admin only)"""
    try:
        # Save the theme settings to the JSON file
        with open(THEME_SETTINGS_PATH, "w") as f:
            json.dump(theme_settings.dict(), f)
        
        # Import required modules for image processing
        import base64
        import re
        
        # Create a directory for theme assets if it doesn't exist
        theme_dir = Path("data/theme")
        theme_dir.mkdir(parents=True, exist_ok=True)
        
        # Function to save base64 image
        def save_base64_image(base64_url, file_prefix):
            if base64_url and base64_url.startswith('data:image'):
                # Parse the base64 string
                data_match = re.match(r'data:image/([a-zA-Z0-9]+);base64,(.+)', base64_url)
                if data_match:
                    file_type, base64_data = data_match.groups()
                    
                    # Save the image to a file
                    file_path = theme_dir / f"{file_prefix}.{file_type}"
                    with open(file_path, "wb") as image_file:
                        image_file.write(base64.b64decode(base64_data))
                    
                    # Return the API URL for the saved image
                    return f"/api/theme/{file_prefix}"
            return base64_url
        
        # Process logo if provided
        if theme_settings.logoUrl and theme_settings.logoUrl.startswith('data:image'):
            try:
                # Save logo and update URL
                file_url = save_base64_image(theme_settings.logoUrl, "logo")
                
                # Update the JSON file with the file URL
                with open(THEME_SETTINGS_PATH, "r") as f:
                    theme_data = json.load(f)
                
                theme_data["logoUrl"] = file_url
                
                with open(THEME_SETTINGS_PATH, "w") as f:
                    json.dump(theme_data, f)
            except Exception as logo_error:
                print(f"Error saving logo file: {str(logo_error)}")
                # Continue even if logo saving fails
        
        # Process favicon if provided
        if theme_settings.faviconUrl and theme_settings.faviconUrl.startswith('data:image'):
            try:
                # Save favicon and update URL
                file_url = save_base64_image(theme_settings.faviconUrl, "favicon")
                
                # Update the JSON file with the file URL
                with open(THEME_SETTINGS_PATH, "r") as f:
                    theme_data = json.load(f)
                
                theme_data["faviconUrl"] = file_url
                
                with open(THEME_SETTINGS_PATH, "w") as f:
                    json.dump(theme_data, f)
            except Exception as favicon_error:
                print(f"Error saving favicon file: {str(favicon_error)}")
                # Continue even if favicon saving fails
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving theme settings: {str(e)}")

# Serve theme CSS
@router.get("/theme.css")
async def get_theme_css():
    """Get the theme CSS for all users"""
    try:
        with open(THEME_SETTINGS_PATH, "r") as f:
            theme = json.load(f)
        
        css = f"""
        :root {{
            --primary-color: {theme.get("primaryColor", "#3B82F6")};
            --secondary-color: {theme.get("secondaryColor", "#10B981")};
            --accent-color: {theme.get("accentColor", "#8B5CF6")};
        }}
        
        /* Buttons */
        .btn-primary, 
        .bg-blue-600,
        .hover\\:bg-blue-700:hover,
        button[type="submit"],
        .bg-blue-500 {{
            background-color: var(--primary-color) !important;
        }}
        
        /* Text colors */
        .text-blue-600,
        .hover\\:text-blue-700:hover,
        .text-blue-500,
        a.text-blue-500,
        .hover\\:text-blue-500:hover {{
            color: var(--primary-color) !important;
        }}
        
        /* Border colors */
        .border-blue-600,
        .focus\\:border-blue-500:focus,
        .border-blue-500,
        .hover\\:border-blue-500:hover {{
            border-color: var(--primary-color) !important;
        }}
        
        /* Focus rings */
        .focus\\:ring-blue-500:focus,
        .focus\\:ring-blue-600:focus,
        .focus\\:ring-offset-blue-200:focus {{
            --tw-ring-color: var(--primary-color) !important;
        }}
        
        /* Secondary color elements */
        .bg-green-500,
        .hover\\:bg-green-600:hover {{
            background-color: var(--secondary-color) !important;
        }}
        
        .text-green-500,
        .hover\\:text-green-600:hover {{
            color: var(--secondary-color) !important;
        }}
        
        .border-green-500,
        .hover\\:border-green-600:hover {{
            border-color: var(--secondary-color) !important;
        }}
        
        /* Accent color elements */
        .bg-purple-500,
        .hover\\:bg-purple-600:hover,
        .bg-indigo-500,
        .hover\\:bg-indigo-600:hover {{
            background-color: var(--accent-color) !important;
        }}
        
        .text-purple-500,
        .hover\\:text-purple-600:hover,
        .text-indigo-500,
        .hover\\:text-indigo-600:hover {{
            color: var(--accent-color) !important;
        }}
        
        .border-purple-500,
        .hover\\:border-purple-600:hover,
        .border-indigo-500,
        .hover\\:border-indigo-600:hover {{
            border-color: var(--accent-color) !important;
        }}
        
        /* Progress bars and other UI elements */
        progress::-webkit-progress-value,
        .progress-bar,
        .progress-value {{
            background-color: var(--primary-color) !important;
        }}
        
        /* Selected items */
        .selected,
        .active,
        .current {{
            border-color: var(--primary-color) !important;
            background-color: color-mix(in srgb, var(--primary-color) 15%, transparent) !important;
        }}
        
        /* Checkboxes and radio buttons */
        input[type="checkbox"]:checked,
        input[type="radio"]:checked {{
            background-color: var(--primary-color) !important;
            border-color: var(--primary-color) !important;
        }}
        
        /* Links */
        a:not([class]) {{
            color: var(--primary-color);
        }}
        
        a:not([class]):hover {{
            color: color-mix(in srgb, var(--primary-color) 80%, black);
        }}
        
        /* Login page logo */
        .login-container {{
            position: relative;
        }}
        
        #login-logo {{
            max-width: 200px;
            max-height: 100px;
            margin: 0 auto;
        }}
        
        /* For browsers that don't support JavaScript */
        .auth-form::before {{
            content: '';
            display: {'' if theme.get("logoUrl") else 'none'};
            height: 100px;
            margin-bottom: 1rem;
            background-image: url('{theme.get("logoUrl", "")}');
            background-position: center;
            background-repeat: no-repeat;
            background-size: contain;
            background-origin: content-box;
            padding: 10px;
        }}
        """
        
        return Response(content=css, media_type="text/css")
    except Exception as e:
        # Return empty CSS on error
        return Response(content="", media_type="text/css")

# Helper function to serve theme images
async def serve_theme_image(image_prefix):
    """Serve a theme image (logo or favicon)"""
    try:
        # Check for image files in different formats
        theme_dir = Path("data/theme")
        for ext in ["png", "jpg", "jpeg", "svg", "gif", "webp", "ico"]:
            image_path = theme_dir / f"{image_prefix}.{ext}"
            if image_path.exists():
                # Determine the correct media type
                media_types = {
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "svg": "image/svg+xml",
                    "gif": "image/gif",
                    "webp": "image/webp",
                    "ico": "image/x-icon"
                }
                
                with open(image_path, "rb") as f:
                    image_data = f.read()
                
                return Response(
                    content=image_data, 
                    media_type=media_types.get(ext, "application/octet-stream")
                )
        
        # If no image file is found, return a 404
        raise HTTPException(status_code=404, detail=f"{image_prefix.capitalize()} not found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error serving {image_prefix}: {str(e)}")

# Serve the logo file
@router.get("/theme/logo")
async def get_theme_logo():
    """Get the theme logo"""
    return await serve_theme_image("logo")

# Serve the favicon file
@router.get("/theme/favicon")
async def get_theme_favicon():
    """Get the theme favicon"""
    return await serve_theme_image("favicon")

# Get the current favicon URL
@router.get("/theme/favicon-url")
async def get_favicon_url():
    """Get the current favicon URL"""
    try:
        if THEME_SETTINGS_PATH.exists():
            with open(THEME_SETTINGS_PATH, "r") as f:
                theme_settings = json.load(f)
                favicon_url = theme_settings.get("faviconUrl", "")
                if favicon_url:
                    return {"url": favicon_url}
        return {"url": "/static/favicon.png"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting favicon URL: {str(e)}")


# Initialize theme module
def init_theme(app):
    """Initialize the theme module"""
    return router
