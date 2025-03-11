import pandas as pd

def load_captions_from_xlsx(file_path):
    """
    Load captions data from an XLSX file and convert each row to a dictionary.
    
    Args:
        file_path (str): Path to the XLSX file
        
    Returns:
        list: List of dictionaries, where each dictionary represents a row with the specified keys
    """
    # Read the Excel file
    df = pd.read_excel(file_path, engine='openpyxl')
    
    # Print the actual column names to help with debugging
    print("Actual columns in the file:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
    
    # Try to map columns based on content rather than exact names
    # This is a best guess approach based on the example you provided
    result = []
    
    for _, row in df.iterrows():
        caption_dict = {}
        
        # Directly map simple columns if they exist
        if 'content_id' in df.columns:
            caption_dict['content_id'] = row['content_id']
        if 'stock_url' in df.columns:
            caption_dict['stock_url'] = row['stock_url']
        
        # For other columns, try to find them based on partial matches
        for col in df.columns:
            col_lower = col.lower()
            if 'summary' in col_lower or 'what is the video about' in col_lower:
                caption_dict['summary_caption'] = row[col]
            elif ('subject' in col_lower and 'background' in col_lower) or 'who or what is in the image' in col_lower:
                caption_dict['subject_background_caption'] = row[col]
            elif ('subject' in col_lower and 'action' in col_lower) or 'what are they doing' in col_lower:
                caption_dict['subject_motion_caption'] = row[col]
            elif 'camera' in col_lower or 'how is it captured' in col_lower:
                caption_dict['camera_caption'] = row[col]
        
        result.append(caption_dict)
    
    return result

def main():
    # Example usage
    # file_path = 'adobe_2_19.xlsx'  # Replace with your actual file path
    file_paths = ['adobe_2_19.xlsx', 'adobe_2_17.xlsx']
    captions_data = []
    for file_path in file_paths:
        captions_data.extend(load_captions_from_xlsx(file_path))
    
    print(f"\nTotal records loaded: {len(captions_data)}")
    
    from feedback_app import load_video_data, parse_args
    args = parse_args()
    
    # Load video data
    video_data_dict = load_video_data(args.video_data, label_collections=args.label_collections)
    
    # find overlap between video_data_dict and captions_data
    video_names = set(video_data_dict.keys()) 
    # only keep file name
    video_names = set([name.split('/')[-1] for name in video_names])
    stock_names = set([caption['stock_url'].split('/')[-1] for caption in captions_data])
    overlap = video_names.intersection(stock_names)
    print(f"Overlap between video data and captions: {len(overlap)}")
    
    # Video that are not in the caption data
    missing = video_names - overlap
    print(f"Videos that we have but not in Adobe data: {len(missing)}")
    
    # Videos that are not in the video data
    missing_video_data = stock_names - overlap
    print(f"Videos that Adobe has but not in our data: {len(missing_video_data)}")
    

if __name__ == "__main__":
    main()