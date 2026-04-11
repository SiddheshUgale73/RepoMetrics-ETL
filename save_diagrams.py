import shutil
import os

images = [
    {
        "src": r"C:\Users\Sarvadnya\.gemini\antigravity\brain\f16dcc87-9ec2-412a-9895-aa7e218bbaec\system_architecture_diagram_v2_1775888084785.png",
        "dest": r"c:\Users\Sarvadnya\OneDrive\Desktop\FInalYearProject\system_architecture.png"
    },
    {
        "src": r"C:\Users\Sarvadnya\.gemini\antigravity\brain\f16dcc87-9ec2-412a-9895-aa7e218bbaec\project_workflow_diagram_1775888054227.png",
        "dest": r"c:\Users\Sarvadnya\OneDrive\Desktop\FInalYearProject\project_workflow.png"
    }
]

for img in images:
    try:
        shutil.copy(img["src"], img["dest"])
        print(f"Successfully copied to {img['dest']}")
    except Exception as e:
        print(f"Error copying {img['src']}: {e}")
