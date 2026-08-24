import asyncio
import json
import os
import random
import sys
import httpx
from datetime import datetime

# Make sure we can import from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.gemini_service import gemini_service
from sklearn.metrics import classification_report

# We'll test against a subset of diseases that our system is somewhat familiar with
# We map PlantVillage folder names to our expected ground truth labels
DISEASES_TO_TEST = {
    "Potato___Early_blight": "Early Blight",
    "Potato___Late_blight": "Late Blight",
    "Tomato___Bacterial_spot": "Bacterial Spot",
    "Corn_(maize)___Common_rust_": "Common Rust",
    "Tomato___healthy": "Healthy"
}

IMAGES_PER_CLASS = 15  # Total = 75 images (moderate smoke-test set that won't take forever)

async def fetch_image_list(client: httpx.AsyncClient, folder_name: str) -> list:
    url = f"https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/{folder_name}"
    response = await client.get(url)
    if response.status_code == 200:
        files = response.json()
        return [f["download_url"] for f in files if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))]
    print(f"Failed to fetch {folder_name}: {response.status_code}")
    return []

async def download_image(client: httpx.AsyncClient, url: str) -> bytes:
    response = await client.get(url)
    response.raise_for_status()
    return response.content

async def run_validation_suite():
    print("🌾 KrishiSathi Real Validation Suite")
    print("---------------------------------------------")
    print(f"Loading test set from PlantVillage GitHub mirror...")
    
    # We need Gemini API key for this to work
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not set. Cannot run real validation.")
        return

    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for folder_name, true_label in DISEASES_TO_TEST.items():
            print(f"\nFetching image list for {true_label}...")
            image_urls = await fetch_image_list(client, folder_name)
            
            if not image_urls:
                continue
                
            # Random sample
            sampled_urls = random.sample(image_urls, min(IMAGES_PER_CLASS, len(image_urls)))
            print(f"Testing {len(sampled_urls)} images for {true_label}...")
            
            for i, url in enumerate(sampled_urls):
                try:
                    print(f"  [{i+1}/{len(sampled_urls)}] Analyzing...")
                    image_bytes = await download_image(client, url)
                    
                    # Call the actual Gemini service
                    # Provide generic crop context based on folder name
                    crop_type = folder_name.split("___")[0].replace("_", " ")
                    
                    response = gemini_service.diagnose_crop_disease(
                        image_bytes=image_bytes,
                        crop_type=crop_type,
                        location_context={"region": "Validation Test", "climate": "Unknown"}
                    )
                    
                    pred_label = response.get("disease_name", "Unknown")
                    confidence = response.get("confidence", 0.0)
                    
                    # Normalize prediction to match ground truth classes roughly
                    # Gemini might say "Potato Early Blight", we want to see if "Early Blight" is in it
                    normalized_pred = "Unknown"
                    for known_label in DISEASES_TO_TEST.values():
                        if known_label.lower() in pred_label.lower():
                            normalized_pred = known_label
                            break
                    if normalized_pred == "Unknown" and "health" in pred_label.lower():
                        normalized_pred = "Healthy"
                    
                    results.append({
                        "true": true_label,
                        "pred": normalized_pred,
                        "raw_pred": pred_label,
                        "conf": confidence
                    })
                except Exception as e:
                    print(f"  Error on image: {e}")

    # Compute metrics
    if not results:
        print("No results to compute.")
        return
        
    y_true = [r["true"] for r in results]
    y_pred = [r["pred"] for r in results]
    
    print("\n\n" + "="*50)
    print("VALIDATION COMPLETE")
    print("="*50)
    
    report = classification_report(y_true, y_pred, zero_division=0, output_dict=True)
    text_report = classification_report(y_true, y_pred, zero_division=0)
    
    print(text_report)
    
    accuracy = report["accuracy"]
    
    # Save results
    output_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_images": len(results),
        "accuracy": accuracy,
        "metrics": report,
        "raw_results": results
    }
    
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'validation_results.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"\nSaved detailed results to {out_path}")

if __name__ == "__main__":
    asyncio.run(run_validation_suite())
