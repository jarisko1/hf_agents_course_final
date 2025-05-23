from dotenv import load_dotenv
import os

# YouTube transcription tool
# from langchain.document_loaders import YoutubeLoader
from langchain_community.document_loaders import YoutubeLoader

# Python tool
from langchain_experimental.utilities import PythonREPL

# Search tools
# from langchain_community.tools import Tool, DuckDuckGoSearchRun
# from langchain_community.utilities import GoogleSerperAPIWrapper
# from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient

from langchain_community.retrievers import WikipediaRetriever
from langchain_community.retrievers import ArxivRetriever

# TTS tool
import assemblyai as aai

# MCP server
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base


# Create an MCP server
mcp = FastMCP("HF_Agents_Tools")

### Audio tool
@mcp.tool()
def transcribe_audio(audio_file: str) -> str | None:
    """Transcribes audio file into text"""

    load_dotenv()

    aai.settings.api_key = os.environ["ASSEMBLY_AI_API_KEY"]

    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)

    transcript = aai.Transcriber(config=config).transcribe(audio_file)

    if transcript.status == "error":
        print(f"Transcription failed: {transcript.error}")
        return ""

    return transcript.text

### YouTube transcription tool
@mcp.tool()
def transcribe_video(video_url: str) -> str:
    """Transcribes YouTube video into text"""

    text = ""

    loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=1htKBjuUWec", add_video_info=False)
    docs = loader.load()
    if len(docs) > 0:
        text = docs[0].page_content

    return text

### Web search tool
@mcp.tool()
def websearch(websearch_query:str) -> str:
    """
    A search engine optimized for comprehensive, accurate, and trusted results.
    Useful for when you need to answer questions about current events.
    Input should be a search query.
    """

    load_dotenv()

    client = TavilyClient()
    result = client.search(query=websearch_query, search_depth="basic", max_results=3)
    return str(result)

### Wikipedia search tool
@mcp.tool()
def wiki_search(wiki_search_query:str) -> str:
    """
    Searches Wikipedia for topic.
    """

    retriever = WikipediaRetriever()
    docs = retriever.invoke(wiki_search_query)
    return str(docs)

### Arxiv search tool
@mcp.tool()
def arxiv_search(arxiv_search_query:str) -> str:
    """
    Searches for studies in Arxiv on topic.
    """

    retriever = ArxivRetriever()
    docs = retriever.invoke(arxiv_search_query)
    return str(docs)

### Python tool
@mcp.tool()
def python_repl(python_code: str) -> str:
    """
    "A Python shell. Use this to execute python commands.
    Input should be a valid python command.
    If you want to see the output of a value, you should print it out with `print(...)`."
    """

    python_repl = PythonREPL()
    result = python_repl.run(python_code, timeout=30)

    return result

if __name__ == "__main__":
    mcp.run(transport="stdio")