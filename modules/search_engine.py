import requests
from typing import Dict, List, Optional, Union
from PIL import Image
import io
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from duckduckgo_search import ddg
import wolframalpha

class UniversalSearch:
    def __init__(self, config: Dict):
        self.config = config
        self.vision_client = ComputerVisionClient(
            config['azure']['vision_endpoint'],
            CognitiveServicesCredentials(config['azure']['vision_key'])
        )
        self.wolfram_client = wolframalpha.Client(config['wolfram_app_id'])
        
    async def search(self, query: str, search_type: str = "text", 
                    engine: str = "auto", image_data: bytes = None) -> Dict:
        """Universal search function supporting both text and image queries"""
        try:
            if search_type == "image" and image_data:
                return await self._image_search(image_data, query)
            else:
                return await self._text_search(query, engine)
        except Exception as e:
            return {"error": str(e)}
            
    async def _text_search(self, query: str, engine: str) -> Dict:
        """Handle text-based searches"""
        results = {
            "query": query,
            "engine": engine,
            "results": []
        }
        
        if engine == "auto":
            # Try Wolfram Alpha first for factual queries
            wolfram_result = self._wolfram_search(query)
            if wolfram_result:
                results["engine"] = "wolfram"
                results["results"] = wolfram_result
                return results
                
        if engine in ["auto", "ddg"]:
            # Fall back to DuckDuckGo
            ddg_results = ddg(query, max_results=5)
            results["engine"] = "ddg"
            results["results"] = ddg_results
            
        return results
        
    async def _image_search(self, image_data: bytes, query: str = "") -> Dict:
        """Handle image-based searches"""
        image = Image.open(io.BytesIO(image_data))
        
        # Analyze image using Azure Computer Vision
        analysis = self.vision_client.analyze_image_in_stream(
            image_data,
            visual_features=[
                VisualFeatureTypes.objects,
                VisualFeatureTypes.tags,
                VisualFeatureTypes.description,
                VisualFeatureTypes.faces
            ]
        )
        
        results = {
            "description": analysis.description.captions[0].text if analysis.description.captions else "",
            "tags": [tag.name for tag in analysis.tags],
            "objects": [obj.object_property for obj in analysis.objects],
            "text_query_results": None
        }
        
        # If there's an additional text query, search related to image content
        if query:
            combined_query = f"{results['description']} {query}"
            text_results = await self._text_search(combined_query, "ddg")
            results["text_query_results"] = text_results
            
        return results
        
    def _wolfram_search(self, query: str) -> Optional[List[Dict]]:
        """Search using Wolfram Alpha"""
        try:
            res = self.wolfram_client.query(query)
            if res.success:
                return [
                    {"pod": pod.title, "text": pod.text}
                    for pod in res.pods
                    if pod.text
                ]
        except:
            return None
