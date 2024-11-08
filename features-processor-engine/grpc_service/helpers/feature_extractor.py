import os
import requests
import time
import re
from . import url_comparator

class FeatureExtractor:
    """Extracts various features from a URL through external API calls, research, and analysis.

    This class provides methods to gather important metrics and attributes of a URL, such as reputation scores, 
    domain age, DNS Time-To-Live (TTL), and similarity to known trusted domains. These features are used for 
    further analysis to assess the URL’s trustworthiness, potential risks, and overall reliability.
    """

    def __init__(self, website_url=None):
        self.__website_url = website_url
        self.__extract_domain()
    
    def __extract_domain(self):
        """Compute the domain name from the URL."""
        try:
            # Regex to match the domain part
            match = re.search(r"^(?:http[s]?://)?([^:/\s]+)", self.__website_url)
            self.__website_domain = match.group(1) if match else None
        except Exception as e:
            print(f"Error analyzing the website domain: {e}")
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
        """Compute the Levenshtein distance between the website's domain and a set of trusted domains.

        This method calculates the Levenshtein distance, which measures the similarity between the website's domain 
        and known trusted domains. A lower distance indicates higher similarity, suggesting a possible typosquatting 
        or phishing attempt if the domain is closely similar to a trusted domain.
        """
        url_cpr = url_comparator.URLComparator(self.__website_domain)
        # Run the pattern matching algorithm to find the levenshtein dx
        url_cpr.run_url_comparator()
        self.__levenshtein_dx = url_cpr.levenshtein_dx

    def __compute_time_to_live(self):
        """Retrieve the website's DNS Time-To-Live (TTL) value using Google's DNS API.

        This method queries Google's DNS API to obtain the TTL value for the website's domain, which represents 
        the duration (in seconds) that DNS records are cached before requiring a refresh. A lower TTL indicates 
        that the domain's DNS information is updated frequently, while a higher TTL suggests longer caching periods.
        """
        try:
            response = requests.get(f"https://dns.google/resolve?name={self.__website_domain}&type=A")
            response.raise_for_status()
            data = response.json()
            if "Answer" in data:
                self.__time_to_live = float(data['Answer'][0]['TTL'])
            else:
                print("No DNS records found for the specified domain.")
                self.__time_to_live = 0.0
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TTL from Google DNS API: {e}")
            self.__time_to_live = None

    def __compute_domain_age(self):
        """Retrieve and compute the age of the website's domain using the WHOIS XML API.

        This method calls the WHOIS XML API to obtain the estimated domain age in years. Domain age is an indicator of 
        the website's longevity and potential trustworthiness, as older domains are generally considered more reliable. 
        If the domain age is available, it is stored; otherwise, a default value of 0 is set if the information 
        cannot be retrieved.
        """
        params = {
            "apiKey": os.getenv("WHOIS_XML_KEY"),
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
                self.__domain_age = float(estimated_age)
            else:
                print(f"Could not retrieve the estimated domain age.")
                self.__domain_age = 0.0
        except requests.exceptions.RequestException as e:
            print(f"Error fetching domain age from WHOIS API service {e}")
            self.__domain_age = None


    def __compute_reputation_score(self):
        """Compute a reputation score indicating the likelihood of a website being a phishing site using VirusTotal's API.

        This method submits the website URL to VirusTotal for analysis, retrieves the analysis report, and calculates 
        a reputation score based on the proportion of malicious and suspicious flags from various security engines.
        The score ranges from 0 to 1, where a higher score indicates a higher likelihood of the website being malicious or suspicious.
        """
        headers = {
            "accept": "application/json",
            "x-apikey": os.getenv("VIRUS_TOTAL_KEY"),
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
                    print("Evaluated using existing data...")
                    self.__reputation_score = (stats.get("malicious", 0) + stats.get("suspicious", 0)) / total_reports
                else:
                    print("No available data to calculate a reputation score.")
                    self.__reputation_score = 0.0
            else:
                print("No stats data available in the response.")
                self.__reputation_score = 0.0
        except requests.exceptions.RequestException as e:
            print(f"Error fetching reputation score from VirusTotal API: {e}")
            self.__reputation_score = None

    def __evaluate_malicious_label(self):
        """
        Checks the likelihood of a URL being malicious using the Google Safe Browsing API.

        This method submits the URL for analysis against "MALWARE" and "SOCIAL_ENGINEERING" threats, evaluates the threat counts, 
        and flags the URL as malicious if both threat types exceed set thresholds. If an error occurs, the result is set to None.
        """
        params = {
            "key": os.getenv("GOOGLE_SAFE_BROWSING_KEY")
        }
        payload = {
                    "client": {
                        "clientId": "surf-shelter-data-server-engine",
                        "clientVersion": "0.0"
                    },
                    "threatInfo": {
                        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
                        "platformTypes": ["ANY_PLATFORM"],
                        "threatEntryTypes": ["URL"],
                        "threatEntries": [
                            {
                                "url": self.__website_url
                            }
                        ]
                    }
                }
        # Define threshold values based on security research
        malware_threshold = 3
        social_engineering_threshold = 3
        try:
            response = requests.post(
                "https://safebrowsing.googleapis.com/v4/threatMatches:find",
                params=params,
                json=payload
            )
            response.raise_for_status()
            data = response.json() 
            if "matches" in data:
                threat_counts = {"MALWARE": 0, "SOCIAL_ENGINEERING": 0}   
                # Aggregate threat counts
                for match in data["matches"]:
                    threat_type = match['threatType']
                    threat_counts[threat_type] += 1
                # Label as malicious only if both threats exceed their thresholds
                if (threat_counts["MALWARE"] >= malware_threshold and 
                    threat_counts["SOCIAL_ENGINEERING"] >= social_engineering_threshold):
                    self.__is_malicious = True
                    print(f"The URL is flagged as malicious. Threat counts: {threat_counts}")
                else:
                    self.__is_malicious = False
                    print("The URL does not meet the malicious threshold.")     
            else:
                self.__is_malicious = False
                print("The URL is safe.")
        except requests.exceptions.RequestException as e:
            print(f"Error checking URL with Google Safe Browsing API: {e}")
            self.__is_malicious = None

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
    
    def get_prediction_label(self):
        self.__evaluate_malicious_label()
        return {
            "is_malicious": self.__is_malicious,
            "is_click_fraud": False,
            "is_pay_fraud": False,
        }
