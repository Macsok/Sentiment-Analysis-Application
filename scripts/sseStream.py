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
        compound_list = []
        pos_list = []
        neg_list = []
        neu_list = []
        for index, row in dataframe.iterrows():
            pos, neg, neu, compound, language, text = analyses.default_analysis(row['reply_text'])
            compound_list.append(compound)
            pos_list.append(pos)
            neg_list.append(neg)
            neu_list.append(neu)
            # Setting color
            if compound < 0: color = 'negative'
            elif compound > 0: color = 'positive'
            else: color = 'neutral'
            result_data = {
                'author': row['username'],
                'text': text,
                'compound': compound,
                'language': language,
                'color_type' : color,
                'is_final' : False
            }
            result_json = json.dumps(result_data)
            yield f"data: {result_json}\n\n"
        # Calculate mean values
        mean_compound = sum(compound_list) / len(compound_list) if compound_list else 0
        mean_pos = sum(pos_list) / len(pos_list) if pos_list else 0
        mean_neg = sum(neg_list) / len(neg_list) if neg_list else 0
        mean_neu = sum(neu_list) / len(neu_list) if neu_list else 0
        # After the loop, send a final message to signal the end of the stream
        final_message = {
            'text': 'All items processed!',
            'mean_compound': mean_compound,
            'mean_pos': mean_pos,
            'mean_neg': mean_neg,
            'mean_neu': mean_neu,
            'is_final': True  # Flag to indicate this is the final message
        }
        print(f"""Calculated mean values - Compound: 
              {mean_compound}, Pos: {mean_pos}, Neg: {mean_neg}, Neu: {mean_neu}""")
        yield f"data: {json.dumps(final_message)}\n\n"

    except Exception as e:
        return jsonify({"error": str(e)})