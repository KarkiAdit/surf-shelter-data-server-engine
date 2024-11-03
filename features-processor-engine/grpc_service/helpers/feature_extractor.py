from . import url_comparator
class FeatureExtractor:
    """Extracts features from a URL by calling external APIs or research and analysis."""

    def __init__(self, website_url=None):
        self.__website_url = website_url

    def __compute_url_length(self, url):
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
            self.__tld_analysis_score = float(90)  # Sets average TLD score of commonly trusted and widely used websites
        except Exception as e:
            print(f"Error calculating the TLD analysis score: {e}")
            self.__tld_analysis_score = None
  
    def __analyze_ip_address(self):
        """Compute a score based on IP address analysis of the URL."""
        try:
            # Conduct research to analyze IP address pattern, develop an evaluation metric, and return a score
            self.__ip_analysis_score = float(90)  # Sets average IP address score of commonly trusted and widely used websites
        except Exception as e:
            print(f"Error calculating the IP analysis score: {e}")
            self.__ip_analysis_score = None     

    def __analyze_sub_level_domain(self):
        """Compute a score based on sub-domain analysis of the URL."""
        try:
            # Conduct research to analyze sub-domain pattern, develop an evaluation metric, and return a score
            self.__sub_domain_analysis_score = float(90)  # Sets average Sub-domain analysis score of commonly trusted and widely used websites
        except Exception as e:
            print(f"Error calculating the sub-domain analysis score: {e}")
            self.__sub_domain_analysis_score = None      

    def __compute_levenshtein_dx(self):
        url_cpr = url_comparator.URLComparator(self.__website_url)
        self.__levenshtein_dx = url_cpr.levenshtein_dx 

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
