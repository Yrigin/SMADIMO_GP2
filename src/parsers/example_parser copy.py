from utils.logger import setup_logger

class ExampleParser:
    def __init__(self, url):
        self.url = url
        self.soup = None

    def fetch_data(self):
        import requests
        response = requests.get(self.url)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.content, 'html.parser')
        else:
            raise Exception(f"Failed to fetch data from {self.url}")

    def parse(self):
        if self.soup is None:
            raise Exception("No data fetched. Call fetch_data() first.")
        
        # Example parsing logic
        data = self.soup.find_all('h1')  # Change this to your parsing needs
        return [element.get_text() for element in data]

    def run(self):
        self.fetch_data()
        parsed_data = self.parse()
        return parsed_data


def main():
    # Set up logging
    setup_logger()
    
    # Initialize the parser
    parser = ExampleParser()
    
    # Run the parser
    parser.run()

if __name__ == "__main__":
    main()
