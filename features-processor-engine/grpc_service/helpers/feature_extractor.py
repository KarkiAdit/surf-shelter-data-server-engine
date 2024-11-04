import requests
import time
from urllib.parse import urlparse
from . import url_comparator


class FeatureExtractor:
    """Extracts features from a URL by calling external APIs or research and analysis."""

    def __init__(self, website_url=None):
        self.__website_url = website_url
        self.__extract_domain()
    
    def __extract_domain(self):
        """Compute the domain name from the URL."""
        try:
            self.__website_domain = urlparse(self.__website_url).netloc
        except Exception as e:
            print(f"Error calculating the website domain: {e}")
            self.__website_domain = None

    def __compute_url_length(self):
        """Compute the length of the URL."""
        try:
            self.__url_length = float(len(self.__website_url))
        except Exception as e:
            print(f"Error calculating the URL length: {e}")
            self.__url_length = None

    def __analyze_top_level_domain(self):
        """Compute a score based on the TLD of the URL."""
        try:
            # Conduct research to analyze TLD (top-level domain) pattern, develop an evaluation metric, and return a score
            self.__tld_analysis_score = float(
                90
            )  # Sets average TLD score of commonly trusted and widely used websites
        except Exception as e:
            print(f"Error calculating the TLD analysis score: {e}")
            self.__tld_analysis_score = None

    def __analyze_ip_address(self):
        """Compute a score based on IP address analysis of the URL."""
        try:
            # Conduct research to analyze IP address pattern, develop an evaluation metric, and return a score
            self.__ip_analysis_score = float(
                90
            )  # Sets average IP address score of commonly trusted and widely used websites
        except Exception as e:
            print(f"Error calculating the IP analysis score: {e}")
            self.__ip_analysis_score = None

    def __analyze_sub_level_domain(self):
        """Compute a score based on sub-domain analysis of the URL."""
        try:
            # Conduct research to analyze sub-domain pattern, develop an evaluation metric, and return a score
            self.__sub_domain_analysis_score = float(
                90
            )  # Sets average Sub-domain analysis score of commonly trusted and widely used websites
        except Exception as e:
            print(f"Error calculating the sub-domain analysis score: {e}")
            self.__sub_domain_analysis_score = None

    def __compute_levenshtein_dx(self):
        url_cpr = url_comparator.URLComparator(self.__website_domain)
        self.__levenshtein_dx = url_cpr.levenshtein_dx

    def __compute_time_to_live(self):
        try:
            response = requests.get(f"https://dns.google/resolve?name={self.__website_domain}&type=A")
            response.raise_for_status()
            data = response.json()
            if "Answer" in data:
                self.__time_to_live = data['Answer'][0]['TTL']
            else:
                print("No DNS records found for the specified domain.")
                self.__time_to_live = 0
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TTL from Google DNS API: {e}")
            self.__time_to_live = None

    def __compute_domain_age(self):
        params = {
            "apiKey": "***",
            "domainName": self.__website_domain,
            "outputFormat": "JSON"
        }
        try:
            response = requests.get("https://www.whoisxmlapi.com/whoisserver/WhoisService", params=params)
            response.raise_for_status()
            data = response.json()
            # Extract the estimated domain age if available
            estimated_age = data.get('WhoisRecord', {}).get('estimatedDomainAge')
            if estimated_age is not None:
                self.__domain_age = estimated_age
            else:
                print(f"Could not retrieve the estimated domain age.")
                self.__domain_age = 0
        except requests.exceptions.RequestException as e:
            print(f"Error fetching domain age from WHOIS API service {e}")    
            self.__domain_age = None   


    def __compute_reputation_score(self):
        headers = {
            "accept": "application/json",
            "x-apikey": "*****",
            "content-type": "application/x-www-form-urlencoded"
        }
        payload = {
            "url": self.__website_url
        }
        try:
            # Scan the URL to create a VirusTotal report
            make_report_response = requests.post("https://www.virustotal.com/api/v3/urls", data=payload, headers=headers)
            make_report_response.raise_for_status()
            
            # Extract the report ID
            report_id = make_report_response.json().get("data", {}).get("id")
            if not report_id:
                print("Failed to retrieve report ID.")
                self.__reputation_score = None
                return
            
            # Wait for the analysis to complete
            time.sleep(5)

            # Read the report
            read_report_response = requests.get(f"https://www.virustotal.com/api/v3/analyses/{report_id}", headers=headers)
            read_report_response.raise_for_status()
            data = read_report_response.json()

            # Calculate reputation score based on stats
            stats = data.get("data", {}).get("attributes", {}).get("stats", {})
            if stats:
                total_reports = stats.get("malicious", 0) + stats.get("suspicious", 0) + stats.get("harmless", 0) + stats.get("undetected", 0)
                if total_reports > 0:
                    self.__reputation_score = (stats.get("malicious", 0) + stats.get("suspicious", 0)) / total_reports
                else:
                    print("No available data to calculate a reputation score.")
                    self.__reputation_score = 0
            else:
                print("No stats data available in the response.")
                self.__reputation_score = None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching reputation score from VirusTotal API: {e}")
            self.__reputation_score = None

    def get_unusual_ext_features(self):
        self.__compute_url_length()
        self.__analyze_top_level_domain()
        self.__analyze_ip_address()
        self.__analyze_sub_level_domain()
        return {
            "url_length": self.__url_length,
            "tld-analysis-score": self.__tld_analysis_score,
            "ip-analysis-score": self.__ip_analysis_score,
            "sub-domain-analysis-score": self.__sub_domain_analysis_score,
        }

    def get_typosquatting_features(self):
        self.__compute_levenshtein_dx()
        return {
            "levenshtein_dx": self.__levenshtein_dx,
        }

    def get_phishing_features(self):
        self.__compute_time_to_live()
        self.__compute_domain_age()
        self.__compute_reputation_score()
        return {
            "time_to_live": self.__time_to_live,
            "domain_age": self.__domain_age,
            "reputation_score": self.__reputation_score,
        }
