from Sign_processing.Map_extractor import MapExtractor, ORB_maps
from pathlib import Path
from Sign_processing.Sign_extractor import Sign_extractor_class
from Sign_processing.cnn import CNNPredictor
import csv

if __name__ == "__main__":

    output_dir_maps=Path( "Outputs/Output_from_Map_extractor")
    output_dir_sign= Path("Outputs/Output_from_Sign_extractor")
    APV_plan_GDPR_trygg= "APV_plan_GDPR_trygg/AP22222-gdpr fixed AF Gruppen.pdf"

    Orb = ORB_maps (nfeatures=20000,  ratio=0.75,min_good=12000)
    Maps= MapExtractor (orb_matcher = Orb,  output_dir= output_dir_maps)
    Maps.pdf_To_image (APV_plan_GDPR_trygg)
    Files_sorted =sorted( output_dir_maps.glob("page_*.jpg"),
                         key= lambda p: int(p.stem.split("_") [1]) )
    for image_path in Files_sorted:
        sign_extractor = Sign_extractor_class(image_path=image_path, output_dir=output_dir_sign)
        sign_extractor.extract_signs()
    
    model_path = Path("Sign_processing/demo/cnn.pth")
    classes_path = Path("Sign_processing/demo/classes.json")
    predictor = CNNPredictor(model_path, classes_path)
    
    # Loop through all signs and save results to CSV
    results = []
    sign_files = sorted(output_dir_sign.glob("*.png"))
    
    for sign_path in sign_files:
        print(f"Processing {sign_path.name}...")
        prediction_results = predictor.predict(str(sign_path))
        if prediction_results:
            top_class, top_prob = prediction_results[0]
            results.append({
                'filename': sign_path.name,
                'predicted_class': top_class,
                'confidence': top_prob
            })
    
    # Save results to CSV
    csv_output = Path("Outputs/sign_predictions.csv")
    with open(csv_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'predicted_class', 'confidence'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults saved to {csv_output}")
    