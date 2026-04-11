import os

files_to_remove = [
    r"c:\Users\Sarvadnya\OneDrive\Desktop\FInalYearProject\project_architecture.png",
    r"c:\Users\Sarvadnya\OneDrive\Desktop\FInalYearProject\system_architecture.png",
    r"c:\Users\Sarvadnya\OneDrive\Desktop\FInalYearProject\project_workflow.png",
    r"c:\Users\Sarvadnya\OneDrive\Desktop\FInalYearProject\copy_image.py",
    r"c:\Users\Sarvadnya\OneDrive\Desktop\FInalYearProject\save_diagrams.py"
]

for file_path in files_to_remove:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Successfully removed {file_path}")
        else:
            print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error removing {file_path}: {e}")
