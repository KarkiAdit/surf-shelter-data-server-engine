import numpy as np
from urllib.parse import urlparse

class URLComparator:
    __good_urls = [
        # Technology and Search
        "https://www.google.com",
        "https://www.apple.com",
        "https://www.microsoft.com",
        "https://www.wikipedia.org",
        "https://www.yahoo.com",
        "https://www.bing.com",
        "https://www.baidu.com",
        "https://www.ask.com",
        "https://www.duckduckgo.com",
        "https://www.aol.com",
        "https://www.yandex.com",
        "https://www.naver.com",
        # Social Media
        "https://www.facebook.com",
        "https://www.twitter.com",
        "https://www.instagram.com",
        "https://www.linkedin.com",
        "https://www.snapchat.com",
        "https://www.pinterest.com",
        "https://www.tiktok.com",
        "https://www.reddit.com",
        "https://www.quora.com",
        "https://www.whatsapp.com",
        "https://www.wechat.com",
        "https://www.telegram.org",
        # E-commerce
        "https://www.amazon.com",
        "https://www.ebay.com",
        "https://www.walmart.com",
        "https://www.alibaba.com",
        "https://www.bestbuy.com",
        "https://www.target.com",
        "https://www.shopify.com",
        "https://www.flipkart.com",
        "https://www.etsy.com",
        "https://www.costco.com",
        "https://www.ikea.com",
        "https://www.homedepot.com",
        # Finance and Banking
        "https://www.bankofamerica.com",
        "https://www.wellsfargo.com",
        "https://www.citi.com",
        "https://www.chase.com",
        "https://www.goldmansachs.com",
        "https://www.morganstanley.com",
        "https://www.hsbc.com",
        "https://www.americanexpress.com",
        "https://www.paypal.com",
        "https://www.mastercard.com",
        "https://www.visa.com",
        "https://www.schwab.com",
        # News and Media
        "https://www.cnn.com",
        "https://www.bbc.com",
        "https://www.nytimes.com",
        "https://www.theguardian.com",
        "https://www.forbes.com",
        "https://www.bloomberg.com",
        "https://www.wsj.com",
        "https://www.usatoday.com",
        "https://www.foxnews.com",
        "https://www.reuters.com",
        "https://www.cnbc.com",
        "https://www.nbcnews.com",
        # Government and Public Services
        "https://www.usa.gov",
        "https://www.whitehouse.gov",
        "https://www.nasa.gov",
        "https://www.cdc.gov",
        "https://www.nih.gov",
        "https://www.fbi.gov",
        "https://www.tsa.gov",
        "https://www.cia.gov",
        "https://www.irs.gov",
        "https://www.ssa.gov",
        "https://www.sec.gov",
        "https://www.fcc.gov",
        # Education
        "https://www.harvard.edu",
        "https://www.stanford.edu",
        "https://www.mit.edu",
        "https://www.berkeley.edu",
        "https://www.cam.ac.uk",
        "https://www.ox.ac.uk",
        "https://www.yale.edu",
        "https://www.ucla.edu",
        "https://www.columbia.edu",
        "https://www.princeton.edu",
        "https://www.caltech.edu",
        "https://www.nyu.edu",
        # Entertainment and Streaming
        "https://www.netflix.com",
        "https://www.spotify.com",
        "https://www.hulu.com",
        "https://www.disneyplus.com",
        "https://www.pandora.com",
        "https://www.siriusxm.com",
        "https://www.vimeo.com",
        "https://www.soundcloud.com",
        "https://www.crunchyroll.com",
        "https://www.funimation.com",
        "https://www.twitch.tv",
        "https://www.hbo.com",
        # Health and Wellness
        "https://www.webmd.com",
        "https://www.mayoclinic.org",
        "https://www.healthline.com",
        "https://www.clevelandclinic.org",
        "https://www.medlineplus.gov",
        "https://www.drugs.com",
        "https://www.everydayhealth.com",
        "https://www.nih.gov",
        "https://www.hopkinsmedicine.org",
        "https://www.heart.org",
        "https://www.lung.org",
        "https://www.kff.org",
        # Travel and Tourism
        "https://www.tripadvisor.com",
        "https://www.booking.com",
        "https://www.expedia.com",
        "https://www.airbnb.com",
        "https://www.kayak.com",
        "https://www.priceline.com",
        "https://www.hotels.com",
        "https://www.orbitz.com",
        "https://www.agoda.com",
        "https://www.travelocity.com",
        "https://www.hilton.com",
        "https://www.marriott.com",
        # Food and Beverage
        "https://www.mcdonalds.com",
        "https://www.starbucks.com",
        "https://www.dominos.com",
        "https://www.pizzahut.com",
        "https://www.kfc.com",
        "https://www.bk.com",
        "https://www.dunkindonuts.com",
        "https://www.subway.com",
        "https://www.tacobell.com",
        "https://www.chick-fil-a.com",
        "https://www.wendys.com",
        "https://www.papajohns.com",
        # Automotive
        "https://www.toyota.com",
        "https://www.ford.com",
        "https://www.honda.com",
        "https://www.chevrolet.com",
        "https://www.bmw.com",
        "https://www.mercedes-benz.com",
        "https://www.audi.com",
        "https://www.tesla.com",
        "https://www.volkswagen.com",
        "https://www.nissanusa.com",
        "https://www.hyundaiusa.com",
        "https://www.lexus.com",
        # Job Search and Career
        "https://www.indeed.com",
        "https://www.linkedin.com",
        "https://www.monster.com",
        "https://www.glassdoor.com",
        "https://www.ziprecruiter.com",
        "https://www.careerbuilder.com",
        "https://www.simplyhired.com",
        "https://www.roberthalf.com",
        "https://www.snagajob.com",
        "https://www.usajobs.gov",
        "https://www.angel.co",
        "https://www.flexjobs.com",
        # Real Estate
        "https://www.zillow.com",
        "https://www.realtor.com",
        "https://www.redfin.com",
        "https://www.trulia.com",
        "https://www.century21.com",
        "https://www.primelocation.com",
        "https://www.rightmove.co.uk",
        "https://www.apartments.com",
        "https://www.compass.com",
        "https://www.coldwellbanker.com",
        "https://www.kw.com",
        "https://www.movoto.com",
        # Miscellaneous Popular Sites
        "https://www.weather.com",
        "https://www.time.com",
        "https://www.nationalgeographic.com",
        "https://www.history.com",
        "https://www.adobe.com",
        "https://www.autodesk.com",
        "https://www.ibm.com",
        "https://www.oracle.com",
        "https://www.salesforce.com",
        "https://www.dropbox.com",
        "https://www.zoom.us",
        "https://www.ups.com",
        "https://www.fedex.com",
        "https://www.dhl.com",
        "https://www.tesla.com",
        "https://www.cnn.com",
    ]
    levenshtein_dx = None

    def __init__(self, target_domain):
        self.__target_domain = target_domain

    def __find_levenshtein_distance(self, str1, str2):
        """Helper method to compute Levenshtein distance between two strings."""
        len_str1, len_str2 = len(str1), len(str2)
        dp = np.zeros((len_str1 + 1, len_str2 + 1), dtype=int)

        for i in range(len_str1 + 1):
            dp[i][0] = i
        for j in range(len_str2 + 1):
            dp[0][j] = j

        for i in range(1, len_str1 + 1):
            for j in range(1, len_str2 + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        return dp[len_str1][len_str2]

    def run_url_comparator(self):
        try:
            distances = []
            for url in self.__good_urls:
                parsed_good_domain = urlparse(url).netloc
                distance = self.__find_levenshtein_distance(
                    self.__target_domain, parsed_good_domain
                )
                distances.append(distance)

            # Set minimum distance as the typosquatting score
            self.levenshtein_dx = min(distances)

        except Exception as e:
            print(f"Error calculating the typosquatting score: {e}")
