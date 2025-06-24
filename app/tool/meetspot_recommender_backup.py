import asyncio
import json
import math
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import aiofiles
import aiohttp
from pydantic import Field

from app.logger import logger
from app.tool.base import BaseTool, ToolResult
from app.config import config


class CafeRecommender(BaseTool):
    """场所推荐工具，基于多个地点计算最佳会面位置并推荐周边场所"""

    name: str = "place_recommender"
    description: str = """推荐适合多人会面的场所。
该工具基于多个地点的位置信息，计算最佳会面地点，并推荐附近的各类场所。
工具会生成包含地图和推荐信息的HTML页面，提供详细的场所信息、地理位置和交通建议。
可以搜索各种类型的场所，如咖啡馆、餐厅、商场、电影院、篮球场等。
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "locations": {
                "type": "array",
                "description": "(必填) 所有参与者的位置描述列表，每个元素为一个地点描述字符串，如['北京朝阳区望京宝星园', '海淀中关村地铁站']",
                "items": {"type": "string"},
            },
            "keywords": {
                "type": "string",
                "description": "(可选) 搜索关键词，如'咖啡馆'、'篮球场'、'电影院'、'商场'等。前端会将选择的场所类型（如“图书馆”）合并到此关键词中。",
                "default": "咖啡馆",
            },
            "place_type": {
                "type": "string",
                "description": "(可选) 场所类型编码，如'050000'(餐饮),'080116'(篮球场),'080601'(电影院),'060100'(商场)等，默认为空。注意：通常前端会将场所类型通过keywords参数传递。",
                "default": "",
            },
            "user_requirements": {
                "type": "string",
                "description": "(可选) 用户的额外需求，如'停车方便'，'环境安静'等",
                "default": "",
            },
        },
        "required": ["locations"],
    }

    # 高德地图API密钥
    api_key: str = Field(default="")

    # 缓存请求结果以减少API调用
    geocode_cache: Dict[str, Dict] = Field(default_factory=dict)
    poi_cache: Dict[str, List] = Field(default_factory=dict)

    PLACE_TYPE_CONFIG: Dict[str, Dict[str, str]] = {
        "咖啡馆": {
            "topic": "咖啡会",
            "icon_header": "bxs-coffee-togo",
            "icon_section": "bx-coffee",
            "icon_card": "bxs-coffee-alt",
            "map_legend": "咖啡馆",
            "noun_singular": "咖啡馆",
            "noun_plural": "咖啡馆",
            "theme_primary": "#9c6644", # 棕色系
            "theme_primary_light": "#c68b59",
            "theme_primary_dark": "#7f5539",
            "theme_secondary": "#c9ada7",
            "theme_light": "#f2e9e4",
            "theme_dark": "#22223b",
        },
        "图书馆": {
            "topic": "知书达理会",
            "icon_header": "bxs-book",
            "icon_section": "bx-book",
            "icon_card": "bxs-book-reader",
            "map_legend": "图书馆",
            "noun_singular": "图书馆",
            "noun_plural": "图书馆",
            "theme_primary": "#4a6fa5", # 蓝色系
            "theme_primary_light": "#6e8fc5",
            "theme_primary_dark": "#305182",
            "theme_secondary": "#9dc0e5",
            "theme_light": "#f0f5fa",
            "theme_dark": "#2c3e50",
        },
        "餐厅": {
            "topic": "美食汇",
            "icon_header": "bxs-restaurant",
            "icon_section": "bx-restaurant",
            "icon_card": "bxs-restaurant",
            "map_legend": "餐厅",
            "noun_singular": "餐厅",
            "noun_plural": "餐厅",
            "theme_primary": "#e74c3c", # 红色系
            "theme_primary_light": "#f1948a",
            "theme_primary_dark": "#c0392b",
            "theme_secondary": "#fadbd8",
            "theme_light": "#fef5e7",
            "theme_dark": "#34222e",
        },
        "商场": {
            "topic": "乐购汇",
            "icon_header": "bxs-shopping-bag",
            "icon_section": "bx-shopping-bag",
            "icon_card": "bxs-store-alt",
            "map_legend": "商场",
            "noun_singular": "商场",
            "noun_plural": "商场",
            "theme_primary": "#8e44ad", # 紫色系
            "theme_primary_light": "#af7ac5",
            "theme_primary_dark": "#6c3483",
            "theme_secondary": "#d7bde2",
            "theme_light": "#f4ecf7",
            "theme_dark": "#3b1f2b",
        },
        "公园": {
            "topic": "悠然汇",
            "icon_header": "bxs-tree",
            "icon_section": "bx-leaf",
            "icon_card": "bxs-florist",
            "map_legend": "公园",
            "noun_singular": "公园",
            "noun_plural": "公园",
            "theme_primary": "#27ae60", # 绿色系
            "theme_primary_light": "#58d68d",
            "theme_primary_dark": "#1e8449",
            "theme_secondary": "#a9dfbf",
            "theme_light": "#eafaf1",
            "theme_dark": "#1e3b20",
        },
        "电影院": {
            "topic": "光影汇",
            "icon_header": "bxs-film",
            "icon_section": "bx-film",
            "icon_card": "bxs-movie-play",
            "map_legend": "电影院",
            "noun_singular": "电影院",
            "noun_plural": "电影院",
            "theme_primary": "#34495e", # 深蓝灰色系
            "theme_primary_light": "#5d6d7e",
            "theme_primary_dark": "#2c3e50",
            "theme_secondary": "#aeb6bf",
            "theme_light": "#ebedef",
            "theme_dark": "#17202a",
        },        "篮球场": {
            "topic": "篮球部落",
            "icon_header": "bxs-basketball",
            "icon_section": "bx-basketball",
            "icon_card": "bxs-basketball",
            "map_legend": "篮球场",
            "noun_singular": "篮球场",
            "noun_plural": "篮球场",
            "theme_primary": "#f39c12", # 橙色系
            "theme_primary_light": "#f8c471",
            "theme_primary_dark": "#d35400",
            "theme_secondary": "#fdebd0",
            "theme_light": "#fef9e7",
            "theme_dark": "#4a2303",
        },
        "KTV": {
            "topic": "嗨歌汇",
            "icon_header": "bxs-microphone",
            "icon_section": "bx-microphone",
            "icon_card": "bxs-music",
            "map_legend": "KTV",
            "noun_singular": "KTV",
            "noun_plural": "KTV",
            "theme_primary": "#e91e63", # 玫红色系
            "theme_primary_light": "#f06292",
            "theme_primary_dark": "#c2185b",
            "theme_secondary": "#f8bbd9",
            "theme_light": "#fce4ec",
            "theme_dark": "#3e1929",
        },
        "茶楼": {
            "topic": "品茗雅聚",
            "icon_header": "bxs-coffee-togo",
            "icon_section": "bx-coffee",
            "icon_card": "bxs-coffee-bean",
            "map_legend": "茶楼",
            "noun_singular": "茶楼",
            "noun_plural": "茶楼",
            "theme_primary": "#4caf50", # 茶绿色系
            "theme_primary_light": "#81c784",
            "theme_primary_dark": "#388e3c",
            "theme_secondary": "#c8e6c9",
            "theme_light": "#e8f5e8",
            "theme_dark": "#1b5e20",
        },
        "健身房": {
            "topic": "健康活力汇",
            "icon_header": "bxs-dumbbell",
            "icon_section": "bx-dumbbell",
            "icon_card": "bxs-heart-circle",
            "map_legend": "健身房",
            "noun_singular": "健身房",
            "noun_plural": "健身房",
            "theme_primary": "#ff5722", # 橙红色系
            "theme_primary_light": "#ff8a65",
            "theme_primary_dark": "#d84315",
            "theme_secondary": "#ffccbc",
            "theme_light": "#fff3e0",
            "theme_dark": "#3e2723",
        },
        "博物馆": {
            "topic": "文化探索汇",
            "icon_header": "bxs-building",
            "icon_section": "bx-building",
            "icon_card": "bxs-castle",
            "map_legend": "博物馆",
            "noun_singular": "博物馆",
            "noun_plural": "博物馆",
            "theme_primary": "#795548", # 棕褐色系
            "theme_primary_light": "#a1887f",
            "theme_primary_dark": "#5d4037",
            "theme_secondary": "#d7ccc8",
            "theme_light": "#efebe9",
            "theme_dark": "#3e2723",
        },
        "购物中心": {
            "topic": "购物狂欢汇",
            "icon_header": "bxs-shopping-bags",
            "icon_section": "bx-shopping-bag",
            "icon_card": "bxs-gift",
            "map_legend": "购物中心",
            "noun_singular": "购物中心",
            "noun_plural": "购物中心",
            "theme_primary": "#9c27b0", # 紫色系
            "theme_primary_light": "#ba68c8",
            "theme_primary_dark": "#7b1fa2",
            "theme_secondary": "#e1bee7",
            "theme_light": "#f3e5f5",
            "theme_dark": "#4a148c",
        },
        "书店": {
            "topic": "书香墨韵汇",
            "icon_header": "bxs-book-open",
            "icon_section": "bx-book-open",
            "icon_card": "bxs-book-content",
            "map_legend": "书店",
            "noun_singular": "书店",
            "noun_plural": "书店",
            "theme_primary": "#607d8b", # 蓝灰色系
            "theme_primary_light": "#90a4ae",
            "theme_primary_dark": "#455a64",
            "theme_secondary": "#cfd8dc",
            "theme_light": "#eceff1",
            "theme_dark": "#263238",
        },
        "酒吧": {
            "topic": "夜色微醺汇",
            "icon_header": "bxs-wine",
            "icon_section": "bx-wine",
            "icon_card": "bxs-drink",
            "map_legend": "酒吧",
            "noun_singular": "酒吧",
            "noun_plural": "酒吧",
            "theme_primary": "#673ab7", # 深紫色系
            "theme_primary_light": "#9575cd",
            "theme_primary_dark": "#512da8",
            "theme_secondary": "#d1c4e9",
            "theme_light": "#ede7f6",
            "theme_dark": "#311b92",
        },
        "游乐场": {
            "topic": "童心嘉年华",
            "icon_header": "bxs-game",
            "icon_section": "bx-game",
            "icon_card": "bxs-carousel",
            "map_legend": "游乐场",
            "noun_singular": "游乐场",
            "noun_plural": "游乐场",
            "theme_primary": "#ff9800", # 橙黄色系
            "theme_primary_light": "#ffb74d",
            "theme_primary_dark": "#f57c00",
            "theme_secondary": "#ffe0b2",
            "theme_light": "#fff3e0",
            "theme_dark": "#e65100",
        },
        "spa会所": {
            "topic": "身心放松汇",
            "icon_header": "bxs-spa",
            "icon_section": "bx-spa",
            "icon_card": "bxs-leaf",
            "map_legend": "spa会所",
            "noun_singular": "spa会所",
            "noun_plural": "spa会所",
            "theme_primary": "#00bcd4", # 青蓝色系
            "theme_primary_light": "#4dd0e1",
            "theme_primary_dark": "#0097a7",
            "theme_secondary": "#b2ebf2",
            "theme_light": "#e0f2f1",
            "theme_dark": "#006064",
        },
        "美容院": {
            "topic": "美丽焕颜汇",
            "icon_header": "bxs-face-mask",
            "icon_section": "bx-face-mask",
            "icon_card": "bxs-heart",
            "map_legend": "美容院",
            "noun_singular": "美容院",
            "noun_plural": "美容院",
            "theme_primary": "#ff4081", # 粉红色系
            "theme_primary_light": "#ff80ab",
            "theme_primary_dark": "#c60055",
            "theme_secondary": "#f8bbd9",
            "theme_light": "#fce4ec",
            "theme_dark": "#880e4f",
        },
        "default": { # 默认主题颜色 (同咖啡馆)
            "topic": "会面点",
            "icon_header": "bxs-map-pin",
            "icon_section": "bx-map-pin",
            "icon_card": "bxs-location-plus",
            "map_legend": "场所",
            "noun_singular": "场所",
            "noun_plural": "场所",
            "theme_primary": "#9c6644",
            "theme_primary_light": "#c68b59",
            "theme_primary_dark": "#7f5539",
            "theme_secondary": "#c9ada7",
            "theme_light": "#f2e9e4",
            "theme_dark": "#22223b",
        }
    }

    def _get_place_config(self, primary_keyword: str) -> Dict[str, str]:
        """获取指定场所类型的显示配置"""
        return self.PLACE_TYPE_CONFIG.get(primary_keyword, self.PLACE_TYPE_CONFIG["default"])

    async def execute(
        self,
        locations: List[str],
        keywords: str = "咖啡馆",
        place_type: str = "",
        user_requirements: str = "",
        min_rating: float = 0,
        max_distance: int = 10000,
        price_range: str = "",
        limit: int = 5,
    ) -> ToolResult:
        if hasattr(config._config, "amap") and hasattr(config._config.amap, "api_key"):
            self.api_key = config._config.amap.api_key
        
        if not self.api_key:
            logger.error("高德地图API密钥未配置。请在config.yml中设置 amap.api_key。")
            return ToolResult(output="推荐失败: 高德地图API密钥未配置。")

        try:
            coordinates = []
            location_info = []
            for location in locations:
                geocode_result = await self._geocode(location)
                if not geocode_result:
                    return ToolResult(output=f"无法找到地点: {location}")
                lng, lat = geocode_result["location"].split(",")
                coordinates.append((float(lng), float(lat)))
                location_info.append({
                    "name": location,
                    "formatted_address": geocode_result.get("formatted_address", location),
                    "location": geocode_result["location"],
                    "lng": float(lng),
                    "lat": float(lat)
                })

            if not coordinates:
                return ToolResult(output="未能解析任何有效地点。")

            center_point = self._calculate_center_point(coordinates)
            
            searched_places = await self._search_pois(
                f"{center_point[0]},{center_point[1]}",
                keywords, 
                radius=5000,
                types=place_type 
            )

            if not searched_places:
                logger.info(f"使用 keywords '{keywords}' 和 types '{place_type}' 未找到结果，尝试仅使用 keywords 进行搜索。")
                searched_places = await self._search_pois(
                    f"{center_point[0]},{center_point[1]}",
                    keywords,
                    radius=5000,
                    types="" 
                )
                if not searched_places:
                     return ToolResult(output=f"在计算的中心点附近找不到与 '{keywords}' 相关的场所。")

            recommended_places = self._rank_places(searched_places, center_point, user_requirements, keywords)

            html_path = await self._generate_html_page(
                location_info,
                recommended_places,
                center_point,
                user_requirements,
                keywords 
            )
            result_text = self._format_result_text(location_info, recommended_places, html_path, keywords) 
            return ToolResult(output=result_text)

        except Exception as e:
            logger.exception(f"场所推荐过程中发生错误: {str(e)}") 
            return ToolResult(output=f"推荐失败: {str(e)}")

    async def _geocode(self, address: str) -> Optional[Dict[str, Any]]:
        if address in self.geocode_cache:
            return self.geocode_cache[address]
        url = "https://restapi.amap.com/v3/geocode/geo"
        params = {"key": self.api_key, "address": address, "output": "json"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"高德地图API地理编码请求失败: {response.status}, 地址: {address}")
                    return None
                data = await response.json()
                if data["status"] != "1" or not data["geocodes"]:
                    logger.error(f"地理编码失败: {data.get('info', '未知错误')}, 地址: {address}")
                    return None
                result = data["geocodes"][0]
                self.geocode_cache[address] = result
                return result

    def _calculate_center_point(self, coordinates: List[Tuple[float, float]]) -> Tuple[float, float]:
        if not coordinates:
            raise ValueError("至少需要一个坐标来计算中心点。")
        avg_lng = sum(lng for lng, _ in coordinates) / len(coordinates)
        avg_lat = sum(lat for _, lat in coordinates) / len(coordinates)
        return (avg_lng, avg_lat)

    async def _search_pois(
        self,
        location: str,
        keywords: str,
        radius: int = 2000,
        types: str = "", 
        offset: int = 20
    ) -> List[Dict]:
        cache_key = f"{location}_{keywords}_{radius}_{types}"
        if cache_key in self.poi_cache:
            return self.poi_cache[cache_key]
        url = "https://restapi.amap.com/v3/place/around"
        params = {
            "key": self.api_key,
            "location": location,
            "keywords": keywords,
            "radius": radius,
            "offset": offset,
            "page": 1,
            "extensions": "all"
        }
        if types: 
            params["types"] = types

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"高德地图POI搜索失败: {response.status}, 参数: {params}")
                    return []
                data = await response.json()                if data["status"] != "1":
                    logger.error(f"POI搜索API返回错误: {data.get('info', '未知错误')}, 参数: {params}")
                    return []
                pois = data.get("pois", [])
                self.poi_cache[cache_key] = pois
                return pois

    def _rank_places(
        self,
        places: List[Dict], 
        center_point: Tuple[float, float],
        user_requirements: str,
        keywords: str,
        min_rating: float = 0,
        max_distance: int = 10000,
        price_range: str = "",
        limit: int = 5
    ) -> List[Dict]:
        """优化的场所排序算法，支持多维度筛选"""
        
        # 用户需求关键词映射（优化版）
        requirement_keywords_map = {
            "停车": ["停车", "车位", "停车场", "免费停车"],
            "安静": ["安静", "环境好", "氛围", "清静", "舒适"],
            "商务": ["商务", "会议", "办公", "洽谈", "工作"],
            "交通": ["交通", "地铁", "公交", "便利", "出行"],
            "WiFi": ["wifi", "网络", "上网", "无线"],
            "24小时": ["24小时", "全天", "不打烊", "营业时间长"]
        }
        
        user_priorities = []
        for key, kw_list in requirement_keywords_map.items():
            if any(kw in user_requirements.lower() for kw in kw_list):
                user_priorities.append(key)

        # 价格范围映射
        price_score_map = {
            "low": {"低消费": 3, "经济": 2, "实惠": 2},
            "mid": {"中等": 3, "适中": 2, "合理": 2},
            "high": {"高端": 3, "奢华": 2, "精品": 2}
        }

        filtered_places = []
        
        for place in places:
            # 基础评分计算（优化版）
            score = 0
            
            # 1. 评分权重 (40%)
            rating = float(place.get("biz_ext", {}).get("rating", "0") or "0")
            if rating >= min_rating:
                score += rating * 20  # 提高评分权重
            else:
                continue  # 跳过不满足评分要求的场所

            # 2. 距离权重 (30%)
            place_lng_str, place_lat_str = place.get("location", "").split(",")
            if not place_lng_str or not place_lat_str: 
                continue  # 跳过没有坐标的场所

            place_lng, place_lat = float(place_lng_str), float(place_lat_str)
            distance = self._calculate_distance(center_point, (place_lng, place_lat))
            
            if distance <= max_distance:
                # 距离越近分数越高
                distance_score = max(0, 30 - (distance / max_distance) * 30)
                score += distance_score
            else:
                continue  # 跳过超出距离范围的场所

            # 3. 价格匹配权重 (15%)
            if price_range and price_range in price_score_map:
                price_keywords = price_score_map[price_range]
                place_name = place.get("name", "").lower()
                place_address = place.get("address", "").lower()
                for price_kw, bonus in price_keywords.items():
                    if price_kw in place_name or price_kw in place_address:
                        score += bonus

            # 4. 用户需求匹配权重 (10%)
            place_name = place.get("name", "").lower()
            place_address = place.get("address", "").lower()
            tags = place.get("tag", [])
            if isinstance(tags, str):
                tags = tags.split(";") if tags else []
            
            all_text = f"{place_name} {place_address} {' '.join(tags)}".lower()
            
            for priority in user_priorities:
                keywords_list = requirement_keywords_map[priority]
                for kw in keywords_list:
                    if kw in all_text:
                        score += 2  # 每个匹配的需求加2分

            # 5. 关键词匹配权重 (5%)
            if keywords.lower() in all_text:
                score += 3

            place["_score"] = score
            place["_distance"] = distance
            filtered_places.append(place)

        # 按评分排序并返回前limit个
        filtered_places.sort(key=lambda x: x["_score"], reverse=True)
        return filtered_places[:limit]

            place_lng, place_lat = float(place_lng_str), float(place_lat_str)
            distance = self._calculate_distance(center_point, (place_lng, place_lat))
            distance_score = max(0, 20 * (1 - (distance / 2000))) 
            score += distance_score

            for priority in user_priorities:
                if priority == "停车" and ("停车" in place.get("tag", "") or "免费停车" in place.get("parking_type", "")): 
                    score += 10
                elif priority == "安静" and ("安静" in place.get("tag", "") or "环境" in place.get("tag", "")):
                    score += 10
                elif priority == "商务" and ("商务" in place.get("tag", "") or "会议" in place.get("tag", "")): 
                    score += 10
                elif priority == "交通" and ("地铁" in place.get("tag", "") or "公交" in place.get("tag", "")):
                    score += 10
            place["_score"] = score
        
        ranked_places = sorted(places, key=lambda x: x.get("_score", 0), reverse=True)
        return ranked_places[:5]


    def _calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        lng1, lat1 = point1
        lng2, lat2 = point2
        x = (lng2 - lng1) * 85000 
        y = (lat2 - lat1) * 111000 
        return math.sqrt(x*x + y*y)

    async def _generate_html_page(
        self,
        locations: List[Dict],
        places: List[Dict], 
        center_point: Tuple[float, float],
        user_requirements: str,
        keywords: str 
    ) -> str:
        file_name_prefix = "place"
        
        html_content = self._generate_html_content(locations, places, center_point, user_requirements, keywords)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_name = f"{file_name_prefix}_recommendation_{timestamp}_{unique_id}.html"
        
        workspace_js_src_path = os.path.join("workspace", "js_src")
        os.makedirs(workspace_js_src_path, exist_ok=True)
        file_path = os.path.join(workspace_js_src_path, file_name)

        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(html_content)
        return file_path 

    def _generate_html_content(
        self,
        locations: List[Dict],
        places: List[Dict], 
        center_point: Tuple[float, float],
        user_requirements: str,
        keywords: str 
    ) -> str:
        primary_keyword = keywords.split("、")[0] if keywords else "场所"
        cfg = self._get_place_config(primary_keyword)

        search_process_html = self._generate_search_process(locations, center_point, user_requirements, keywords) 

        location_markers = []
        for idx, loc in enumerate(locations):
            location_markers.append({
                "name": f"地点{idx+1}: {loc['name']}",
                "position": [loc["lng"], loc["lat"]],
                "icon": "location"
            })

        place_markers = [] 
        for place in places:
            lng_str, lat_str = place.get("location", ",").split(",")
            if lng_str and lat_str:
                place_markers.append({
                    "name": place["name"],
                    "position": [float(lng_str), float(lat_str)],
                    "icon": "place" 
                })

        center_marker = {
            "name": "最佳会面点",
            "position": [center_point[0], center_point[1]],
            "icon": "center"
        }
        all_markers = [center_marker] + location_markers + place_markers

        location_rows_html = ""
        for idx, loc in enumerate(locations):
            location_rows_html += f"<tr><td>{idx+1}</td><td>{loc['name']}</td><td>{loc['formatted_address']}</td></tr>"

        location_distance_html = ""
        for loc in locations:
            distance = self._calculate_distance(center_point, (loc['lng'], loc['lat']))/1000
            location_distance_html += f"<li><i class='bx bx-map'></i><strong>{loc['name']}</strong>: 距离中心点约 <span class='distance'>{distance:.1f} 公里</span></li>"

        place_cards_html = "" 
        for place in places:
            rating = place.get("biz_ext", {}).get("rating", "暂无评分")
            address = place.get("address", "地址未知")
            business_hours = place.get("business_hours", "营业时间未知")
            if isinstance(business_hours, list) and business_hours:
                business_hours = "; ".join(business_hours)
            tel = place.get("tel", "电话未知")
            
            tags = place.get("tag", [])
            if isinstance(tags, str): tags = tags.split(";") if tags else []
            elif not isinstance(tags, list): tags = []
            
            tags_html = "".join([f"<span class='cafe-tag'>{tg.strip()}</span>" for tg in tags if tg.strip()])
            if not tags_html: 
                tags_html = f"<span class='cafe-tag'>{cfg['noun_singular']}</span>"

            lng_str, lat_str = place.get("location",",").split(",")
            distance_text = "未知距离"
            map_link_coords = ""
            if lng_str and lat_str:
                lng, lat = float(lng_str), float(lat_str)
                distance = self._calculate_distance(center_point, (lng, lat))
                distance_text = f"{distance/1000:.1f} 公里"
                map_link_coords = f"{lng},{lat}"

            place_cards_html += f'''
            <div class="cafe-card"> 
                <div class="cafe-img">
                    <i class='bx {cfg["icon_card"]}'></i> 
                </div>
                <div class="cafe-content">
                    <div class="cafe-header">
                        <div>
                            <h3 class="cafe-name">{place['name']}</h3>
                        </div>
                        <span class="cafe-rating">评分: {rating}</span>
                    </div>
                    <div class="cafe-details">
                        <div class="cafe-info">
                            <i class='bx bx-map'></i>
                            <div class="cafe-info-text">{address}</div>
                        </div>
                        <div class="cafe-info">
                            <i class='bx bx-time'></i>
                            <div class="cafe-info-text">{business_hours}</div>
                        </div>
                        <div class="cafe-info">
                            <i class='bx bx-phone'></i>
                            <div class="cafe-info-text">{tel}</div>
                        </div>
                        <div class="cafe-tags">
                            {tags_html}
                        </div>
                    </div>
                    <div class="cafe-footer">
                        <div class="cafe-distance">
                            <i class='bx bx-walk'></i> {distance_text}
                        </div>
                        <div class="cafe-actions">
                            <a href="https://uri.amap.com/marker?position={map_link_coords}&name={place['name']}" target="_blank">
                                <i class='bx bx-navigation'></i>导航
                            </a>
                        </div>
                    </div>
                </div>
            </div>'''
        markers_json = json.dumps(all_markers)

        amap_security_js_code = ""
        if hasattr(config, 'amap') and hasattr(config.amap, 'security_js_code') and config.amap.security_js_code:
            amap_security_js_code = config.amap.security_js_code

        # Dynamically set CSS variables for theme colors
        dynamic_style = f"""
        :root {{
            --primary: {cfg.get("theme_primary", "#9c6644")}; 
            --primary-light: {cfg.get("theme_primary_light", "#c68b59")};
            --primary-dark: {cfg.get("theme_primary_dark", "#7f5539")};
            --secondary: {cfg.get("theme_secondary", "#c9ada7")};
            --light: {cfg.get("theme_light", "#f2e9e4")};
            --dark: {cfg.get("theme_dark", "#22223b")};
            --success: #4a934a; /* Success color can remain static or be themed */
            --border-radius: 12px;
            --box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
            --transition: all 0.3s ease;
        }}"""

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{cfg["topic"]} - 最佳会面{cfg["noun_singular"]}推荐</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/boxicons@2.0.9/css/boxicons.min.css">
    <style>
        {dynamic_style} /* Inject dynamic theme colors here */

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; line-height: 1.6; background-color: var(--light); color: var(--dark); padding-bottom: 50px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        header {{ background-color: var(--primary); color: white; padding: 60px 0 100px; text-align: center; position: relative; margin-bottom: 80px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); }}
        header::after {{ content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 60px; background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 60"><path fill="{cfg.get("theme_light", "#f2e9e4")}" fill-opacity="1" d="M0,32L80,42.7C160,53,320,75,480,64C640,53,800,11,960,5.3C1120,0,1280,32,1360,48L1440,64L1440,100L1360,100C1280,100,1120,100,960,100C800,100,640,100,480,100C320,100,160,100,80,100L0,100Z"></path></svg>'); background-size: cover; background-position: center; }}
        .header-logo {{ font-size: 3rem; font-weight: 700; margin-bottom: 10px; letter-spacing: -1px; }}
        .coffee-icon {{ font-size: 3rem; vertical-align: middle; margin-right: 10px; }}
        .header-subtitle {{ font-size: 1.2rem; opacity: 0.9; }}
        .main-content {{ margin-top: -60px; }}
        .card {{ background-color: white; border-radius: var(--border-radius); padding: 30px; box-shadow: var(--box-shadow); margin-bottom: 30px; transition: var(--transition); }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1); }}
        .section-title {{ font-size: 1.8rem; color: var(--primary-dark); margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid var(--secondary); display: flex; align-items: center; }}
        .section-title i {{ margin-right: 12px; font-size: 1.6rem; color: var(--primary); }}
        .summary-card {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 15px; }}
        .summary-item {{ flex: 1; min-width: 200px; padding: 15px; background-color: rgba(0,0,0,0.03); /* Adjusted for better contrast with various themes */ border-radius: 8px; border-left: 4px solid var(--primary); }}
        .summary-label {{ font-size: 0.9rem; color: var(--primary-dark); margin-bottom: 5px; }}
        .summary-value {{ font-size: 1.2rem; font-weight: 600; color: var(--dark); }}
        .map-container {{ height: 500px; border-radius: var(--border-radius); overflow: hidden; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); position: relative; margin-bottom: 30px; }}
        #map {{ height: 100%; width: 100%; }}
        .map-legend {{ position: absolute; bottom: 15px; left: 15px; background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.15); z-index: 100; }}
        .legend-item {{ display: flex; align-items: center; margin-bottom: 8px; }}
        .legend-color {{ width: 20px; height: 20px; margin-right: 10px; border-radius: 50%; }}
        .legend-center {{ background-color: #2ecc71; }} 
        .legend-location {{ background-color: #3498db; }} 
        .legend-place {{ background-color: #e74c3c; }} 
        .location-table {{ width: 100%; border-collapse: collapse; border-radius: 8px; overflow: hidden; margin-bottom: 25px; box-shadow: 0 0 8px rgba(0, 0, 0, 0.1); }}
        .location-table th, .location-table td {{ padding: 15px; text-align: left; border-bottom: 1px solid #eee; }}
        .location-table th {{ background-color: var(--primary-light); color: white; font-weight: 600; }}
        .location-table tr:last-child td {{ border-bottom: none; }}
        .location-table tr:nth-child(even) {{ background-color: rgba(0,0,0,0.02); /* Adjusted for better contrast */ }}
        .cafe-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 25px; margin-top: 20px; }} 
        .cafe-card {{ background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08); transition: var(--transition); display: flex; flex-direction: column; }}
        .cafe-card:hover {{ transform: translateY(-10px); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15); }}
        .cafe-img {{ height: 180px; background-color: var(--primary-light); display: flex; align-items: center; justify-content: center; color: white; font-size: 3rem; }}
        .cafe-content {{ padding: 20px; flex: 1; display: flex; flex-direction: column; }}
        .cafe-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }}
        .cafe-name {{ font-size: 1.3rem; margin: 0 0 5px 0; color: var(--primary-dark); }}
        .cafe-rating {{ display: inline-block; background-color: var(--primary); color: white; padding: 5px 12px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; white-space: nowrap; }}
        .cafe-details {{ flex: 1; }}
        .cafe-info {{ margin-bottom: 12px; display: flex; align-items: flex-start; }}
        .cafe-info i {{ color: var(--primary); margin-right: 8px; font-size: 1.1rem; min-width: 20px; margin-top: 3px; }}
        .cafe-info-text {{ flex: 1; }}
        .cafe-tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 15px; }}
        .cafe-tag {{ background-color: rgba(0,0,0,0.05); /* Adjusted for better contrast */ color: var(--primary-dark); padding: 4px 10px; border-radius: 15px; font-size: 0.8rem; }}
        .cafe-footer {{ display: flex; align-items: center; justify-content: space-between; margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; }}
        .cafe-distance {{ display: flex; align-items: center; color: var(--primary-dark); font-weight: 600; }}
        .cafe-distance i {{ margin-right: 5px; }}
        .cafe-actions a {{ display: inline-flex; align-items: center; justify-content: center; background-color: var(--primary); color: white; padding: 8px 15px; border-radius: 6px; text-decoration: none; font-size: 0.9rem; transition: var(--transition); }}
        .cafe-actions a:hover {{ background-color: var(--primary-dark); transform: translateY(-2px); }}
        .cafe-actions i {{ margin-right: 5px; }}
        .transportation-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-top: 20px; }}
        .transport-card {{ background-color: white; border-radius: 12px; padding: 25px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05); border-top: 5px solid var(--primary); }}
        .transport-title {{ font-size: 1.3rem; color: var(--primary-dark); margin-bottom: 15px; display: flex; align-items: center; }}
        .transport-title i {{ margin-right: 10px; font-size: 1.4rem; color: var(--primary); }}
        .transport-list {{ list-style: none; margin: 0; padding: 0; }}
        .transport-list li {{ padding: 10px 0; border-bottom: 1px solid #eee; display: flex; align-items: center; }}
        .transport-list li:last-child {{ border-bottom: none; }}
        .transport-list i {{ color: var(--primary); margin-right: 10px; }}
        .center-coords {{ display: inline-block; background-color: rgba(0,0,0,0.05); /* Adjusted for better contrast */ border-radius: 6px; padding: 3px 8px; margin: 0 5px; font-family: monospace; font-size: 0.9rem; }}
        .footer {{ text-align: center; background-color: var(--primary-dark); color: white; padding: 20px 0; margin-top: 50px; }}
        .back-button {{ display: inline-flex; align-items: center; justify-content: center; background-color: white; color: var(--primary); border: 2px solid var(--primary); padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 1rem; transition: var(--transition); margin-top: 30px; }}
        .back-button:hover {{ background-color: var(--primary); color: white; transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); }}
        .back-button i {{ margin-right: 8px; }}
        .search-process-card {{ position: relative; overflow: hidden; background-color: #fafafa; border-left: 5px solid #2c3e50; }} /* Search process card can have static border */
        .search-process {{ position: relative; padding: 20px 0; }}
        .process-step {{ display: flex; margin-bottom: 30px; opacity: 0.5; transform: translateX(-20px); transition: opacity 0.5s ease, transform 0.5s ease; }}
        .process-step.active {{ opacity: 1; transform: translateX(0); }}
        .step-icon {{ flex: 0 0 60px; height: 60px; border-radius: 50%; background-color: var(--primary-light); display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; margin-right: 20px; position: relative; }}
        .step-number {{ position: absolute; top: -5px; right: -5px; width: 25px; height: 25px; border-radius: 50%; background-color: var(--primary-dark); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; }}
        .step-content {{ flex: 1; }}
        .step-title {{ font-size: 1.3rem; color: var(--primary-dark); margin-bottom: 10px; }}
        .step-details {{ background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.05); }}
        .code-block {{ background-color: #2c3e50; color: #e6e6e6; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.9rem; margin: 15px 0; white-space: pre; overflow-x: auto; }}
        .highlight-text {{ background-color: rgba(46, 204, 113, 0.2); color: #2c3e50; padding: 3px 6px; border-radius: 4px; font-weight: bold; }}
        .search-animation {{ height: 200px; position: relative; display: flex; align-items: center; justify-content: center; margin: 20px 0; }}
        .radar-circle {{ position: absolute; width: 50px; height: 50px; border-radius: 50%; background-color: rgba(52, 152, 219, 0.1); animation: radar 3s infinite; }}
        .radar-circle:nth-child(1) {{ animation-delay: 0s; }} .radar-circle:nth-child(2) {{ animation-delay: 1s; }} .radar-circle:nth-child(3) {{ animation-delay: 2s; }}
        .center-point {{ width: 15px; height: 15px; border-radius: 50%; background-color: #e74c3c; z-index: 2; box-shadow: 0 0 0 5px rgba(231, 76, 60, 0.3); }}
        .map-operation-animation {{ height: 200px; position: relative; border-radius: 8px; overflow: hidden; background-color: #f5f5f5; margin: 20px 0; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
        .map-bg {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23f0f0f0"/><path d="M0,0 L100,0 L100,100 L0,100 Z" fill="none" stroke="%23ccc" stroke-width="0.5"/><path d="M50,0 L50,100 M0,50 L100,50" stroke="%23ccc" stroke-width="0.5"/></svg>'); background-size: 50px 50px; opacity: 0.7; }}
        .map-cursor {{ position: absolute; width: 20px; height: 20px; background-color: rgba(231, 76, 60, 0.7); border-radius: 50%; top: 50%; left: 30%; transform: translate(-50%, -50%); animation: mapCursor 4s infinite ease-in-out; z-index: 2; }}
        .map-search-indicator {{ position: absolute; width: 80px; height: 80px; border: 2px dashed rgba(52, 152, 219, 0.6); border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%); animation: mapSearch 3s infinite ease-in-out; z-index: 1; }}
        @keyframes mapCursor {{ 0% {{ left: 30%; top: 30%; }} 30% {{ left: 60%; top: 40%; }} 60% {{ left: 40%; top: 70%; }} 100% {{ left: 30%; top: 30%; }} }}
        @keyframes mapSearch {{ 0% {{ width: 30px; height: 30px; opacity: 1; }} 100% {{ width: 150px; height: 150px; opacity: 0; }} }}
        @keyframes radar {{ 0% {{ width: 40px; height: 40px; opacity: 1; }} 100% {{ width: 300px; height: 300px; opacity: 0; }} }}
        .ranking-result {{ margin-top: 15px; }}
        .result-bar {{ height: 30px; background-color: var(--primary); color: white; margin-bottom: 8px; border-radius: 15px; padding: 0 15px; display: flex; align-items: center; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.1); animation: growBar 2s ease; transform-origin: left; }}
        @keyframes growBar {{ 0% {{ width: 0; }} 100% {{ width: 100%; }} }}
        .mt-4 {{ margin-top: 1rem; }}
        @media (max-width: 768px) {{ .cafe-grid {{ grid-template-columns: 1fr; }} .transportation-info {{ grid-template-columns: 1fr; }} header {{ padding: 40px 0 80px; }} .header-logo {{ font-size: 2.2rem; }} .process-step {{ flex-direction: column; }} .step-icon {{ margin-bottom: 15px; margin-right: 0; }} }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-logo">
                <i class='bx {cfg["icon_header"]} coffee-icon'></i>{cfg["topic"]}
            </div>
            <div class="header-subtitle">为您找到的最佳会面{cfg["noun_plural"]}</div>
        </div>
    </header>

    <div class="container main-content">
        <div class="card">
            <h2 class="section-title"><i class='bx bx-info-circle'></i>推荐摘要</h2>
            <div class="summary-card">
                <div class="summary-item">
                    <div class="summary-label">参与地点数</div>
                    <div class="summary-value">{len(locations)} 个地点</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">推荐{cfg["noun_plural"]}数</div>
                    <div class="summary-value">{len(places)} 家{cfg["noun_plural"]}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">特殊需求</div>
                    <div class="summary-value">{user_requirements or "无特殊需求"}</div>
                </div>
            </div>
        </div>
        {search_process_html}
        <div class="card">
            <h2 class="section-title"><i class='bx bx-map-pin'></i>地点信息</h2>
            <table class="location-table">
                <thead><tr><th>序号</th><th>地点名称</th><th>详细地址</th></tr></thead>
                <tbody>{location_rows_html}</tbody>
            </table>
        </div>
        <div class="card">
            <h2 class="section-title"><i class='bx bx-map-alt'></i>地图展示</h2>
            <div class="map-container">
                <div id="map"></div>
                <div class="map-legend">
                    <div class="legend-item"><div class="legend-color legend-center"></div><span>最佳会面点</span></div>
                    <div class="legend-item"><div class="legend-color legend-location"></div><span>所在地点</span></div>
                    <div class="legend-item"><div class="legend-color legend-place"></div><span>{cfg["map_legend"]}</span></div>
                </div>
            </div>
        </div>
        <div class="card">
            <h2 class="section-title"><i class='bx {cfg["icon_section"]}'></i>推荐{cfg["noun_plural"]}</h2>
            <div class="cafe-grid">
                {place_cards_html}
            </div>
        </div>
        <div class="card">
            <h2 class="section-title"><i class='bx bx-car'></i>交通与停车建议</h2>
            <div class="transportation-info">
                <div class="transport-card">
                    <h3 class="transport-title"><i class='bx bx-trip'></i>前往方式</h3>
                    <p>最佳会面点位于<span class="center-coords">{center_point[0]:.6f}, {center_point[1]:.6f}</span>附近</p>
                    <ul class="transport-list">{location_distance_html}</ul>
                </div>
                <div class="transport-card">
                    <h3 class="transport-title"><i class='bx bxs-car-garage'></i>停车建议</h3>
                    <ul class="transport-list">
                        <li><i class='bx bx-check'></i>大部分推荐的{cfg["noun_plural"]}周边有停车场或提供停车服务</li>
                        <li><i class='bx bx-check'></i>建议使用高德地图或百度地图导航到目的地</li>
                        <li><i class='bx bx-check'></i>高峰时段建议提前30分钟出发，以便寻找停车位</li>
                        <li><i class='bx bx-check'></i>部分{cfg["noun_plural"]}可能提供免费停车或停车优惠</li>
                    </ul>
                </div>
            </div>
            <a href="/workspace/meetspot_finder.html" class="back-button"> 
                <i class='bx bx-left-arrow-alt'></i>返回首页
            </a>
        </div>
    </div>
    <footer class="footer">
        <div class="container">
            <p>© {datetime.now().year} {cfg["topic"]} - 智能{cfg["noun_singular"]}推荐服务 | 数据来源：高德地图</p>
        </div>
    </footer>
    <script type="text/javascript">
        var markersData = {markers_json};
        window._AMapSecurityConfig = {{ securityJsCode: "{amap_security_js_code}" }};
        window.onload = function() {{
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.src = 'https://webapi.amap.com/loader.js';
            script.onload = function() {{
                AMapLoader.load({{
                    key: "{self.api_key}", 
                    version: "2.0",
                    plugins: ["AMap.Scale", "AMap.ToolBar"],
                    AMapUI: {{ version: "1.1", plugins: ["overlay/SimpleMarker"] }}
                }})
                .then(function(AMap) {{ initMap(AMap); }})
                .catch(function(e) {{ console.error('地图加载失败:', e); }});
            }};
            document.body.appendChild(script);
            animateCafeCards(); 
        }};
        function initMap(AMap) {{
            var map = new AMap.Map('map', {{
                zoom: 12, center: [{center_point[0]}, {center_point[1]}],
                resizeEnable: true, viewMode: '3D'
            }});
            map.addControl(new AMap.ToolBar()); map.addControl(new AMap.Scale());
            var mapMarkers = []; 
            markersData.forEach(function(item) {{
                var markerContent, position = new AMap.LngLat(item.position[0], item.position[1]);
                var color = '#e74c3c'; 
                if (item.icon === 'center') color = '#2ecc71'; 
                else if (item.icon === 'location') color = '#3498db'; 
                
                markerContent = `<div style="background-color: ${{color}}; width: 24px; height: 24px; border-radius: 12px; border: 2px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.3);"></div>`;
                
                var marker = new AMap.Marker({{
                    position: position, content: markerContent,
                    title: item.name, anchor: 'center', offset: new AMap.Pixel(0, 0)
                }});
                var infoWindow = new AMap.InfoWindow({{
                    content: '<div style="padding:10px;font-size:14px;">' + item.name + '</div>',
                    offset: new AMap.Pixel(0, -12)
                }});
                marker.on('click', function() {{ infoWindow.open(map, marker.getPosition()); }});
                mapMarkers.push(marker);
                marker.setMap(map);
            }});
            if (markersData.length > 1) {{
                var pathCoordinates = [];
                markersData.filter(item => item.icon !== 'place').forEach(function(item) {{ 
                    pathCoordinates.push(new AMap.LngLat(item.position[0], item.position[1]));
                }});
                if (pathCoordinates.length > 1) {{ 
                    var polyline = new AMap.Polyline({{
                        path: pathCoordinates, strokeColor: '#3498db', strokeWeight: 4,
                        strokeStyle: 'dashed', strokeDasharray: [5, 5], lineJoin: 'round'
                    }});
                    polyline.setMap(map);
                }}
            }}
            if (mapMarkers.length > 0) {{ 
                 map.setFitView(mapMarkers);
            }}
        }}
        function animateCafeCards() {{
            const cards = document.querySelectorAll('.cafe-card');
            if ('IntersectionObserver' in window) {{
                const observer = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            entry.target.style.opacity = 1;
                            entry.target.style.transform = 'translateY(0)';
                            observer.unobserve(entry.target);
                        }}
                    }});
                }}, {{ threshold: 0.1 }});
                cards.forEach((card, index) => {{
                    card.style.opacity = 0; card.style.transform = 'translateY(30px)';
                    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    card.style.transitionDelay = (index * 0.1) + 's';
                    observer.observe(card);
                }});
            }} else {{
                cards.forEach((card, index) => {{
                    card.style.opacity = 0; card.style.transform = 'translateY(30px)';
                    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    setTimeout(() => {{ card.style.opacity = 1; card.style.transform = 'translateY(0)'; }}, 300 + (index * 100));
                }});
            }}
        }}
    </script>
</body>
</html>"""
        return html

    def _format_result_text(
        self,
        locations: List[Dict],
        places: List[Dict], 
        html_path: str,
        keywords: str 
    ) -> str:
        primary_keyword = keywords.split("、")[0] if keywords else "场所"
        cfg = self._get_place_config(primary_keyword)
        num_places = len(places)

        result = [
            f"## 已为您找到{num_places}家适合会面的{cfg['noun_plural']}", 
            "",
            f"### 推荐{cfg['noun_plural']}:", 
        ]
        for i, place in enumerate(places):
            rating = place.get("biz_ext", {}).get("rating", "暂无评分")
            address = place.get("address", "地址未知")
            result.append(f"{i+1}. **{place['name']}** (评分: {rating})")
            result.append(f"   地址: {address}")
            result.append("")
        
        html_file_basename = os.path.basename(html_path)
        result.append(f"HTML页面: {html_file_basename}") 
        result.append(f"可在浏览器中打开查看详细地图和{cfg['noun_plural']}信息。") 

        return "\n".join(result)

    def _generate_search_process(
        self,
        locations: List[Dict],
        center_point: Tuple[float, float],
        user_requirements: str,
        keywords: str 
    ) -> str:
        primary_keyword = keywords.split("、")[0] if keywords else "场所"
        cfg = self._get_place_config(primary_keyword)
        search_steps = []

        location_analysis = "<ul>"
        for idx, loc in enumerate(locations):
            location_analysis += f"<li>分析位置 {idx+1}: <strong>{loc['name']}</strong></li>"
        location_analysis += "</ul>"
        search_steps.append({
            "icon": "bx-map-pin", "title": "分析用户位置信息",
            "content": f"<p>我检测到{len(locations)}个不同的位置。正在分析它们的地理分布...</p>{location_analysis}"
        })

        search_steps.append({
            "icon": "bx-map", "title": f"正在操作高德地图寻找最佳{cfg['noun_singular']}的位置...", 
            "content": f"""
            <p>正在操作高德地图寻找最佳{cfg['noun_singular']}的位置...</p> 
            <div class="map-operation-animation">
                <div class="map-bg"></div> <div class="map-cursor"></div> <div class="map-search-indicator"></div>
            </div>"""
        })

        requirement_analysis = ""
        if user_requirements:
            requirement_keywords_map = {
                "停车": ["停车", "车位", "停车场"], "安静": ["安静", "环境好", "氛围"],
                "商务": ["商务", "会议", "办公"], "交通": ["交通", "地铁", "公交"]
            }
            detected_requirements = [key for key, kw_list in requirement_keywords_map.items() if any(kw in user_requirements for kw in kw_list)]
            if detected_requirements:
                requirement_analysis = "<p>我从您的需求中检测到以下关键偏好:</p><ul>" + "".join([f"<li><strong>{req}</strong>: 将优先考虑{req}便利的{cfg['noun_plural']}</li>" for req in detected_requirements]) + "</ul>" 
            else:
                requirement_analysis = f"<p>您没有提供特定的需求偏好，将基于综合评分和距离推荐最佳{cfg['noun_plural']}。</p>" 
        else:
            requirement_analysis = f"<p>未提供特殊需求，将根据评分和位置便利性进行推荐{cfg['noun_plural']}。</p>" 
        search_steps.append({"icon": "bx-list-check", "title": "分析用户特殊需求", "content": requirement_analysis})

        search_places_explanation = f"""
        <p>我正在以最佳会面点为中心，搜索周边2公里范围内的{cfg['noun_plural']}...</p> 
        <div class="search-animation">
            <div class="radar-circle"></div> <div class="radar-circle"></div> <div class="radar-circle"></div>
            <div class="center-point"></div>
        </div>"""
        search_steps.append({"icon": "bx-search-alt", "title": f"搜索周边{cfg['noun_plural']}", "content": search_places_explanation}) 

        ranking_explanation = f"""
        <p>我已找到多家{cfg['noun_plural']}，正在根据综合评分对它们进行排名...</p> 
        <div class="ranking-result">
            <div class="result-bar" style="width: 95%;">{cfg['noun_singular']}评分</div> 
            <div class="result-bar" style="width: 85%;">距离便利性</div>
            <div class="result-bar" style="width: 75%;">环境舒适度</div>
            <div class="result-bar" style="width: 65%;">交通便利性</div>
        </div>"""
        search_steps.append({"icon": "bx-sort", "title": f"对{cfg['noun_plural']}进行排名", "content": ranking_explanation}) 

        search_process_html = ""
        for idx, step in enumerate(search_steps):
            search_process_html += f"""
            <div class="process-step" data-step="{idx+1}">
                <div class="step-icon"><i class='bx {step["icon"]}'></i><div class="step-number">{idx+1}</div></div>
                <div class="step-content"><h3 class="step-title">{step["title"]}</h3><div class="step-details">{step["content"]}</div></div>
            </div>"""

        search_process_javascript = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const steps = document.querySelectorAll('.process-step');
            let currentStep = 0;
            function showNextStep() {
                if (currentStep < steps.length) {
                    steps[currentStep].classList.add('active');
                    currentStep++;
                    setTimeout(showNextStep, 1500); 
                }
            }
            setTimeout(showNextStep, 500); 
        });
        </script>"""
        return f"""
        <div class="card search-process-card">
            <h2 class="section-title"><i class='bx bx-bot'></i>AI 搜索过程</h2>
            <div class="search-process">{search_process_html}</div>
            {search_process_javascript}
        </div>"""

