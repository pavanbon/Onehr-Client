import shutil
import os
import zipfile

def create_deployment_package():
    # Source filenames
    lambda_file = "lambda_function.py"
    package_dir = "package"
    zip_filename = "OneHR_API_Fixed_Final_v2.zip"

    # Verify sources exist
    if not os.path.exists(lambda_file):
        print(f"Error: {lambda_file} not found.")
        return
    if not os.path.exists(package_dir):
        print(f"Error: {package_dir} directory not found.")
        return

    print(f"Creating {zip_filename}...")
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Add all dependencies from 'package' directory
            print("Adding dependencies...")
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Archive name should be relative to 'package' so they end up at root of zip
                    arcname = os.path.relpath(file_path, package_dir)
                    zipf.write(file_path, arcname)

            # 2. Add lambda_function.py to root of zip
            print("Adding lambda_function.py...")
            zipf.write(lambda_file, arcname="lambda_function.py")

        print(f"SUCCESS: {zip_filename} created.")

    except Exception as e:
        print(f"Failed to create zip: {e}")

if __name__ == "__main__":
    create_deployment_package()
