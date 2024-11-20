import json
from flask import jsonify
import os
import analyses
import pandas as pd


def x_generate_sse(csv_file_path : str):
    """
    Reads a CSV file, processes each row with a function, and returns results.
    """
    # csv_file_path = os.path.join(os.path.dirname(__file__), file_path)

    if not os.path.exists(csv_file_path):
        return jsonify({"error": "CSV file not found!"}), 404
    
    try:
        dataframe = pd.read_csv(csv_file_path)
        for index, row in dataframe.iterrows():
            pos, neg, neu, compound, language, text = analyses.default_analysis(row['reply_text'])
            # Setting color
            if compound < 0: color = '#ba1f1f'
            elif compound > 0: color = '#4aa54d'
            else: color = '#3888e3'
            result_data = {
                'author': row['username'],
                'text': text,
                'compound': compound,
                'language': language,
                'color' : color
            }
            result_json = json.dumps(result_data)
            yield f"data: {result_json}\n\n"
        # After the loop, send a final message to signal the end of the stream
        final_message = {
        'text': 'All items processed!',
        'is_final': True  # Flag to indicate this is the final message
        }
        yield f"data: {json.dumps(final_message)}\n\n"

    except Exception as e:
        return jsonify({"error": str(e)})