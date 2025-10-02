from typing import List, Dict, Any

import numpy as np


def get_cf_recommendations(book_name: str, pt, books, similarity_scores, k: int = 5) -> List[Dict[str, Any]]:
    """
    Compute collaborative filtering recommendations given the matrices/dataframes.
    Returns a list of dicts with keys: title, author, image.
    """
    try:
        index_list = np.where(pt.index == book_name)[0]
        if not index_list.any():
            return []

        index = index_list[0]
        similar_items = sorted(
            list(enumerate(similarity_scores[index])),
            key=lambda x: x[1],
            reverse=True
        )[1 : 1 + k]

        recommendations: List[Dict[str, Any]] = []
        for i in similar_items:
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            if temp_df.empty:
                continue
            book_data = temp_df.drop_duplicates('Book-Title').iloc[0]
            recommendations.append({
                'title': book_data['Book-Title'],
                'author': book_data['Book-Author'],
                'image': book_data['Image-URL-M']
            })

        return recommendations
    except Exception:
        return []


