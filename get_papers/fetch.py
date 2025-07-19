import requests
import xml.etree.ElementTree as ET
from typing import List, Dict

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def fetch_papers(query: str, debug: bool = False) -> List[Dict]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 10
    }

    if debug:
        print(f"Searching PubMed with query: {query}")

    response = requests.get(ESEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()

    id_list = data.get("esearchresult", {}).get("idlist", [])
    if debug:
        print(f"Found {len(id_list)} articles.")

    if not id_list:
        return []

    efetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml"
    }

    efetch_response = requests.get(EFETCH_URL, params=efetch_params)
    efetch_response.raise_for_status()

    root = ET.fromstring(efetch_response.text)
    papers = []

    for article in root.findall(".//PubmedArticle"):
        paper = {
            "PubmedID": "",
            "Title": "",
            "Publication Date": "",
            "Non-academic Author(s)": "",
            "Company Affiliation(s)": "",
            "Corresponding Author Email": ""
        }

        # PubMed ID
        pmid = article.findtext(".//PMID")
        paper["PubmedID"] = pmid if pmid else ""

        # Title
        title = article.findtext(".//ArticleTitle")
        paper["Title"] = title if title else ""

        # Publication Date
        date = article.find(".//PubDate")
        if date is not None:
            year = date.findtext("Year") or ""
            month = date.findtext("Month") or ""
            day = date.findtext("Day") or ""
            paper["Publication Date"] = f"{year}-{month}-{day}".strip("-")
        else:
            paper["Publication Date"] = ""

        # Authors and Affiliations
        non_academic_authors = []
        company_affiliations = []
        corresponding_email = ""

        for author in article.findall(".//Author"):
            affiliation_info = author.findtext(".//AffiliationInfo/Affiliation") or ""
            if "university" not in affiliation_info.lower() and "institute" not in affiliation_info.lower():
                last_name = author.findtext("LastName") or ""
                fore_name = author.findtext("ForeName") or ""
                full_name = f"{fore_name} {last_name}".strip()
                if full_name:
                    non_academic_authors.append(full_name)
                if affiliation_info:
                    company_affiliations.append(affiliation_info)

                # Try to find email in affiliation
                if "@" in affiliation_info and not corresponding_email:
                    for word in affiliation_info.split():
                        if "@" in word:
                            corresponding_email = word.strip(".,;()<>\"'")

        paper["Non-academic Author(s)"] = "; ".join(non_academic_authors)
        paper["Company Affiliation(s)"] = "; ".join(company_affiliations)
        paper["Corresponding Author Email"] = corresponding_email

        papers.append(paper)

    return papers
