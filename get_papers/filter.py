from typing import List, Dict

def filter_non_academic_authors(papers: List[Dict]) -> List[Dict]:
    """
    Filters papers that contain at least one non-academic author.
    """
    return [paper for paper in papers if paper["Non-academic Author(s)"]]