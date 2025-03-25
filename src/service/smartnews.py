import requests

# Assuming GPTClient is part of chatgpt module, import it
from service.chatgpt import GPTClient

class SmartNews(GPTClient):
    def __init__(self, openai_api_key=None, news_api_key=None, model=None):
        """
        Initializes SmartNews with both an OpenAI API key and a NewsAPI key.
        
        Parameters:
          openai_api_key (str): Your OpenAI API key.
          news_api_key (str): Your NewsAPI key.
          model (str): The GPT model to use.
        """
        super().__init__(openai_api_key, model=model)
        if news_api_key is None:
            news_api_key = "your api key here"
        self.news_api_key = news_api_key

    def search_latest_news(self, query, pageSize=5):
        """
        Uses the NewsAPI to search for the latest news articles matching the query.
        
        Parameters:
          query (str): The news topic to search for.
          pageSize (int): The maximum number of articles to retrieve.
        
        Returns:
          list: A list of article dictionaries containing keys like "title", "description", and "url".
        """
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": pageSize,
            "apiKey": self.news_api_key,
            "language": "en"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            return articles            
        else:
            print(f"Error fetching news: {response.status_code} - {response.text}")
            return []

    def get_news(self, query):
        """
        Searches for the latest news on the given topic, then uses ChatGPT to generate a summary.
        
        Parameters:
          query (str): The news topic.
        
        Returns:
          str: A concise summary of the latest news.
        """
        articles = self.search_latest_news(query)
        if not articles:
            return "No news articles found."

        # Build a string with the headlines, descriptions, and URLs.
        news_content = ""
        for article in articles:
            title = article.get("title", "No title")
            description = article.get("description", "")
            url = article.get("url", "")
            news_content += f"Title: {title}\nDescription: {description}\nURL: {url}\n\n"

        prompt = f"Summarize the following news articles in a concise manner (no web link):\n\n{news_content}"
        if len(prompt) > 4096:
            prompt = prompt[:4096]
        #if return from ask is none then return the prompt, otherwise return the news_content
        summary = self.ask(prompt) or news_content
        return summary


# Example usage:
if __name__ == "__main__":
    openai_api_key = None
    news_api_key = None
    
    smart_news = SmartNews(openai_api_key, news_api_key)
    
    topic = input("Enter the topic to search news for: ")
    summary = smart_news.summarize_latest_news(topic)
    
    print("\nNews Summary:")
    print(summary)