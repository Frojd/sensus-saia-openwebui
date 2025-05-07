from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
import json
import os
from pathlib import Path

from open_webui.utils.auth import get_admin_user

router = APIRouter()

# Define the theme settings model
class ThemeSettings(BaseModel):
    primaryColor: str
    secondaryColor: str
    accentColor: str
    logoUrl: str = ""

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
            "logoUrl": ""
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
        
        # If there's a base64 logo, also save it as a file
        if theme_settings.logoUrl and theme_settings.logoUrl.startswith('data:image'):
            try:
                # Extract the base64 data and file type
                import base64
                import re
                
                # Parse the base64 string
                data_match = re.match(r'data:image/([a-zA-Z0-9]+);base64,(.+)', theme_settings.logoUrl)
                if data_match:
                    file_type, base64_data = data_match.groups()
                    
                    # Create a directory for the logo if it doesn't exist
                    logo_dir = Path("data/theme")
                    logo_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save the logo to a file
                    logo_path = logo_dir / f"logo.{file_type}"
                    with open(logo_path, "wb") as logo_file:
                        logo_file.write(base64.b64decode(base64_data))
                    
                    # Update the theme settings to use the file path instead of base64
                    file_url = f"/api/theme/logo"
                    
                    # Update the JSON file with the file URL
                    with open(THEME_SETTINGS_PATH, "r") as f:
                        theme_data = json.load(f)
                    
                    theme_data["logoUrl"] = file_url
                    
                    with open(THEME_SETTINGS_PATH, "w") as f:
                        json.dump(theme_data, f)
            except Exception as logo_error:
                print(f"Error saving logo file: {str(logo_error)}")
                # Continue even if logo saving fails
        
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

# Serve the logo file
@router.get("/theme/logo")
async def get_theme_logo():
    """Get the theme logo"""
    try:
        # Check for logo files in different formats
        logo_dir = Path("data/theme")
        for ext in ["png", "jpg", "jpeg", "svg", "gif", "webp"]:
            logo_path = logo_dir / f"logo.{ext}"
            if logo_path.exists():
                # Determine the correct media type
                media_types = {
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "svg": "image/svg+xml",
                    "gif": "image/gif",
                    "webp": "image/webp"
                }
                
                with open(logo_path, "rb") as f:
                    logo_data = f.read()
                
                return Response(
                    content=logo_data, 
                    media_type=media_types.get(ext, "application/octet-stream")
                )
        
        # If no logo file is found, return a 404
        raise HTTPException(status_code=404, detail="Logo not found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error serving logo: {str(e)}")
