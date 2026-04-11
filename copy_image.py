import shutil
import os

source = r"C:\Users\Sarvadnya\.gemini\antigravity\brain\f16dcc87-9ec2-412a-9895-aa7e218bbaec\project_architecture_diagram_1775887666613.png"
dest = r"c:\Users\Sarvadnya\OneDrive\Desktop\FInalYearProject\project_architecture.png"

try:
    shutil.copy(source, dest)
    print(f"Successfully copied to {dest}")
except Exception as e:
    print(f"Error: {e}")
