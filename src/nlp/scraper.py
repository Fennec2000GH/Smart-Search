
import requests, os

from bs4 import BeautifulSoup, SoupStrainer
from google.oauth2 import service_account
from google.cloud import language_v1
from dotenv import load_dotenv

def scrape_important_words(url: str):
    """Soups HTML from given url.

    Args:
        url (str): Url to scrape web content from.
    """
    req = requests.get(url=url)
    bs = BeautifulSoup(markup=req.text)
    # print(bs)

    # tags to consider that may contain important words in website
    important_tags = list(['title', 'head', 'thead', 'h1', 'h2', 'h3', 'h4', 'p'])

    important_tags_text = [tag.text for tag in bs.find_all(name=important_tags)]
    important_tags_textblock = '\n'.join(important_tags_text)
    print(important_tags_textblock)
    return important_tags_textblock

def sample_analyze_entities(text_content: str, text_type: language_v1.Document.Type = language_v1.Document.Type.PLAIN_TEXT):
    """Finds entities i.e. topics present within text and lists links to wikipedia articles for each discovered entity.

    Args:
        text_content (str): The text content to analyze.
        text_type (language_v1.Document.Type, optional): Type of text gi. Defaults to language_v1.Document.Type.PLAIN_TEXT.

    Returns:
        list[dict]: List of entity objects as dicts resembling an array of objects in JavaScript/
    """

    load_dotenv()
    KEYDIR_PATH = os.getenv('KEYDIR_PATH')
    credentials = service_account.Credentials.from_service_account_file(KEYDIR_PATH)
    client = language_v1.LanguageServiceClient(credentials=credentials)

    # Example only
    # text_content = 'California is a state.'

    # Available types: PLAIN_TEXT, HTML
    type_ = text_type

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entities(request = {'document': document, 'encoding_type': encoding_type})

    # Loop through entitites returned from the API
    for entity in response.entities:
        print(u"Representative name for the entity: {}".format(entity.name))

        # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al
        print(u"Entity type: {}".format(language_v1.Entity.Type(entity.type_).name))

        # Get the salience score associated with the entity in the [0, 1.0] range
        print(u"Salience score: {}".format(entity.salience))

        # Loop over the metadata associated with entity. For many known entities,
        # the metadata is a Wikipedia URL (wikipedia_url) and Knowledge Graph MID (mid).
        # Some entity types may have additional metadata, e.g. ADDRESS entities
        # may have metadata for the address street_name, postal_code, et al.
        for metadata_name, metadata_value in entity.metadata.items():
            print(u"{}: {}".format(metadata_name, metadata_value))

        # Loop over the mentions of this entity in the input document.
        # The API currently supports proper noun mentions.
        for mention in entity.mentions:
            print(u"Mention text: {}".format(mention.text.content))

            # Get the mention type, e.g. PROPER for proper noun
            print(
                u"Mention type: {}".format(language_v1.EntityMention.Type(mention.type_).name)
            )

    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
    print(u"Language of the text: {}".format(response.language))
    return response

def findAllWikiLinks(response: language_v1.types.language_service.AnalyzeEntitiesResponse):
    """Collects wikipedia links to discovered entities.

    Args:
        response (language_v1.types.language_service.AnalyzeEntitiesResponse): Object returned by "sample_analyze_entities" function.

    Returns:
        list[str]: List of urls to wikipedia articles for each available entity discrovered.
    """
    wikiLIST = []
    for i in response.entities:
        for value, key in i.metadata.items():
            if value == "wikipedia_url":
                wikiLIST.append(key)
    return wikiLIST

def sample_analyze_sentiment(text_content: str, text_type: language_v1.Document.Type = language_v1.Document.Type.PLAIN_TEXT):
    """Analyzing Sentiment in a String.

    Args:
        text_content (str): The text content to analyze.
        text_type (language_v1.Document.Type, optional): Type of text gi. Defaults to language_v1.Document.Type.PLAIN_TEXT.
    """

    load_dotenv()
    KEYDIR_PATH = os.getenv('KEYDIR_PATH')
    keyDIR = "ruhacks-312105-8c743209e4a6.json"
    credentials = service_account.Credentials.from_service_account_file(KEYDIR_PATH)
    client = language_v1.LanguageServiceClient(credentials=credentials)

    # Available types: PLAIN_TEXT, HTML
    type_ = text_type

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8
    response = client.analyze_sentiment(request = {'document': document, 'encoding_type': encoding_type})

    # Get overall sentiment of the input document
    print(u"Document sentiment score: {}".format(response.document_sentiment.score))
    print(
        u"Document sentiment magnitude: {}".format(
            response.document_sentiment.magnitude
        )
    )
    # Get sentiment for all sentences in the document
    for sentence in response.sentences:
        print(u"Sentence text: {}".format(sentence.text.content))
        print(u"Sentence sentiment score: {}".format(sentence.sentiment.score))
        print(u"Sentence sentiment magnitude: {}".format(sentence.sentiment.magnitude))

    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
    print(u"Language of the text: {}".format(response.language))

    return response

def emojify(response: language_v1.types.language_service.AnalyzeSentimentResponse):
    """[summary]

    Args:
        response (language_v1.types.language_service.AnalyzeSentimentResponse): [description]
    """
    score = response.document_sentiment.score
    if score > 0.5:
        return '😃'
    elif score > 0.25:
        return '😊'
    elif score > 0:
        return '🙂'
    elif score == 0:
        return '😐'
    elif score >= -0.25:
        return '😠'
    elif score >= -0.5:
        return '👿'
    else:
        return '💀'

if __name__ == '__main__':
    url = 'https://mlh.io'
    sample_text = scrape_important_words(url=url)
    # bs = BeautifulSoup(markup=requests.get(url=url).text)
    # print(bs.html)
    response_entities = sample_analyze_entities(text_content=sample_text)
    print('-' * 100)
    print(response_entities)
    print(type(response_entities))
    print('-' * 100)
    wikiLIST = findAllWikiLinks(response=response_entities)
    print(wikiLIST)
    print('-' * 100)
    response_sentiment = sample_analyze_sentiment(text_content=sample_text)
    print(response_sentiment)
    print(type(response_sentiment))
    emoticon = emojify(response=response_sentiment)
    print(f'sentiment score: {response_sentiment.document_sentiment.score}, emoticon: {emoticon}')
