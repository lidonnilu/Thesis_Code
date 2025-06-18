import json
import csv
import glob
import os
import zipfile
import io
import subprocess
from datetime import datetime

# Field mapping from eLab JSON to NOMAD schema
FIELD_MAPPING = {
    "Chamber": "room",
    "Sample": "id_item_processed",
    "Target": "target_material",
    "Thickness": "thickness_measured",
    "Target 2": "target_material_2",
    "Thickness 2": "thickness_measured_2",
    "Buffer gas": "buffer_gas",
    "Process pressure ": "chamber_pressure",
    "Heater temperature": "temperature_target",
    "Heater-target distance": "heater_target_distance",
    "Repetition rate": "repetition_rate",
    "Laser Fluence": "exposure_intensity"
}

def extract_and_map_data(input_json, pid=None, affiliation=None):
    """
    This function extracts and transforms data from the original JSON to fit the NOMAD schema.
    Handles simple fields, cross-references and file attachments.
    Accepts optional PID and affiliation parameters.
    """
    item = input_json["data"][0]
    metadata_fields = item["metadata_decoded"]["extra_fields"]
    item_links = item.get("items_links", [])

    # Map element IDs to their titles
    entity_map = {i["entityid"]: i["title"] for i in item_links}

    mapped_data = {
        "m_def": "nomad_plugin_pld_moda.schema_packages.pld_schema.PLDProcess"
    }

    # Mapping of main fields
    for json_key, archive_key in FIELD_MAPPING.items():
        field = metadata_fields.get(json_key, {})
        
        # Managing references to other elements
        if field.get("type") == "items" and isinstance(field.get("value"), int):
            entity_id = field["value"]
            title = entity_map.get(entity_id)
            if title:
                mapped_data[archive_key] = title
        else:
            # Numeric value conversion and string cleanup
            value = field.get("value", "").strip()
            if value:
                try:
                    num_value = float(value)
                    mapped_data[archive_key] = int(num_value) if num_value.is_integer() else num_value
                except ValueError:
                    mapped_data[archive_key] = value

    # Added interactive fields for pid and affiliation
    if pid is not None:
        mapped_data["id_proposal"] = pid
    if affiliation is not None:
        mapped_data["affiliation"] = affiliation

    # Add operator and datetime entries after exposure_intensity
    changelog = item.get("changelog", [])
    operator = ""
    datetime_str = ""
    
    if changelog:
        first_change = changelog[0]
        operator = first_change.get("fullname", "")
        created_at = first_change.get("created_at", "")
        try:
            dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            datetime_str = dt.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            datetime_str = created_at  # Keep original format in case of error

    mapped_data["operator"] = operator
    mapped_data["datetime"] = datetime_str
    mapped_data["notes"] = item.get("body", "").strip()  # Adding notes from the body field of the json file exported from eLab

    # RHEED Image Management
    rheed_images = [
        {"image_name": f"Immagine {i+1}", "image_file": upload["real_name"]}
        for i, upload in enumerate(item.get("uploads", []))
        if upload.get("real_name", "").lower().endswith(".png")
    ]

    if rheed_images:
        mapped_data["rheed_data_images"] = rheed_images

    # RHEED data file detection
    has_rheed_txt = any(
        upload.get("real_name", "").startswith("Real-time-Region-Analysis-Peak") 
        and upload.get("real_name", "").lower().endswith(".txt")
        for upload in item.get("uploads", [])
    )

    if has_rheed_txt:
        mapped_data["rheed_intensity_plot"] = {
            "data_file": "RHEED_measurements.csv"
        }

    return {"data": mapped_data}

def convert_rheed_txt_to_csv():
    """
    Converts RHEED data TXT file to CSV format while keeping it in memory.
    Returns CSV data as a string or None if no file is found.
    """
    matching_files = glob.glob("*Real-time-Region-Analysis-Peak*.txt")
    if not matching_files:
        print("No RHEED TXT files found.")
        return None
    
    input_file = matching_files[0]
    
    # In-memory CSV creation
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["time", "intensity_11", "intensity_00", "intensity_1m1"])
    
    with open(input_file, "r") as infile:
        reader = csv.reader(infile, delimiter="\t")
        for row in reader:
            writer.writerow(row)
    
    csv_data = output.getvalue()
    output.close()
    
    print(f"File '{input_file}' converted to CSV data in memory.")
    return csv_data

def create_zip(entry_name, json_data, csv_data):
    """
    Create the ZIP archive containing:
    - The main ARCHIVE.JSON file
    - The RHEED data CSV file (if present)
    - All PNG images in the current folder
    """
    zip_filename = f"{entry_name}.zip"
    png_files = glob.glob("*.png")
    png_count = len(png_files)
    
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        # Adding JSON to ZIP
        zipf.writestr(f"{entry_name}.archive.json", json_data)
        
        # Add CSV if available
        if csv_data:
            zipf.writestr("RHEED_measurements.csv", csv_data)
        
        # Add PNG images                                    
        for png_file in png_files:
            if os.path.exists(png_file):
                zipf.write(png_file)
    
    # Print summary of zip file contents
    print(f"\nComplete archive created: {zip_filename}")
    print("Content:")
    print(f"- {entry_name}.archive.json")
    if csv_data:
        print("- RHEED_measurements.csv")
    print(f"- {png_count} PNG images" if png_count > 0 else "- no PNG images")
    
    return zip_filename

def send_to_nomad(zip_filename):
    """
    Send the ZIP archive to NOMAD using cURL
    Handles errors and displays server feedback
    """
    try:
        print(f"\nSending {zip_filename} to NOMAD...")
        result = subprocess.run(
            [
                'curl',
                '-X', 'POST',
                'http://localhost:8000/fairdi/nomad/latest/api/v1/uploads?token=N45FBTMzTZmBr7IKeNXV9w.QUeIbGA0e_30HHBs-Rp4YA270xs',
                '-T', zip_filename
            ],
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ Upload completed successfully!")
        print("Response from the server:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("✗ Error while uploading:")
        print("Error code:", e.returncode)
        print("Error output:", e.stderr)
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")

def main():
    """
    Main flow of the program:
    1. Requires the entry name, if you want to enter a proposal ID and affiliation
    2. Process JSON file
    3. Generate data for the archive
    4. Create the ZIP
    5. Offers option for upload
    """
    entry_name = input("Enter the name of the NOMAD entry: ").strip()
    
    # Search for the input JSON file within the current folder
    json_files = glob.glob("*.json")
    if not json_files:
        print("No JSON files found in the current folder.")
        return

    # JSON Reading and Processing
    with open(json_files[0], "r", encoding="utf-8") as file:
        input_json = json.load(file)
    
    # PID request
    pid = None
    pid_choice = input("Do you want to enter a proposal ID (PID)? (y/n) ").strip().lower()
    if pid_choice == 'y':
        while True:
            try:
                pid = int(input("Enter PID: "))
                break
            except ValueError:
                print("Error: please enter a valid number")

    # Affiliation Request
    print("\nSelect affiliation:")
    print("1 NFFA-DI")
    print("2 iENTRANCE@ENL")
    print("3 No affiliation")
    aff_choice = input("Choice: ").strip()
    affiliation = "NFFA-DI" if aff_choice == '1' else "iENTRANCE@ENL" if aff_choice == '2' else None

    mapped_data = extract_and_map_data(input_json, pid, affiliation)
    json_data = json.dumps(mapped_data, indent=4, ensure_ascii=False)


    # RHEED Data Conversion
    csv_data = convert_rheed_txt_to_csv()
    
    # ZIP archive creation
    zip_filename = create_zip(entry_name, json_data, csv_data)
    
    # Upload choice
    choice = input("\nDo you want to automatically send your data to NOMAD?? (y/n) ").lower()
    if choice == 'y':
        send_to_nomad(zip_filename)
    else:
        print("\nOperation completed. The ZIP file has been saved in the current folder.")

if __name__ == "__main__":
    main()
