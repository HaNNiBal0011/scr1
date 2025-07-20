#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Universal Product Scraper - Расширенная версия с детальным извлечением данных
Доработанная версия с расширенным набором извлекаемых данных товаров
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import csv
import time
import random
import subprocess
import sys
import os
from typing import List, Dict, Optional, Union
import logging
from urllib.parse import urljoin, urlparse
import webbrowser
import re

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Настройка темы customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class EnhancedUniversalScraper:
    """Расширенный универсальный скрапер с детальным извлечением данных товаров."""
    
    def __init__(self):
        self.session = None
        self.current_id = 1
        
        # Расширенный список User agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        
        # Конфигурации сайтов с селекторами на основе реального HTML
        self.site_configs = {
            'rozetka': {
                'base_url': 'https://rozetka.com.ua',
                'search_url': 'https://rozetka.com.ua/ua/search/?text={}',
                'alt_search_urls': [
                    'https://rozetka.com.ua/search/?text={}',
                    'https://rozetka.com.ua/ua/catalog/search/?query={}'
                ],
                'direct_url': 'https://rozetka.com.ua/ua/p{}/',
                'selectors': {
                    'product_cards': [
                        'li.catalog-grid__cell',
                        'rz-catalog-tile',
                        'app-goods-tile-default',
                        'div.goods-tile',
                        'div[data-goods-id]',
                        'li[class*="catalog-grid__cell"]',
                        'div[class*="goods-tile"]'
                    ],
                    'title': [
                        'span.goods-tile__title',
                        'a.goods-tile__heading span.goods-tile__title',
                        '.goods-tile__title',
                        'rz-indexed-link span.goods-tile__title',
                        '.goods-tile__heading',
                        'a[class*="goods-tile__heading"]'
                    ],
                    'price_regular': [
                        '.goods-tile__price--old',
                        '.price--gray',
                        'div.goods-tile__price--old.price--gray'
                    ],
                    'price_discount': [
                        'span.goods-tile__price-value',
                        '.goods-tile__price-value',
                        'div.goods-tile__price span.goods-tile__price-value',
                        '.goods-tile__price .goods-tile__price-value'
                    ],
                    'discount_percent': [
                        '.goods-tile__label.promo-label',
                        'span.goods-tile__label.promo-label'
                    ],
                    'article': [
                        '.g-id',
                        'div.g-id',
                        '[data-goods-id]'
                    ],
                    'availability': [
                        '.goods-tile__availability',
                        '.goods-tile__availability--available',
                        '.goods-tile__availability--unavailable'
                    ],
                    'image': [
                        'div.goods-tile__picture img',
                        '.goods-tile__picture img',
                        'rz-button-product-page img'
                    ],
                    'link': [
                        'a[href*="/p"]',
                        'rz-indexed-link a[href*="/p"]',
                        '.product-link[href*="/p"]',
                        'a.goods-tile__heading[href*="/p"]'
                    ]
                },
                'detail_selectors': {
                    'characteristics': [
                        '.product-about__brief',
                        '.characteristics-table',
                        '.product-specs'
                    ],
                    'brand': [
                        '.product-brand',
                        '[data-brand]',
                        '.brand-name'
                    ]
                }
            },
            'allo': {
                'base_url': 'https://allo.ua',
                'search_url': 'https://allo.ua/ua/catalogsearch/result/?q={}',
                'alt_search_urls': [
                    'https://allo.ua/catalogsearch/result/?q={}',
                    'https://allo.ua/ua/search/?q={}',
                    'https://allo.ua/search/?query={}'
                ],
                'direct_url': 'https://allo.ua/ua/p{}/',
                'selectors': {
                    'product_cards': [
                        'div.product-card',
                        '.product-card'
                    ],
                    'title': [
                        'a.product-card__title',
                        '.product-card__title'
                    ],
                    'price_regular': [
                        'div.v-pb__old span.sum',
                        '.v-pb__old .sum'
                    ],
                    'price_discount': [
                        'div.v-pb__cur span.sum',
                        'div.v-pb__cur.discount span.sum',
                        '.v-pb__cur .sum'
                    ],
                    'article': [
                        '.product-sku__value',
                        'span.product-sku__value'
                    ],
                    'availability': [
                        '.product-card__availability',
                        '.availability'
                    ],
                    'characteristics': [
                        '.product-card__detail',
                        'div.product-card__detail dl'
                    ],
                    'image': [
                        'div.product-card__pictures img',
                        '.product-card__img img',
                        '.image-carousel img',
                        'picture img'
                    ],
                    'link': [
                        'a.product-card__title[href]',
                        '.product-card__title[href]'
                    ]
                }
            },
            'epicentr': {
                'base_url': 'https://epicentrk.ua',
                'search_url': 'https://epicentrk.ua/ua/search/?q={}',
                'alt_search_urls': [
                    'https://epicentrk.ua/search/?q={}',
                    'https://epicentrk.ua/ua/catalog/search/?query={}'
                ],
                'direct_url': 'https://epicentrk.ua/ua/shop/p{}/',
                'selectors': {
                    'product_cards': [
                        '.card-product',
                        'div[class*="product-card"]',
                        'div[class*="catalog-item"]'
                    ],
                    'title': [
                        '.card-product__title a',
                        '.product-card__title a'
                    ],
                    'price_regular': [
                        '.card-product__price-old',
                        '.price-old'
                    ],
                    'price_discount': [
                        '.card-product__price-current',
                        '.price-current'
                    ],
                    'image': [
                        '.card-product__image img',
                        '.product-card__image img'
                    ],
                    'link': [
                        '.card-product__title a',
                        'a[href*="/shop/"]'
                    ]
                }
            },
            'comfy': {
                'base_url': 'https://comfy.ua',
                'search_url': 'https://comfy.ua/ua/search/?q={}',
                'alt_search_urls': [
                    'https://comfy.ua/search/?q={}',
                    'https://comfy.ua/ua/catalog/search/?query={}'
                ],
                'direct_url': 'https://comfy.ua/ua/{}/',
                'selectors': {
                    'product_cards': [
                        '.prdl-item',
                        'div[class*="prdl-item"]'
                    ],
                    'title': [
                        '.prdl-item__name',
                        'a.prdl-item__name'
                    ],
                    'price_discount': [
                        '.prdl-item__price-current',
                        '.prdl-item__price .prdl-item__price-current'
                    ],
                    'article': [
                        '.prdl-item__code',
                        'a.prdl-item__code'
                    ],
                    'image': [
                        '.nci-sl__slide img',
                        '.prdl-item__media img'
                    ],
                    'link': [
                        'a.prdl-item__name[href]',
                        '.prdl-item__name[href]'
                    ]
                }
            }
        }
        
    def get_random_headers(self) -> Dict[str, str]:
        """Генерация улучшенных заголовков для запросов."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    def init_cloudscraper(self):
        """Инициализация cloudscraper с улучшенными настройками."""
        try:
            import cloudscraper
            self.session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                },
                delay=10,
                debug=False
            )
            logger.info("✓ Cloudscraper инициализирован успешно")
            return True
        except ImportError:
            logger.error("✗ Cloudscraper недоступен")
            return False
    
    def search_by_code(self, product_code: str, sites: List[str] = None) -> List[Dict]:
        """Поиск товара по коду на выбранных сайтах."""
        if sites is None:
            sites = ['rozetka']
        
        all_results = []
        
        for site in sites:
            try:
                logger.info(f"🔍 Поиск на сайте {site.upper()}")
                site_results = self.search_on_site(product_code, site)
                for result in site_results:
                    result['source_site'] = site
                    result['search_code'] = product_code
                all_results.extend(site_results)
                
                # Задержка между сайтами
                if len(sites) > 1:
                    delay = random.uniform(2, 4)
                    logger.debug(f"Задержка между сайтами: {delay:.2f}c")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"❌ Ошибка поиска на {site}: {e}")
                continue
        
        return all_results
    
    def search_on_site(self, product_code: str, site: str) -> List[Dict]:
        """Улучшенный поиск на конкретном сайте с множественными попытками."""
        if site not in self.site_configs:
            logger.error(f"❌ Неизвестный сайт: {site}")
            return []
        
        config = self.site_configs[site]
        
        # Создаем новую сессию для каждого поиска
        if not self.init_cloudscraper():
            logger.error(f"❌ Не удалось инициализировать сессию для {site}")
            return []
        
        # Попытка прямого доступа (более быстрая)
        logger.info(f"🎯 Попытка прямого доступа к товару на {site}")
        direct_result = self.try_direct_access(product_code, site, config)
        if direct_result:
            logger.info(f"✅ Товар найден через прямой доступ на {site}")
            return direct_result
        
        # Поиск через основную страницу поиска
        logger.info(f"🔍 Поиск через страницу поиска на {site}")
        search_result = self.try_search_page(product_code, site, config)
        if search_result:
            logger.info(f"✅ Товары найдены через основной поиск на {site}: {len(search_result)} шт.")
            return search_result
        
        # Попытка альтернативных URL поиска
        if 'alt_search_urls' in config:
            logger.info(f"🔄 Пробуем альтернативные URL поиска для {site}")
            alt_result = self.try_alternative_search_urls(product_code, site, config)
            if alt_result:
                logger.info(f"✅ Товары найдены через альтернативный поиск на {site}: {len(alt_result)} шт.")
                return alt_result
        
        logger.warning(f"⚠️ Товар с кодом {product_code} не найден на {site}")
        return []
    
    def try_direct_access(self, product_code: str, site: str, config: Dict) -> List[Dict]:
        """Улучшенная попытка прямого доступа к товару."""
        try:
            # Различные варианты URL для каждого сайта
            url_variants = []
            
            if site == 'rozetka':
                url_variants = [
                    f"https://rozetka.com.ua/ua/p{product_code}/",
                    f"https://rozetka.com.ua/p{product_code}/",
                    f"https://rozetka.com.ua/ua/product/{product_code}/",
                    f"https://rozetka.com.ua/goods/{product_code}/"
                ]
            elif site == 'epicentr':
                url_variants = [
                    f"https://epicentrk.ua/ua/shop/p{product_code}/",
                    f"https://epicentrk.ua/shop/p{product_code}/",
                    f"https://epicentrk.ua/ua/product/{product_code}/"
                ]
            elif site == 'comfy':
                url_variants = [
                    f"https://comfy.ua/ua/product/{product_code}/",
                    f"https://comfy.ua/product/{product_code}/",
                    f"https://comfy.ua/ua/p{product_code}/"
                ]
            elif site == 'allo':
                url_variants = [
                    f"https://allo.ua/ua/p{product_code}/",
                    f"https://allo.ua/p{product_code}/",
                    f"https://allo.ua/ua/product/{product_code}/"
                ]
            
            for direct_url in url_variants:
                try:
                    logger.debug(f"🔗 Проверяем URL: {direct_url}")
                    
                    headers = self.get_random_headers()
                    response = self.session.get(direct_url, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'lxml')
                        
                        # Проверяем, что это действительно страница товара
                        if self.is_product_page(soup, site):
                            logger.info(f"✅ Найдена страница товара: {direct_url}")
                            product_data = self.extract_single_product(soup, direct_url, site, config)
                            if product_data:
                                product_data['id'] = self.current_id
                                self.current_id += 1
                                return [product_data]
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"❌ Ошибка с URL {direct_url}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Ошибка прямого доступа на {site}: {e}")
            return []
    
    def try_search_page(self, product_code: str, site: str, config: Dict) -> List[Dict]:
        """Улучшенный поиск через страницу поиска сайта."""
        try:
            search_url = config['search_url'].format(product_code)
            logger.info(f"🔍 Поиск по URL: {search_url}")
            
            # Добавляем случайную задержку
            delay = random.uniform(1, 3)
            logger.debug(f"⏰ Задержка перед запросом: {delay:.2f}с")
            time.sleep(delay)
            
            # Специальные заголовки для каждого сайта
            headers = self.get_random_headers()
            self.add_site_specific_headers(headers, site)
            
            response = self.session.get(search_url, headers=headers, timeout=30)
            logger.info(f"📊 Статус ответа для {site}: {response.status_code}")
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Сохраняем HTML для отладки
                debug_file = f'debug_{site}_{product_code}_search.html'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.debug(f"💾 HTML сохранен в {debug_file}")
                
                # Проверяем, загружен ли контент
                if self.is_content_loaded(soup, site):
                    logger.info(f"✅ Контент загружен для {site}")
                    return self.parse_search_results(soup, search_url, site, config, product_code)
                else:
                    logger.warning(f"⚠️ Контент не загружен для {site}, попробуем дополнительные методы")
                    return self.try_ajax_search(product_code, site, config, soup)
                
            elif response.status_code == 403:
                logger.warning(f"🚫 Доступ запрещен для {site} (403)")
                return []
            elif response.status_code == 429:
                logger.warning(f"⏰ Слишком много запросов для {site} (429)")
                time.sleep(random.uniform(5, 10))
                return []
            else:
                logger.error(f"❌ Статус {response.status_code} для {search_url}")
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска на {site}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []
    
    def try_alternative_search_urls(self, product_code: str, site: str, config: Dict) -> List[Dict]:
        """Попытка поиска через альтернативные URL."""
        try:
            alt_urls = config.get('alt_search_urls', [])
            
            for i, url_template in enumerate(alt_urls):
                try:
                    search_url = url_template.format(product_code)
                    logger.info(f"🔍 Альтернативный URL {i+1}: {search_url}")
                    
                    delay = random.uniform(2, 4)
                    time.sleep(delay)
                    
                    headers = self.get_random_headers()
                    self.add_site_specific_headers(headers, site)
                    
                    response = self.session.get(search_url, headers=headers, timeout=30)
                    logger.info(f"📊 Альтернативный статус для {site}: {response.status_code}")
                    
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'lxml')
                        
                        if self.is_content_loaded(soup, site):
                            logger.info(f"✅ Альтернативный контент загружен для {site}")
                            results = self.parse_search_results(soup, search_url, site, config, product_code)
                            if results:
                                return results
                        else:
                            ajax_results = self.try_ajax_search(product_code, site, config, soup)
                            if ajax_results:
                                return ajax_results
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка альтернативного URL {i+1} для {site}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Ошибка альтернативного поиска на {site}: {e}")
            return []
    
    def is_content_loaded(self, soup, site: str) -> bool:
        """Проверяет, загружен ли контент на странице."""
        try:
            content_indicators = {
                'rozetka': [
                    'rz-catalog-tile',
                    'goods-tile',
                    '.catalog-grid__cell',
                    '[data-goods-id]'
                ],
                'comfy': [
                    '.prdl-item',
                    '.product-card',
                    '[data-product-id]'
                ],
                'epicentr': [
                    '.card-product',
                    '.catalog-item',
                    '[data-product-id]'
                ],
                'allo': [
                    '.product-card',
                    '.catalog-item',
                    '[data-product-id]'
                ]
            }
            
            indicators = content_indicators.get(site, [])
            for indicator in indicators:
                if soup.select(indicator):
                    return True
            
            # Дополнительная проверка - ищем любые цены
            price_texts = soup.find_all(text=re.compile(r'\d+\s*₴|\d+\s*грн', re.IGNORECASE))
            if len(price_texts) >= 3:
                return True
            
            # Проверяем наличие ссылок на товары
            product_links = soup.find_all('a', href=re.compile(r'/p\d+|/product|/shop'))
            if len(product_links) >= 5:
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"❌ Ошибка проверки загрузки контента: {e}")
            return False
    
    def try_ajax_search(self, product_code: str, site: str, config: Dict, soup) -> List[Dict]:
        """Дополнительные методы поиска для AJAX-сайтов."""
        try:
            logger.info(f"🔄 Применяем AJAX-методы для {site}")
            return self.advanced_universal_search(soup, site, config, product_code)
            
        except Exception as e:
            logger.error(f"❌ Ошибка AJAX поиска: {e}")
            return []
    
    def advanced_universal_search(self, soup, site: str, config: Dict, product_code: str) -> List[Dict]:
        """Расширенный универсальный поиск для сложных случаев."""
        try:
            logger.info(f"🔍 Расширенный универсальный поиск для {site}")
            
            products = []
            
            # Метод 1: Поиск по data-атрибутам
            data_elements = soup.find_all(attrs={'data-product-id': True})
            data_elements += soup.find_all(attrs={'data-goods-id': True})
            data_elements += soup.find_all(attrs={'data-item-id': True})
            
            if data_elements:
                logger.info(f"📦 Найдено {len(data_elements)} элементов с data-атрибутами")
                for elem in data_elements[:5]:
                    product_data = self.extract_from_data_element(elem, site, config)
                    if product_data:
                        products.append(product_data)
            
            # Метод 2: Поиск по паттернам URL и текста
            if not products:
                pattern_products = self.search_by_patterns(soup, site, product_code)
                products.extend(pattern_products)
            
            # Метод 3: Последняя попытка - поиск любых товароподобных элементов
            if not products:
                fallback_products = self.fallback_product_search(soup, site)
                products.extend(fallback_products[:3])
            
            logger.info(f"🎯 Расширенный поиск нашел {len(products)} товаров")
            return products
            
        except Exception as e:
            logger.error(f"❌ Ошибка расширенного поиска: {e}")
            return []
    
    def parse_search_results(self, soup, base_url: str, site: str, config: Dict, product_code: str) -> List[Dict]:
        """Улучшенный парсинг результатов поиска."""
        products = []
        
        try:
            logger.info(f"🔍 Начинаем парсинг результатов для {site}")
            
            # Ищем карточки товаров с улучшенной логикой
            product_cards = self.find_product_cards(soup, site, config)
            
            if not product_cards:
                logger.warning(f"⚠️ Товарные карточки не найдены на {site}")
                return []
            
            logger.info(f"📦 Найдено {len(product_cards)} потенциальных карточек на {site}")
            
            # Извлекаем данные товаров
            extracted_count = 0
            for i, card in enumerate(product_cards[:10]):
                try:
                    logger.debug(f"📝 Обрабатываем карточку {i+1}/{min(len(product_cards), 10)}")
                    
                    product_data = self.extract_enhanced_product_data(card, base_url, site, config)
                    if product_data and self.is_relevant_product(product_data, product_code):
                        product_data['id'] = self.current_id
                        products.append(product_data)
                        self.current_id += 1
                        extracted_count += 1
                        
                        title_preview = product_data['title'][:50] if product_data['title'] else 'Без названия'
                        logger.info(f"✅ Товар {extracted_count}: {title_preview}...")
                    else:
                        logger.debug(f"❌ Карточка {i+1} не прошла проверку")
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка обработки карточки {i+1}: {e}")
                    continue
            
            logger.info(f"📊 Итого извлечено товаров с {site}: {len(products)}")
            return products
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга результатов на {site}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []
    
    def extract_enhanced_product_data(self, card, base_url: str, site: str, config: Dict) -> Optional[Dict]:
        """РАСШИРЕННОЕ извлечение всех требуемых данных товара."""
        try:
            # Расширенная структура данных товара согласно требованиям
            product_data = {
                # Основные данные
                'article': None,           # Артикул ЭП
                'title': None,            # Наименование с сайта
                'price_regular': None,    # Цена неакционная
                'price_discount': None,   # Цена акционная
                'discount_percent': None, # % скидки
                
                # Характеристики товара
                'material': None,         # Материал товара
                'brand': None,           # Бренд
                'collection': None,      # Коллекция
                'color': None,           # Цвет
                'image_url': None,       # Фото
                'availability': 'available', # Наличие
                'composition': None,     # Комплектация
                'type': None,           # Тип
                'packaging': None,      # Упаковка (есть коробка/или нет)
                'quantity': None,       # Количество предметов
                'size': None,           # Размер (объем, диаметр)
                
                # Служебные поля
                'product_url': None,    # Ссылка на товар
                'search_code': None,
                'source_site': site
            }
            
            logger.debug(f"🔍 Извлекаем РАСШИРЕННЫЕ данные для {site}")
            
            # 1. Извлечение артикула (код товара)
            product_data['article'] = self.extract_article_enhanced(card, site, config)
            logger.debug(f"🔢 Артикул: {product_data['article']}")
            
            # 2. Извлечение названия
            product_data['title'] = self.extract_title_enhanced(card, config, site)
            logger.debug(f"📝 Название: {product_data['title']}")
            
            # 3. Извлечение цен (обычная и акционная)
            prices = self.extract_prices_enhanced(card, config, site)
            product_data.update(prices)
            logger.debug(f"💰 Цены: обычная={product_data['price_regular']}, акционная={product_data['price_discount']}")
            
            # 4. Расчет скидки
            product_data['discount_percent'] = self.calculate_discount_enhanced(
                product_data['price_regular'], 
                product_data['price_discount']
            )
            logger.debug(f"🎯 Скидка: {product_data['discount_percent']}%")
            
            # 5. Извлечение ссылки
            product_data['product_url'] = self.extract_link_enhanced(card, config, base_url, site)
            
            # 6. Извлечение изображения
            product_data['image_url'] = self.extract_image_enhanced(card, config, base_url, site)
            
            # 7. Извлечение характеристик из карточки
            characteristics = self.extract_characteristics_enhanced(card, site, config)
            product_data.update(characteristics)
            
            # 8. Проверка наличия
            product_data['availability'] = self.check_availability_enhanced(card, site, config)
            
            # 9. Если есть ссылка на товар, получаем дополнительные данные
            if product_data['product_url']:
                detailed_data = self.fetch_detailed_product_info_enhanced(product_data['product_url'], site)
                if detailed_data:
                    # Обновляем данные более детальной информацией
                    for key, value in detailed_data.items():
                        if value and not product_data.get(key):
                            product_data[key] = value
            
            # Валидация - товар должен иметь хотя бы название или артикул
            if product_data['title'] or product_data['article']:
                logger.info(f"✅ РАСШИРЕННЫЙ товар извлечен: {product_data['title'][:50] if product_data['title'] else product_data['article']}")
                return product_data
            else:
                logger.warning(f"❌ Товар отклонен - нет названия и артикула")
                return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения расширенных данных товара: {e}")
            return None
    
    def extract_article_enhanced(self, card, site: str, config: Dict) -> Optional[str]:
        """Расширенное извлечение артикула товара."""
        # Ищем в data-атрибутах
        for attr in ['data-goods-id', 'data-product-id', 'data-item-id', 'data-sku']:
            value = card.get(attr)
            if value:
                logger.debug(f"🔢 Артикул найден в {attr}: {value}")
                return str(value)
        
        # Используем селекторы для конкретного сайта
        article_selectors = config['selectors'].get('article', [])
        for selector in article_selectors:
            elem = card.select_one(selector)
            if elem:
                article = elem.get_text(strip=True)
                # Извлекаем только цифры из артикула
                article_clean = re.sub(r'[^\d]', '', article)
                if article_clean and len(article_clean) >= 6:
                    logger.debug(f"🔢 Артикул найден селектором '{selector}': {article_clean}")
                    return article_clean
        
        # Ищем в URL товара
        links = card.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            # Различные паттерны для артикула в URL
            patterns = [
                r'/p(\d+)/',
                r'/(\d{8,})/',  # Артикулы обычно длинные
                r'product[/-](\d+)',
                r'id[=:](\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, href)
                if match:
                    article = match.group(1)
                    if len(article) >= 6:
                        logger.debug(f"🔢 Артикул найден в URL по паттерну '{pattern}': {article}")
                        return article
        
        return None
    
    def extract_prices_enhanced(self, card, config: Dict, site: str) -> Dict[str, Optional[str]]:
        """Расширенное извлечение обычной и акционной цены."""
        prices = {
            'price_regular': None,
            'price_discount': None
        }
        
        # Извлекаем обычную цену
        regular_selectors = config['selectors'].get('price_regular', [])
        for selector in regular_selectors:
            elem = card.select_one(selector)
            if elem:
                price = self.parse_price_enhanced(elem.get_text(strip=True))
                if price:
                    prices['price_regular'] = price
                    logger.debug(f"💰 Обычная цена найдена: {price}")
                    break
        
        # Извлекаем акционную цену
        discount_selectors = config['selectors'].get('price_discount', [])
        for selector in discount_selectors:
            elem = card.select_one(selector)
            if elem:
                price = self.parse_price_enhanced(elem.get_text(strip=True))
                if price:
                    prices['price_discount'] = price
                    logger.debug(f"💰 Акционная цена найдена: {price}")
                    break
        
        # Если не нашли акционную цену, пробуем общие селекторы цены
        if not prices['price_discount']:
            general_price_selectors = [
                '.price', '.sum', '[class*="price"]', 
                'span[class*="price"]', 'div[class*="price"]'
            ]
            
            for selector in general_price_selectors:
                elem = card.select_one(selector)
                if elem:
                    price = self.parse_price_enhanced(elem.get_text(strip=True))
                    if price:
                        if prices['price_regular']:
                            prices['price_discount'] = price
                        else:
                            prices['price_discount'] = price
                        logger.debug(f"💰 Цена найдена общим селектором: {price}")
                        break
        
        return prices
    
    def calculate_discount_enhanced(self, regular_price: str, discount_price: str) -> Optional[int]:
        """Расширенный расчет процента скидки."""
        if not regular_price or not discount_price:
            return None
        
        try:
            regular = int(regular_price)
            discount = int(discount_price)
            
            if regular > discount > 0:
                percent = round((regular - discount) / regular * 100)
                logger.debug(f"🎯 Рассчитана скидка: {percent}%")
                return percent
        except (ValueError, ZeroDivisionError):
            pass
        
        return None
    
    def extract_characteristics_enhanced(self, card, site: str, config: Dict) -> Dict[str, Optional[str]]:
        """Расширенное извлечение характеристик товара."""
        characteristics = {
            'material': None,
            'brand': None,
            'collection': None,
            'color': None,
            'composition': None,
            'type': None,
            'packaging': None,
            'quantity': None,
            'size': None
        }
        
        # Сначала ищем в специальных блоках характеристик
        char_selectors = config['selectors'].get('characteristics', [])
        for selector in char_selectors:
            chars_block = card.select_one(selector)
            if chars_block:
                char_text = chars_block.get_text().lower()
                parsed_chars = self.parse_characteristics_text_enhanced(char_text)
                characteristics.update(parsed_chars)
                logger.debug(f"📋 Найдены характеристики в блоке: {len([v for v in parsed_chars.values() if v])}")
                break
        
        # Если не нашли в специальном блоке, ищем в общем тексте карточки
        if not any(characteristics.values()):
            card_text = card.get_text().lower()
            parsed_chars = self.parse_characteristics_text_enhanced(card_text)
            characteristics.update(parsed_chars)
        
        # Дополнительно извлекаем из названия товара
        title = card.select_one(config['selectors']['title'][0])
        if title:
            title_text = title.get_text().lower()
            title_chars = self.parse_characteristics_text_enhanced(title_text)
            # Добавляем только недостающие характеристики
            for key, value in title_chars.items():
                if not characteristics.get(key):
                    characteristics[key] = value
        
        return characteristics
    
    def parse_characteristics_text_enhanced(self, text: str) -> Dict[str, Optional[str]]:
        """Расширенный парсинг характеристик из текста."""
        characteristics = {
            'material': None,
            'brand': None,
            'collection': None,
            'color': None,
            'composition': None,
            'type': None,
            'packaging': None,
            'quantity': None,
            'size': None
        }
        
        # Расширенные паттерны для поиска характеристик
        patterns = {
            'material': [
                r'матеріал[:\s]*([^\n,;\.]+)',
                r'материал[:\s]*([^\n,;\.]+)',
                r'(?:скло|пластик|метал|дерево|кераміка|силікон|нержавіюча сталь|алюміній|скляний|пластиковий)',
                r'з\s+([^\s,;]+(?:\s+[^\s,;]+)*)\s*(?:скла|пластику|металу|дерева|кераміки)'
            ],
            'brand': [
                r'бренд[:\s]*([^\n,;\.]+)',
                r'виробник[:\s]*([^\n,;\.]+)',
                r'торгова марка[:\s]*([^\n,;\.]+)',
                r'\b(xiaomi|samsung|apple|lg|philips|tefal|bosch|siemens|electrolux|a-plus|redmi|sony|panasonic)\b'
            ],
            'color': [
                r'колір[:\s]*([^\n,;\.]+)',
                r'цвет[:\s]*([^\n,;\.]+)',
                r'\b(чорний|білий|червоний|синій|зелений|жовтий|сірий|рожевий|фіолетовий|прозорий)\b',
                r'\b(black|white|red|blue|green|yellow|gray|grey|pink|purple|night|coral|cloud|transparent)\b'
            ],
            'type': [
                r'тип[:\s]*([^\n,;\.]+)',
                r'призначення[:\s]*([^\n,;\.]+)',
                r'категорія[:\s]*([^\n,;\.]+)',
                r'(навушники|наушники|форми для запікання|посуд|кільце|ring|headphones|earbuds)'
            ],
            'quantity': [
                r'(\d+)\s*(?:предметів|предметы|шт|штук|pieces|пр)',
                r'набір\s+(\d+)\s*предметів',
                r'комплект\s+(\d+)\s*штук',
                r'(\d+)\s*в\s*наборі'
            ],
            'size': [
                r'(\d+(?:[,\.]\d+)?)\s*(?:см|мм|л|мл|дм|м)',
                r'діаметр[:\s]*(\d+(?:[,\.]\d+)?)\s*(?:см|мм)',
                r'об\'єм[:\s]*(\d+(?:[,\.]\d+)?)\s*(?:л|мл)',
                r'розмір[:\s]*([^\n,;\.]+)',
                r'(\d+\.?\d*)\s*(?:inch|дюйм|"|\'\')'
            ],
            'packaging': [
                r'упаковка[:\s]*([^\n,;\.]+)',
                r'в\s+коробці',
                r'без\s+упаковки',
                r'картонна\s+коробка',
                r'подарункова\s+упаковка',
                r'з\s+кришкою'
            ],
            'composition': [
                r'комплектація[:\s]*([^\n,;\.]+)',
                r'комплектация[:\s]*([^\n,;\.]+)',
                r'в\s+комплекті[:\s]*([^\n,;\.]+)',
                r'включає[:\s]*([^\n,;\.]+)'
            ],
            'collection': [
                r'колекція[:\s]*([^\n,;\.]+)',
                r'коллекция[:\s]*([^\n,;\.]+)',
                r'серія[:\s]*([^\n,;\.]+)',
                r'серия[:\s]*([^\n,;\.]+)'
            ]
        }
        
        for char_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if match.groups():
                        value = match.group(1).strip()
                    else:
                        value = match.group(0).strip()
                    
                    if value and len(value) > 1:
                        characteristics[char_type] = value
                        logger.debug(f"📋 {char_type}: {value}")
                        break
        
        return characteristics
    
    def check_availability_enhanced(self, card, site: str, config: Dict) -> str:
        """Расширенная проверка наличия товара."""
        # Селекторы для проверки наличия
        availability_selectors = config['selectors'].get('availability', [])
        
        for selector in availability_selectors:
            elem = card.select_one(selector)
            if elem:
                availability_text = elem.get_text().lower()
                
                # Проверяем на наличие
                if any(word in availability_text for word in [
                    'є в наявності', 'в наличии', 'в наявності', 'available', 'in stock', 'доступно'
                ]):
                    return 'available'
                elif any(word in availability_text for word in [
                    'немає в наявності', 'нет в наличии', 'відсутній', 'out of stock', 'unavailable', 'закінчився'
                ]):
                    return 'out_of_stock'
        
        # Ищем в общем тексте карточки
        card_text = card.get_text().lower()
        if any(word in card_text for word in [
            'немає в наявності', 'нет в наличии', 'відсутній', 'out of stock', 'unavailable'
        ]):
            return 'out_of_stock'
        
        # Если не найдено явных индикаторов, считаем доступным
        return 'available'
    
    def fetch_detailed_product_info_enhanced(self, product_url: str, site: str) -> Optional[Dict]:
        """Получение расширенной детальной информации со страницы товара."""
        try:
            logger.debug(f"🔍 Получаем расширенную информацию с: {product_url}")
            
            headers = self.get_random_headers()
            response = self.session.get(product_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'lxml')
                
                return self.parse_product_page_enhanced(soup, site)
            else:
                logger.warning(f"⚠️ Не удалось загрузить страницу товара: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения расширенной информации: {e}")
        
        return None
    
    def parse_product_page_enhanced(self, soup, site: str) -> Dict:
        """Расширенный парсинг детальной информации со страницы товара."""
        detailed_info = {}
        
        try:
            # Селекторы для детальных характеристик на странице товара
            detail_selectors = {
                'rozetka': {
                    'characteristics': ['.characteristics-full', '.product-about', '.characteristics-table', '.specs-table'],
                    'description': ['.product-about__brief', '.product-description']
                },
                'allo': {
                    'characteristics': ['.product-characteristics', '.specifications', '.product-details', '.char-list'],
                    'description': ['.product-description', '.product-info']
                },
                'epicentr': {
                    'characteristics': ['.product-characteristics', '.specifications', '.char-table'],
                    'description': ['.product-description']
                },
                'comfy': {
                    'characteristics': ['.product-specifications', '.characteristics', '.specs-list'],
                    'description': ['.product-description']
                }
            }
            
            selectors = detail_selectors.get(site, {})
            
            # Ищем блок с характеристиками
            for selector in selectors.get('characteristics', []):
                chars_block = soup.select_one(selector)
                if chars_block:
                    # Парсим структурированные характеристики
                    structured_chars = self.parse_structured_characteristics_enhanced(chars_block)
                    detailed_info.update(structured_chars)
                    
                    # Парсим текстовые характеристики
                    char_text = chars_block.get_text().lower()
                    text_chars = self.parse_characteristics_text_enhanced(char_text)
                    
                    # Объединяем данные, приоритет у структурированных
                    for key, value in text_chars.items():
                        if not detailed_info.get(key):
                            detailed_info[key] = value
                    
                    break
            
            # Ищем в описании товара
            for selector in selectors.get('description', []):
                desc_block = soup.select_one(selector)
                if desc_block:
                    desc_text = desc_block.get_text().lower()
                    desc_chars = self.parse_characteristics_text_enhanced(desc_text)
                    
                    # Добавляем только недостающие характеристики
                    for key, value in desc_chars.items():
                        if not detailed_info.get(key):
                            detailed_info[key] = value
            
            logger.debug(f"📋 Извлечено характеристик со страницы: {len([v for v in detailed_info.values() if v])}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга страницы товара: {e}")
        
        return detailed_info
    
    def parse_structured_characteristics_enhanced(self, chars_block) -> Dict:
        """Расширенный парсинг структурированных характеристик."""
        characteristics = {}
        
        try:
            # Ищем пары ключ-значение в различных структурах
            
            # 1. Таблицы tr/td
            rows = chars_block.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    mapped_key = self.map_characteristic_key(key)
                    if mapped_key and value:
                        characteristics[mapped_key] = value
            
            # 2. Списки li
            items = chars_block.find_all('li')
            for item in items:
                text = item.get_text()
                if ':' in text:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().lower()
                        value = parts[1].strip()
                        mapped_key = self.map_characteristic_key(key)
                        if mapped_key and value:
                            characteristics[mapped_key] = value
            
            # 3. dl/dt/dd структуры
            dl_blocks = chars_block.find_all('dl')
            for dl in dl_blocks:
                dt_elements = dl.find_all('dt')
                dd_elements = dl.find_all('dd')
                
                for dt, dd in zip(dt_elements, dd_elements):
                    key = dt.get_text(strip=True).lower()
                    value = dd.get_text(strip=True)
                    mapped_key = self.map_characteristic_key(key)
                    if mapped_key and value:
                        characteristics[mapped_key] = value
            
            # 4. Поиск по паттернам в тексте
            text = chars_block.get_text()
            text_chars = self.parse_characteristics_text_enhanced(text.lower())
            for key, value in text_chars.items():
                if not characteristics.get(key):
                    characteristics[key] = value
            
        except Exception as e:
            logger.debug(f"❌ Ошибка парсинга структурированных характеристик: {e}")
        
        return characteristics
    
    def map_characteristic_key(self, key: str) -> Optional[str]:
        """Маппинг ключей характеристик на наши поля."""
        key_mapping = {
            # Материал
            'матеріал': 'material',
            'материал': 'material',
            'material': 'material',
            
            # Бренд
            'бренд': 'brand',
            'виробник': 'brand',
            'торгова марка': 'brand',
            'brand': 'brand',
            'manufacturer': 'brand',
            
            # Цвет
            'колір': 'color',
            'цвет': 'color',
            'color': 'color',
            'colour': 'color',
            
            # Коллекция
            'колекція': 'collection',
            'коллекция': 'collection',
            'серія': 'collection',
            'серия': 'collection',
            'collection': 'collection',
            'series': 'collection',
            
            # Тип
            'тип': 'type',
            'призначення': 'type',
            'категорія': 'type',
            'type': 'type',
            'category': 'type',
            
            # Комплектация
            'комплектація': 'composition',
            'комплектация': 'composition',
            'в комплекті': 'composition',
            'composition': 'composition',
            'set includes': 'composition',
            
            # Упаковка
            'упаковка': 'packaging',
            'packaging': 'packaging',
            'коробка': 'packaging',
            'box': 'packaging',
            
            # Количество
            'кількість': 'quantity',
            'количество': 'quantity',
            'quantity': 'quantity',
            'pieces': 'quantity',
            'count': 'quantity',
            
            # Размер
            'розмір': 'size',
            'размер': 'size',
            'діаметр': 'size',
            'диаметр': 'size',
            'об\'єм': 'size',
            'объем': 'size',
            'size': 'size',
            'diameter': 'size',
            'volume': 'size',
            'dimensions': 'size'
        }
        
        # Проверяем точные совпадения
        mapped = key_mapping.get(key.strip())
        if mapped:
            return mapped
        
        # Проверяем частичные совпадения
        for search_key, mapped_key in key_mapping.items():
            if search_key in key:
                return mapped_key
        
        return None
    
    # Остальные методы остаются без изменений (сохраняем принцип работы)
    def add_site_specific_headers(self, headers: Dict[str, str], site: str):
        """Добавляет специфичные для сайта заголовки."""
        site_headers = {
            'comfy': {
                'Referer': 'https://comfy.ua/',
                'Origin': 'https://comfy.ua'
            },
            'epicentr': {
                'Referer': 'https://epicentrk.ua/',
                'Origin': 'https://epicentrk.ua'
            },
            'allo': {
                'Referer': 'https://allo.ua/',
                'Origin': 'https://allo.ua'
            },
            'rozetka': {
                'Referer': 'https://rozetka.com.ua/',
                'Origin': 'https://rozetka.com.ua'
            }
        }
        
        if site in site_headers:
            headers.update(site_headers[site])
    
    def find_product_cards(self, soup, site: str, config: Dict) -> List:
        """Улучшенный поиск карточек товаров."""
        product_cards = []
        
        # Пробуем основные селекторы
        for selector in config['selectors']['product_cards']:
            try:
                cards = soup.select(selector)
                logger.debug(f"🔍 Селектор '{selector}': {len(cards)} элементов")
                
                if cards:
                    valid_cards = []
                    for card in cards:
                        if self.is_valid_product_card(card, site):
                            valid_cards.append(card)
                    
                    if valid_cards:
                        logger.info(f"✅ Найдено {len(valid_cards)} валидных карточек с селектором: {selector}")
                        return valid_cards[:10]
                        
            except Exception as e:
                logger.debug(f"❌ Ошибка с селектором '{selector}': {e}")
                continue
        
        # Если основные селекторы не сработали, применяем универсальные методы
        logger.warning(f"⚠️ Основные селекторы не сработали на {site}")
        return self.find_cards_universal_method(soup, site)
    
    def is_valid_product_card(self, card, site: str) -> bool:
        """Проверка валидности карточки товара."""
        try:
            card_text = card.get_text().lower()
            card_html = str(card).lower()
            
            # Базовые проверки
            if len(card_text.strip()) < 15:
                return False
            
            # Исключаем системные сообщения
            exclusions = [
                'pardon our interruption', 'access denied', 'checking your browser',
                'cloudflare', 'помилка', 'ошибка'
            ]
            
            for exclusion in exclusions:
                if exclusion in card_text:
                    return False
            
            # Позитивные индикаторы
            indicators = []
            
            # Наличие цены
            has_price = bool(re.search(r'\d+\s*[₴грнuah]', card_text))
            indicators.append(has_price)
            
            # Наличие ссылок на товары
            has_product_links = bool(re.search(r'href="[^"]*(/p|/product|/shop|/goods)', card_html))
            indicators.append(has_product_links)
            
            # Наличие изображений
            has_images = 'img' in card_html
            indicators.append(has_images)
            
            # Достаточный объем текста
            has_sufficient_text = len(card_text.strip()) > 30
            indicators.append(has_sufficient_text)
            
            # Товар валиден если набрал хотя бы 2 балла из 4
            score = sum(indicators)
            return score >= 2
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки валидности карточки: {e}")
            return False
    
    def extract_title_enhanced(self, card, config: Dict, site: str) -> Optional[str]:
        """Расширенное извлечение названия товара."""
        # Пробуем основные селекторы
        for selector in config['selectors']['title']:
            try:
                elem = card.select_one(selector)
                if elem:
                    title = elem.get_text(strip=True)
                    if title and 5 < len(title) < 300:
                        if not self.is_service_title(title):
                            return title
            except Exception as e:
                logger.debug(f"❌ Ошибка с селектором названия '{selector}': {e}")
                continue
        
        # Универсальные методы
        return self.extract_title_universal(card)
    
    def extract_title_universal(self, card) -> Optional[str]:
        """Универсальное извлечение названия."""
        # Ищем в ссылках на товары
        links = card.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if any(pattern in href.lower() for pattern in ['/p', '/product', '/shop', '/goods']):
                if text and 10 < len(text) < 300:
                    if not self.is_service_title(text):
                        return text
        
        # Ищем в заголовках
        for tag in ['h1', 'h2', 'h3', 'h4']:
            headers = card.find_all(tag)
            for elem in headers:
                title = elem.get_text(strip=True)
                if title and 10 < len(title) < 300:
                    if not self.is_service_title(title):
                        return title
        
        return None
    
    def parse_price_enhanced(self, price_text: str) -> Optional[str]:
        """Расширенный парсинг цены."""
        if not price_text:
            return None
        
        # Удаляем валютные символы и лишние символы
        cleaned = re.sub(r'[₴грнuahUAH]', '', price_text, flags=re.IGNORECASE)
        cleaned = re.sub(r'[^\d\s,.]', '', cleaned)
        
        # Обрабатываем разделители
        cleaned = cleaned.replace(' ', '').replace('\u00a0', '').replace(',', '')
        
        if '.' in cleaned:
            parts = cleaned.split('.')
            if len(parts) == 2 and len(parts[1]) <= 2:
                cleaned = parts[0]
            else:
                cleaned = cleaned.replace('.', '')
        
        # Извлекаем только цифры
        numbers = re.findall(r'\d+', cleaned)
        if numbers:
            price = ''.join(numbers)
            try:
                price_int = int(price)
                if 10 <= price_int <= 10000000:
                    return price
            except ValueError:
                pass
        
        return None
    
    def extract_link_enhanced(self, card, config: Dict, base_url: str, site: str) -> Optional[str]:
        """Расширенное извлечение ссылки."""
        # Пробуем основные селекторы
        for selector in config['selectors'].get('link', []):
            try:
                elem = card.select_one(selector)
                if elem:
                    product_url = elem.get('href')
                    if product_url:
                        if not product_url.startswith('http'):
                            product_url = urljoin(base_url, product_url)
                        return product_url
            except Exception:
                continue
        
        return None
    
    def extract_image_enhanced(self, card, config: Dict, base_url: str, site: str) -> Optional[str]:
        """Расширенное извлечение изображения."""
        # Пробуем основные селекторы
        for selector in config['selectors'].get('image', []):
            try:
                elem = card.select_one(selector)
                if elem:
                    for attr in ['src', 'data-src', 'data-lazy-src', 'data-original']:
                        image_url = elem.get(attr)
                        if image_url and self.is_valid_image_url(image_url):
                            if not image_url.startswith('http'):
                                image_url = urljoin(base_url, image_url)
                            return image_url
            except Exception:
                continue
        
        return None
    
    def is_valid_image_url(self, url: str) -> bool:
        """Проверка валидности URL изображения."""
        if not url:
            return False
        
        invalid_patterns = ['placeholder', 'data:image', 'blank.gif', 'empty.png', 'loading.gif']
        url_lower = url.lower()
        
        if any(pattern in url_lower for pattern in invalid_patterns):
            return False
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg']
        return any(ext in url_lower for ext in valid_extensions) or '/images/' in url_lower
    
    def is_service_title(self, title: str) -> bool:
        """Проверка на служебные названия."""
        if not title:
            return True
        
        title_lower = title.lower().strip()
        
        service_patterns = [
            r'^всі\s+результати\s*$',
            r'^все\s+результаты\s*$',
            r'^показать\s+все\s*$',
            r'^показати\s+всі\s*$'
        ]
        
        for pattern in service_patterns:
            if re.match(pattern, title_lower):
                return True
        
        return len(title.strip()) < 5
    
    def is_relevant_product(self, product: Dict, product_code: str) -> bool:
        """Проверка релевантности товара."""
        try:
            # Проверка по URL
            if product.get('product_url'):
                url = product['product_url']
                if (f'/p{product_code}/' in url or 
                    f'/{product_code}/' in url or 
                    f'={product_code}' in url):
                    return True
            
            # Проверка по названию
            title = product.get('title', '').lower()
            if product_code.lower() in title:
                return True
            
            # Проверка по артикулу
            article = product.get('article', '')
            if article and product_code in article:
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки релевантности: {e}")
            return False
    
    def is_product_page(self, soup, site: str) -> bool:
        """Проверяет, является ли страница страницей товара."""
        product_indicators = [
            'h1', '[class*="price"]', '[class*="product"]', 
            'button[class*="buy"]', 'button[class*="cart"]'
        ]
        
        found_indicators = 0
        for indicator in product_indicators:
            if soup.select(indicator):
                found_indicators += 1
        
        return found_indicators >= 3
    
    def extract_single_product(self, soup, url: str, site: str, config: Dict) -> Optional[Dict]:
        """Извлечение данных с отдельной страницы товара."""
        try:
            product_data = self.create_empty_product_data()
            product_data['product_url'] = url
            product_data['source_site'] = site
            
            # Селекторы для страницы товара
            title_selectors = [
                'h1.product__title', 'h1[class*="title"]', 
                '.product-title h1', 'h1', '.product-name h1'
            ]
            
            price_selectors = [
                '.product-prices__big .product-price__big', '.price--red',
                '.product-price__big', '[class*="price"]:not([class*="old"])',
                '.current-price', '.price-current'
            ]
            
            # Извлечение данных
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text(strip=True)
                    if title and len(title) > 5:
                        product_data['title'] = title
                        break
            
            for selector in price_selectors:
                elem = soup.select_one(selector)
                if elem:
                    price = self.parse_price_enhanced(elem.get_text(strip=True))
                    if price:
                        product_data['price_discount'] = price
                        break
            
            return product_data if product_data['title'] else None
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения данных с отдельной страницы: {e}")
            return None
    
    def create_empty_product_data(self) -> Dict:
        """Создает пустую структуру данных товара."""
        return {
            'article': None,
            'title': None,
            'price_regular': None,
            'price_discount': None,
            'discount_percent': None,
            'material': None,
            'brand': None,
            'collection': None,
            'color': None,
            'image_url': None,
            'availability': 'available',
            'composition': None,
            'type': None,
            'packaging': None,
            'quantity': None,
            'size': None,
            'product_url': None,
            'search_code': None,
            'source_site': None
        }
    
    # Методы для совместимости и универсального поиска (остаются без изменений)
    def extract_from_data_element(self, elem, site: str, config: Dict) -> Optional[Dict]:
        """Извлекает данные товара из элемента с data-атрибутами."""
        try:
            product_data = self.create_empty_product_data()
            
            title_link = elem.find('a', href=True)
            if title_link:
                title = title_link.get_text(strip=True)
                product_url = title_link.get('href')
                
                if any(pattern in product_url for pattern in ['/p', '/product', '/shop', '/goods']):
                    product_data['title'] = title
                    product_data['product_url'] = product_url
            
            # Ищем цену
            price_elem = elem.find(text=re.compile(r'\d+\s*₴|\d+\s*грн', re.IGNORECASE))
            if price_elem:
                price = self.parse_price_enhanced(price_elem)
                if price:
                    product_data['price_discount'] = price
            
            # Ищем изображение
            img_elem = elem.find('img')
            if img_elem:
                for attr in ['src', 'data-src', 'data-lazy-src']:
                    image_url = img_elem.get(attr)
                    if image_url and self.is_valid_image_url(image_url):
                        product_data['image_url'] = image_url
                        break
            
            if product_data['title'] and len(product_data['title']) > 10:
                return product_data
            
            return None
            
        except Exception as e:
            logger.debug(f"❌ Ошибка извлечения из data-элемента: {e}")
            return None
    
    def search_by_patterns(self, soup, site: str, product_code: str) -> List[Dict]:
        """Поиск товаров по паттернам URL и текста."""
        try:
            products = []
            
            code_links = soup.find_all('a', href=re.compile(f'{product_code}', re.IGNORECASE))
            
            for link in code_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if any(pattern in href for pattern in ['/p', '/product', '/shop', '/goods']):
                    if text and 10 < len(text) < 200:
                        product_data = self.create_empty_product_data()
                        product_data['title'] = text
                        product_data['product_url'] = href
                        
                        # Ищем цену рядом
                        parent = link.parent
                        for _ in range(3):
                            if parent:
                                price_text = parent.find(text=re.compile(r'\d+\s*₴|\d+\s*грн', re.IGNORECASE))
                                if price_text:
                                    price = self.parse_price_enhanced(price_text)
                                    if price:
                                        product_data['price_discount'] = price
                                        break
                                parent = parent.parent
                        
                        products.append(product_data)
            
            return products
            
        except Exception as e:
            logger.debug(f"❌ Ошибка поиска по паттернам: {e}")
            return []
    
    def fallback_product_search(self, soup, site: str) -> List[Dict]:
        """Последняя попытка найти товары."""
        try:
            products = []
            
            all_links = soup.find_all('a', href=True)
            
            for link in all_links[:50]:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if any(pattern in href for pattern in ['/p', '/product', '/shop', '/goods']):
                    if text and 15 < len(text) < 150:
                        container = link.parent
                        has_price = False
                        
                        for _ in range(4):
                            if container:
                                price_pattern = re.search(r'\d+\s*₴|\d+\s*грн', container.get_text(), re.IGNORECASE)
                                if price_pattern:
                                    has_price = True
                                    break
                                container = container.parent
                        
                        if has_price:
                            product_data = self.create_empty_product_data()
                            product_data['title'] = text
                            product_data['product_url'] = href
                            products.append(product_data)
                            
                            if len(products) >= 3:
                                break
            
            return products
            
        except Exception as e:
            logger.debug(f"❌ Ошибка fallback поиска: {e}")
            return []
    
    def find_cards_universal_method(self, soup, site: str) -> List:
        """Универсальный метод поиска карточек товаров."""
        logger.info(f"🔍 Применяем универсальный метод поиска для {site}")
        
        price_patterns = [r'\d+\s*₴', r'\d+\s*грн', r'\d+\s*uah']
        potential_cards = set()
        
        for pattern in price_patterns:
            price_elements = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
            logger.debug(f"💰 Найдено {len(price_elements)} элементов с ценами")
            
            for price_elem in price_elements[:20]:
                current = price_elem.parent
                for level in range(5):
                    if current and current.name in ['div', 'article', 'li', 'section']:
                        links = current.find_all('a', href=True)
                        product_links = [link for link in links 
                                       if any(pattern in link.get('href', '') 
                                             for pattern in ['/p', '/product', '/shop', '/goods'])]
                        
                        if product_links and len(current.get_text(strip=True)) > 50:
                            potential_cards.add(current)
                            break
                    
                    current = current.parent if current else None
        
        cards_list = list(potential_cards)
        valid_cards = [card for card in cards_list if self.is_valid_product_card(card, site)]
        
        logger.info(f"🎯 Найдено {len(valid_cards)} карточек универсальным методом")
        return valid_cards[:10]


class EnhancedScraperUI:
    """Главный класс пользовательского интерфейса для расширенного скрапера."""
    
    def __init__(self):
        self.scraper = EnhancedUniversalScraper()
        self.scraped_data = []
        self.is_searching = False
        
        # Создание главного окна
        self.root = ctk.CTk()
        self.root.title("Enhanced Universal Product Scraper - Расширенная версия")
        self.root.geometry("1600x1000")
        self.root.resizable(True, True)
        
        # Настройка сетки
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        
        # Заголовок
        title_frame = ctk.CTkFrame(self.root)
        title_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🛒 Enhanced Universal Product Scraper - Расширенное извлечение данных", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Основной контент
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Панель поиска
        self.setup_search_panel(main_frame)
        
        # Панель результатов
        self.setup_results_panel(main_frame)
        
        # Панель кнопок
        self.setup_buttons_panel(main_frame)
        
    def setup_search_panel(self, parent):
        """Настройка панели поиска."""
        search_frame = ctk.CTkFrame(parent)
        search_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        # Поле для кода товара
        ctk.CTkLabel(search_frame, text="Код товара (можно несколько через пробел):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.product_code_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Введите код товара или несколько кодов через пробел (например: 497951464 1124218)",
            width=500,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.product_code_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Выбор магазинов
        stores_frame = ctk.CTkFrame(search_frame)
        stores_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(stores_frame, text="Выберите магазины для поиска:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        checkboxes_frame = ctk.CTkFrame(stores_frame)
        checkboxes_frame.pack(fill="x", padx=10, pady=5)
        
        # Чекбоксы магазинов
        self.store_checkboxes = {}
        
        stores = [
            ("rozetka", "🛒 Rozetka.com.ua", True),
            ("allo", "📱 Allo.ua", True),
            ("epicentr", "🏠 Epicentrk.ua", False),
            ("comfy", "💻 Comfy.ua", False)
        ]
        
        for i, (store_id, store_name, default_checked) in enumerate(stores):
            checkbox = ctk.CTkCheckBox(
                checkboxes_frame,
                text=store_name,
                font=ctk.CTkFont(size=12)
            )
            if default_checked:
                checkbox.select()
            checkbox.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="w")
            self.store_checkboxes[store_id] = checkbox
        
        # Настройки поиска
        settings_frame = ctk.CTkFrame(search_frame)
        settings_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        # Тип поиска
        ctk.CTkLabel(settings_frame, text="Тип поиска:", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        self.search_type = ctk.CTkComboBox(
            settings_frame,
            values=["Расширенное извлечение данных", "Точный поиск"],
            state="readonly",
            width=250
        )
        self.search_type.set("Расширенное извлечение данных")
        self.search_type.pack(side="left", padx=10)
        
        # Кнопки поиска
        buttons_frame = ctk.CTkFrame(search_frame)
        buttons_frame.grid(row=4, column=0, pady=20)
        
        self.search_button = ctk.CTkButton(
            buttons_frame,
            text="🔍 Начать расширенный поиск",
            command=self.start_search,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.search_button.pack(side="left", padx=10)
        
        self.clear_button = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Очистить",
            command=self.clear_results,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.clear_button.pack(side="left", padx=10)
        
        # Статус
        self.status_label = ctk.CTkLabel(search_frame, text="Готов к расширенному поиску", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=5, column=0, pady=10)
        
        # Прогресс бар
        self.progress_bar = ctk.CTkProgressBar(search_frame)
        self.progress_bar.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # Bind Enter key
        self.product_code_entry.bind('<Return>', lambda event: self.start_search())
        
    def setup_results_panel(self, parent):
        """Настройка панели результатов."""
        results_frame = ctk.CTkFrame(parent)
        results_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Таблица результатов с расширенными колонками
        self.setup_enhanced_treeview(results_frame)
        
    def setup_enhanced_treeview(self, parent):
        """Настройка расширенной таблицы результатов."""
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Стиль для Treeview
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       rowheight=30,
                       fieldbackground="#2b2b2b")
        style.map('Treeview', background=[('selected', '#22559b')])
        
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="white",
                       relief="flat")
        style.map("Treeview.Heading",
                 background=[('active', '#1f538d')])
        
        # Расширенные колонки согласно требованиям
        columns = (
            "Артикул", "Название", "Цена обычная", "Цена акционная", "Скидка %",
            "Материал", "Бренд", "Коллекция", "Цвет", "Наличие", 
            "Комплектация", "Тип", "Упаковка", "Количество", "Размер", "Источник"
        )
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        headers = {
            "Артикул": "Артикул ЭП",
            "Название": "Наименование с сайта",
            "Цена обычная": "Цена неакционная (₴)",
            "Цена акционная": "Цена акционная (₴)",
            "Скидка %": "% скидки",
            "Материал": "Материал товара",
            "Бренд": "Бренд",
            "Коллекция": "Коллекция",
            "Цвет": "Цвет",
            "Наличие": "Наличие",
            "Комплектация": "Комплектация",
            "Тип": "Тип",
            "Упаковка": "Упаковка",
            "Количество": "Кол-во предметов",
            "Размер": "Размер/Объем",
            "Источник": "Источник"
        }
        
        for col in columns:
            self.tree.heading(col, text=headers[col])
        
        # Настройка ширины колонок
        column_widths = {
            "Артикул": 100,
            "Название": 200,
            "Цена обычная": 100,
            "Цена акционная": 100,
            "Скидка %": 80,
            "Материал": 120,
            "Бренд": 100,
            "Коллекция": 120,
            "Цвет": 80,
            "Наличие": 100,
            "Комплектация": 150,
            "Тип": 100,
            "Упаковка": 100,
            "Количество": 80,
            "Размер": 120,
            "Источник": 100
        }
        
        for col in columns:
            width = column_widths.get(col, 100)
            self.tree.column(col, width=width, minwidth=80)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение элементов
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Обработчики событий
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)
        
    def setup_buttons_panel(self, parent):
        """Настройка панели кнопок."""
        buttons_frame = ctk.CTkFrame(parent)
        buttons_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Информация о результатах
        self.results_info_label = ctk.CTkLabel(buttons_frame, text="Найдено: 0 товаров", font=ctk.CTkFont(size=14, weight="bold"))
        self.results_info_label.pack(side="left", padx=20, pady=10)
        
        # Кнопки экспорта
        export_frame = ctk.CTkFrame(buttons_frame)
        export_frame.pack(side="right", padx=20, pady=10)
        
        self.export_csv_button = ctk.CTkButton(
            export_frame,
            text="📊 Экспорт расширенный CSV",
            command=self.export_enhanced_csv,
            width=180
        )
        self.export_csv_button.pack(side="left", padx=5)
        
        self.export_json_button = ctk.CTkButton(
            export_frame,
            text="📋 Экспорт JSON",
            command=self.export_enhanced_json,
            width=120
        )
        self.export_json_button.pack(side="left", padx=5)
        
        self.install_button = ctk.CTkButton(
            export_frame,
            text="⚙️ Установить пакеты",
            command=self.install_packages,
            width=140
        )
        self.install_button.pack(side="left", padx=5)
        
        self.test_button = ctk.CTkButton(
            export_frame,
            text="🧪 Тест расширенного поиска",
            command=self.test_enhanced_search,
            width=180
        )
        self.test_button.pack(side="left", padx=5)
        
    def start_search(self):
        """Запуск расширенного поиска в отдельном потоке."""
        if self.is_searching:
            return
            
        product_codes_input = self.product_code_entry.get().strip()
        
        if not product_codes_input:
            messagebox.showerror("Ошибка", "Пожалуйста, введите код товара")
            return
        
        # Проверяем выбранные магазины
        selected_stores = []
        for store_id, checkbox in self.store_checkboxes.items():
            if checkbox.get():
                selected_stores.append(store_id)
        
        if not selected_stores:
            messagebox.showerror("Ошибка", "Выберите хотя бы один магазин для поиска")
            return
        
        # Разделяем коды товаров по пробелам
        product_codes = [code.strip() for code in product_codes_input.split() if code.strip()]
        
        if not product_codes:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные коды товаров")
            return
        
        self.is_searching = True
        self.search_button.configure(state="disabled", text="Расширенный поиск...")
        self.progress_bar.set(0)
        
        # Очистка предыдущих результатов
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Запуск поиска в отдельном потоке
        search_thread = threading.Thread(target=self.perform_enhanced_search, args=(product_codes, selected_stores))
        search_thread.daemon = True
        search_thread.start()
        
    def perform_enhanced_search(self, product_codes, selected_stores):
        """Выполнение расширенного поиска по нескольким кодам товаров и магазинам."""
        try:
            self.update_status("🚀 Инициализация расширенного поиска с детальным извлечением данных...")
            self.progress_bar.set(0.1)
            
            logger.info(f"🎯 Тип поиска: Расширенное извлечение данных")
            logger.info(f"🏪 Выбранные магазины: {selected_stores}")
            logger.info(f"📦 Коды товаров: {product_codes}")
            
            # Инициализация расширенного скрапера
            if not self.scraper.init_cloudscraper():
                self.install_packages_silent()
                self.scraper.init_cloudscraper()
            
            all_results = []
            total_operations = len(product_codes) * len(selected_stores)
            current_operation = 0
            
            for product_code_index, product_code in enumerate(product_codes):
                try:
                    self.update_status(f"🔍 Расширенный поиск товара {product_code_index+1} из {len(product_codes)}: {product_code}")
                    
                    # Поиск на всех выбранных сайтах с расширенным извлечением
                    code_results = []
                    
                    for store_index, store in enumerate(selected_stores):
                        try:
                            logger.info(f"🏪 Расширенный поиск товара {product_code} в магазине {store.upper()}")
                            
                            # Добавляем задержку между магазинами
                            if store_index > 0:
                                delay = random.uniform(2, 5)
                                logger.debug(f"⏰ Задержка между магазинами: {delay:.2f}с")
                                time.sleep(delay)
                            
                            # Поиск в конкретном магазине с расширенным извлечением данных
                            store_results = self.scraper.search_on_site(product_code, store)
                            
                            # Добавляем информацию об источнике
                            for result in store_results:
                                result['source_site'] = store
                                result['search_code'] = product_code
                            
                            if store_results:
                                logger.info(f"✅ Найдено {len(store_results)} товаров с расширенными данными в {store.upper()}")
                                code_results.extend(store_results)
                                
                                # Логируем найденные характеристики
                                for result in store_results:
                                    char_count = len([v for v in [
                                        result.get('material'), result.get('brand'), result.get('color'),
                                        result.get('type'), result.get('quantity'), result.get('size')
                                    ] if v])
                                    logger.info(f"📋 Товар: {result.get('title', 'Без названия')[:30]}... - извлечено {char_count} характеристик")
                            else:
                                logger.warning(f"⚠️ Товары с кодом {product_code} не найдены в {store.upper()}")
                            
                            current_operation += 1
                            progress = 0.1 + (0.7 * current_operation / total_operations)
                            self.progress_bar.set(progress)
                            
                        except Exception as e:
                            logger.error(f"❌ Ошибка расширенного поиска в {store}: {e}")
                            current_operation += 1
                            continue
                    
                    if code_results:
                        logger.info(f"📦 Итого найдено {len(code_results)} товаров с расширенными данными для кода {product_code}")
                        all_results.extend(code_results)
                    else:
                        logger.warning(f"⚠️ Товары с кодом {product_code} не найдены ни в одном магазине")
                    
                    # Небольшая задержка между кодами товаров
                    if product_code_index < len(product_codes) - 1:
                        delay = random.uniform(3, 6)
                        logger.debug(f"⏰ Задержка между кодами товаров: {delay:.2f}с")
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка расширенного поиска товара {product_code}: {e}")
                    continue
            
            self.progress_bar.set(0.8)
            
            # Обновление интерфейса в главном потоке
            self.root.after(0, self.update_enhanced_results, all_results)
            
        except Exception as e:
            error_msg = f"Ошибка расширенного поиска: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.root.after(0, self.show_error, error_msg)
        finally:
            self.root.after(0, self.search_completed)
    
    def install_packages_silent(self):
        """Тихая установка пакетов."""
        required_packages = [
            'cloudscraper',
            'beautifulsoup4',
            'lxml',
            'requests'
        ]
        
        for package in required_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                pass
    
    def update_enhanced_results(self, results):
        """Обновление результатов в расширенной таблице."""
        logger.info(f"📊 Обновление UI с {len(results)} расширенными результатами")
        
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.scraped_data = results
        
        # Добавление новых результатов с расширенными данными
        for i, product in enumerate(results):
            try:
                # Подготовка данных для отображения
                values = [
                    product.get('article', 'Не указан'),  # Артикул ЭП
                    self.truncate_text(product.get('title', 'Без названия'), 50),  # Наименование
                    self.format_price(product.get('price_regular')),  # Цена неакционная
                    self.format_price(product.get('price_discount')),  # Цена акционная
                    f"{product.get('discount_percent', 0)}%" if product.get('discount_percent') else "Нет скидки",  # % скидки
                    product.get('material', 'Не указан'),  # Материал товара
                    product.get('brand', 'Не указан'),  # Бренд
                    product.get('collection', 'Не указана'),  # Коллекция
                    product.get('color', 'Не указан'),  # Цвет
                    "В наличии" if product.get('availability') == 'available' else "Нет в наличии",  # Наличие
                    self.truncate_text(product.get('composition', 'Не указана'), 30),  # Комплектация
                    product.get('type', 'Не указан'),  # Тип
                    product.get('packaging', 'Не указана'),  # Упаковка
                    product.get('quantity', 'Не указано'),  # Количество предметов
                    product.get('size', 'Не указан'),  # Размер/Объем
                    self.format_source(product.get('source_site', 'unknown'))  # Источник
                ]
                
                # Вставка в таблицу
                item_id = self.tree.insert("", "end", values=values)
                
                # Подсчет извлеченных характеристик
                char_count = len([v for v in [
                    product.get('material'), product.get('brand'), product.get('color'),
                    product.get('type'), product.get('quantity'), product.get('size'),
                    product.get('composition'), product.get('packaging')
                ] if v and v != 'Не указан' and v != 'Не указана' and v != 'Не указано'])
                
                logger.info(f"✅ Добавлен в расширенную таблицу: {product.get('title', 'Без названия')[:30]}... ({char_count} характеристик)")
                
            except Exception as e:
                logger.error(f"❌ Ошибка добавления товара в расширенную таблицу: {e}")
                continue
        
        # Обновление информации о результатах
        total_characteristics = 0
        for product in results:
            char_count = len([v for v in [
                product.get('material'), product.get('brand'), product.get('color'),
                product.get('type'), product.get('quantity'), product.get('size'),
                product.get('composition'), product.get('packaging')
            ] if v and v not in ['Не указан', 'Не указана', 'Не указано']])
            total_characteristics += char_count
        
        avg_characteristics = total_characteristics / len(results) if results else 0
        self.results_info_label.configure(
            text=f"Найдено: {len(results)} товаров (ср. {avg_characteristics:.1f} характеристик на товар)"
        )
        
        if results:
            self.update_status(f"✅ Расширенный поиск завершен. Найдено {len(results)} товаров с детальными данными")
            messagebox.showinfo("Успех", f"Расширенный поиск завершен!\nНайдено товаров: {len(results)}\nИзвлечено характеристик: {total_characteristics}")
        else:
            self.update_status("⚠️ Товары не найдены")
            messagebox.showwarning("Результат", "Товары не найдены.\nПроверьте правильность кодов товаров.")
    
    def truncate_text(self, text, max_length):
        """Обрезка текста до максимальной длины."""
        if not text or text in ['Не указан', 'Не указана', 'Не указано']:
            return text
        return text[:max_length] + "..." if len(text) > max_length else text
    
    def format_price(self, price):
        """Форматирование цены."""
        if not price:
            return "Не указана"
        try:
            price_num = int(price)
            return f"{price_num:,}".replace(',', ' ')
        except:
            return str(price)
    
    def format_source(self, source):
        """Форматирование источника."""
        site_icons = {
            'rozetka': '🛒 Rozetka',
            'epicentr': '🏠 Epicentr',
            'comfy': '💻 Comfy',
            'allo': '📱 Allo'
        }
        return site_icons.get(source, f'🌐 {source}')
    
    def search_completed(self):
        """Завершение поиска."""
        self.is_searching = False
        self.search_button.configure(state="normal", text="🔍 Начать расширенный поиск")
        self.progress_bar.set(1.0)
        
    def update_status(self, status):
        """Обновление статуса."""
        self.status_label.configure(text=status)
        
    def show_error(self, error_msg):
        """Показ ошибки."""
        self.update_status("❌ Ошибка расширенного поиска")
        messagebox.showerror("Ошибка", error_msg)
        
    def clear_results(self):
        """Очистка результатов."""
        self.product_code_entry.delete(0, "end")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.scraped_data = []
        self.results_info_label.configure(text="Найдено: 0 товаров")
        self.update_status("Готов к расширенному поиску")
        self.progress_bar.set(0)
    
    def on_item_double_click(self, event):
        """Обработчик двойного клика по элементу таблицы."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            article = item['values'][0]  # Артикул - первая колонка
            
            product = None
            for p in self.scraped_data:
                if p.get('article') == article or p.get('search_code') == article:
                    product = p
                    break
            
            if not product:
                messagebox.showwarning("Предупреждение", "Товар не найден")
                return
            
            self.show_enhanced_product_details(product)
    
    def on_right_click(self, event):
        """Обработчик правого клика - показывает контекстное меню."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            article = item['values'][0]
            
            product = None
            for p in self.scraped_data:
                if p.get('article') == article or p.get('search_code') == article:
                    product = p
                    break
            
            if product:
                self.show_action_menu(product)
    
    def show_enhanced_product_details(self, product):
        """Показывает расширенные детали товара."""
        # Создаем окно с детальной информацией
        details_window = ctk.CTkToplevel(self.root)
        details_window.title("Расширенная информация о товаре")
        details_window.geometry("800x600")
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Центрируем окно
        details_window.update_idletasks()
        x = (details_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (details_window.winfo_screenheight() // 2) - (600 // 2)
        details_window.geometry(f"800x600+{x}+{y}")
        
        # Создаем прокручиваемый фрейм
        scrollable_frame = ctk.CTkScrollableFrame(details_window, width=750, height=550)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            scrollable_frame,
            text=f"📦 Расширенная информация о товаре",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Основная информация
        self.add_detail_section(scrollable_frame, "Основная информация", [
            ("Артикул ЭП:", product.get('article', 'Не указан')),
            ("Наименование:", product.get('title', 'Не указано')),
            ("Источник:", self.format_source(product.get('source_site', 'unknown'))),
            ("Наличие:", "В наличии" if product.get('availability') == 'available' else "Нет в наличии")
        ])
        
        # Ценовая информация
        self.add_detail_section(scrollable_frame, "Ценовая информация", [
            ("Цена неакционная:", f"{self.format_price(product.get('price_regular'))} ₴"),
            ("Цена акционная:", f"{self.format_price(product.get('price_discount'))} ₴"),
            ("Процент скидки:", f"{product.get('discount_percent', 0)}%" if product.get('discount_percent') else "Нет скидки")
        ])
        
        # Характеристики товара
        self.add_detail_section(scrollable_frame, "Характеристики товара", [
            ("Материал:", product.get('material', 'Не указан')),
            ("Бренд:", product.get('brand', 'Не указан')),
            ("Коллекция:", product.get('collection', 'Не указана')),
            ("Цвет:", product.get('color', 'Не указан')),
            ("Тип:", product.get('type', 'Не указан'))
        ])
        
        # Дополнительная информация
        self.add_detail_section(scrollable_frame, "Дополнительная информация", [
            ("Комплектация:", product.get('composition', 'Не указана')),
            ("Упаковка:", product.get('packaging', 'Не указана')),
            ("Количество предметов:", product.get('quantity', 'Не указано')),
            ("Размер/Объем:", product.get('size', 'Не указан'))
        ])
        
        # Кнопки действий
        actions_frame = ctk.CTkFrame(scrollable_frame)
        actions_frame.pack(fill="x", pady=20)
        
        if product.get('product_url'):
            open_link_btn = ctk.CTkButton(
                actions_frame,
                text="🔗 Открыть ссылку на товар",
                command=lambda: self.open_product_link(product, details_window),
                width=200
            )
            open_link_btn.pack(side="left", padx=10, pady=10)
        
        if product.get('image_url'):
            open_image_btn = ctk.CTkButton(
                actions_frame,
                text="🖼️ Открыть изображение",
                command=lambda: self.open_product_image(product, details_window),
                width=200
            )
            open_image_btn.pack(side="left", padx=10, pady=10)
        
        close_btn = ctk.CTkButton(
            actions_frame,
            text="❌ Закрыть",
            command=details_window.destroy,
            width=150
        )
        close_btn.pack(side="right", padx=10, pady=10)
    
    def add_detail_section(self, parent, title, items):
        """Добавляет секцию с деталями."""
        # Заголовок секции
        section_title = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title.pack(anchor="w", pady=(20, 10))
        
        # Фрейм для элементов секции
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        for label_text, value_text in items:
            item_frame = ctk.CTkFrame(section_frame)
            item_frame.pack(fill="x", padx=10, pady=5)
            
            label = ctk.CTkLabel(
                item_frame,
                text=label_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=150
            )
            label.pack(side="left", padx=10, pady=5)
            
            value = ctk.CTkLabel(
                item_frame,
                text=str(value_text),
                font=ctk.CTkFont(size=12),
                wraplength=400
            )
            value.pack(side="left", padx=10, pady=5, fill="x", expand=True)
    
    def show_action_menu(self, product):
        """Показывает меню с доступными действиями для товара."""
        actions = []
        if product.get('product_url'):
            actions.append("🔗 Открыть ссылку на товар")
        if product.get('image_url'):
            actions.append("🖼️ Открыть изображение")
        
        if not actions:
            messagebox.showwarning("Предупреждение", "Нет доступных действий для этого товара")
            return
        
        # Создаем окно выбора действия
        action_window = ctk.CTkToplevel(self.root)
        action_window.title("Выберите действие")
        action_window.geometry("400x300")
        action_window.transient(self.root)
        action_window.grab_set()
        
        # Центрируем окно
        action_window.update_idletasks()
        x = (action_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (action_window.winfo_screenheight() // 2) - (300 // 2)
        action_window.geometry(f"400x300+{x}+{y}")
        
        # Заголовок
        title_label = ctk.CTkLabel(
            action_window, 
            text=f"Товар: {product.get('title', 'Без названия')[:50]}...",
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=350
        )
        title_label.pack(pady=20, padx=20)
        
        # Кнопки действий
        if product.get('product_url'):
            open_link_btn = ctk.CTkButton(
                action_window,
                text="🔗 Открыть ссылку на товар",
                command=lambda: self.open_product_link(product, action_window),
                width=300,
                height=40
            )
            open_link_btn.pack(pady=10)
        
        if product.get('image_url'):
            open_image_btn = ctk.CTkButton(
                action_window,
                text="🖼️ Открыть изображение",
                command=lambda: self.open_product_image(product, action_window),
                width=300,
                height=40
            )
            open_image_btn.pack(pady=10)
        
        # Кнопка детальной информации
        details_btn = ctk.CTkButton(
            action_window,
            text="📋 Показать все характеристики",
            command=lambda: [action_window.destroy(), self.show_enhanced_product_details(product)],
            width=300,
            height=40
        )
        details_btn.pack(pady=10)
        
        # Кнопка закрытия
        close_btn = ctk.CTkButton(
            action_window,
            text="❌ Закрыть",
            command=action_window.destroy,
            width=300,
            height=40
        )
        close_btn.pack(pady=20)
    
    def open_product_link(self, product, window):
        """Открывает ссылку на товар в браузере."""
        try:
            product_url = product.get('product_url')
            if product_url:
                if not product_url.startswith('http'):
                    source_site = product.get('source_site', 'rozetka')
                    site_configs = {
                        'rozetka': 'https://rozetka.com.ua',
                        'epicentr': 'https://epicentrk.ua',
                        'comfy': 'https://comfy.ua',
                        'allo': 'https://allo.ua'
                    }
                    base_url = site_configs.get(source_site, 'https://rozetka.com.ua')
                    product_url = urljoin(base_url, product_url)
                
                logger.info(f"🔗 Открываем ссылку: {product_url}")
                webbrowser.open(product_url)
                window.destroy()
            else:
                messagebox.showerror("Ошибка", "Ссылка на товар отсутствует")
        except Exception as e:
            logger.error(f"❌ Ошибка открытия ссылки: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть ссылку: {str(e)}")
    
    def open_product_image(self, product, window):
        """Открывает изображение товара в браузере."""
        try:
            image_url = product.get('image_url')
            if image_url:
                if not image_url.startswith('http'):
                    source_site = product.get('source_site', 'rozetka')
                    site_configs = {
                        'rozetka': 'https://rozetka.com.ua',
                        'epicentr': 'https://epicentrk.ua',
                        'comfy': 'https://comfy.ua',
                        'allo': 'https://allo.ua'
                    }
                    base_url = site_configs.get(source_site, 'https://rozetka.com.ua')
                    image_url = urljoin(base_url, image_url)
                
                logger.info(f"🖼️ Открываем изображение: {image_url}")
                webbrowser.open(image_url)
                window.destroy()
            else:
                messagebox.showerror("Ошибка", "Изображение товара отсутствует")
        except Exception as e:
            logger.error(f"❌ Ошибка открытия изображения: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {str(e)}")
    
    def export_enhanced_csv(self):
        """Экспорт расширенных данных в CSV."""
        if not self.scraped_data:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname="enhanced_products_data.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    fieldnames = [
                        'Артикул ЭП', 'Наименование с сайта', 'Цена неакционная', 'Цена акционная', '% скидки',
                        'Материал товара', 'Бренд', 'Коллекция', 'Цвет', 'Наличие',
                        'Комплектация', 'Тип', 'Упаковка', 'Количество предметов', 'Размер/Объем',
                        'Источник', 'URL товара', 'URL изображения'
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for product in self.scraped_data:
                        writer.writerow({
                            'Артикул ЭП': product.get('article', 'Не указан'),
                            'Наименование с сайта': product.get('title', 'Не указано'),
                            'Цена неакционная': product.get('price_regular', 'Не указана'),
                            'Цена акционная': product.get('price_discount', 'Не указана'),
                            '% скидки': product.get('discount_percent', 'Нет скидки'),
                            'Материал товара': product.get('material', 'Не указан'),
                            'Бренд': product.get('brand', 'Не указан'),
                            'Коллекция': product.get('collection', 'Не указана'),
                            'Цвет': product.get('color', 'Не указан'),
                            'Наличие': 'В наличии' if product.get('availability') == 'available' else 'Нет в наличии',
                            'Комплектация': product.get('composition', 'Не указана'),
                            'Тип': product.get('type', 'Не указан'),
                            'Упаковка': product.get('packaging', 'Не указана'),
                            'Количество предметов': product.get('quantity', 'Не указано'),
                            'Размер/Объем': product.get('size', 'Не указан'),
                            'Источник': product.get('source_site', 'unknown'),
                            'URL товара': product.get('product_url', ''),
                            'URL изображения': product.get('image_url', '')
                        })
                
                messagebox.showinfo("Успех", f"Расширенные данные экспортированы в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")
    
    def export_enhanced_json(self):
        """Экспорт расширенных данных в JSON."""
        if not self.scraped_data:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialname="enhanced_products_data.json"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as jsonfile:
                    json.dump(self.scraped_data, jsonfile, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Успех", f"Расширенные данные экспортированы в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")
    
    def test_enhanced_search(self):
        """Тестовая функция для отладки расширенного поиска."""
        def run_enhanced_test():
            try:
                logger.info("=== НАЧАЛО ТЕСТА РАСШИРЕННОГО ПОИСКА ===")
                
                # Тестовые коды с расширенным извлечением
                test_cases = [
                    ('rozetka', '497951464', 'Скляні форми для запікання'),
                    ('allo', '1124218', 'Навушники Redmi Buds 6'),
                ]
                
                for site, code, expected in test_cases:
                    try:
                        logger.info(f"\n--- Тест расширенного поиска для {site.upper()} с кодом {code} ---")
                        
                        # Тестируем расширенный поиск
                        results = self.scraper.search_on_site(code, site)
                        
                        logger.info(f"📊 Результат для {site}: {len(results)} товаров")
                        
                        if results:
                            for i, result in enumerate(results):
                                logger.info(f"  📦 Товар {i+1}: {result.get('title', 'Без названия')[:50]}")
                                logger.info(f"    🔢 Артикул: {result.get('article', 'Не указан')}")
                                logger.info(f"    💰 Цена обычная: {result.get('price_regular', 'Не указана')}")
                                logger.info(f"    💰 Цена акционная: {result.get('price_discount', 'Не указана')}")
                                logger.info(f"    🎯 Скидка: {result.get('discount_percent', 'Нет')}%")
                                logger.info(f"    🧱 Материал: {result.get('material', 'Не указан')}")
                                logger.info(f"    🏷️ Бренд: {result.get('brand', 'Не указан')}")
                                logger.info(f"    🎨 Цвет: {result.get('color', 'Не указан')}")
                                logger.info(f"    📝 Тип: {result.get('type', 'Не указан')}")
                                logger.info(f"    📦 Количество: {result.get('quantity', 'Не указано')}")
                                logger.info(f"    📏 Размер: {result.get('size', 'Не указан')}")
                                
                                # Подсчет извлеченных характеристик
                                char_count = len([v for v in [
                                    result.get('material'), result.get('brand'), result.get('color'),
                                    result.get('type'), result.get('quantity'), result.get('size'),
                                    result.get('composition'), result.get('packaging')
                                ] if v and v not in ['Не указан', 'Не указана', 'Не указано']])
                                
                                logger.info(f"    📋 Извлечено характеристик: {char_count}/8")
                        else:
                            logger.warning(f"  ⚠️ Товары не найдены на {site}")
                            
                        time.sleep(3)
                        
                    except Exception as e:
                        logger.error(f"❌ Ошибка теста для {site}: {e}")
                
                logger.info("=== КОНЕЦ ТЕСТА РАСШИРЕННОГО ПОИСКА ===")
                
                self.root.after(0, lambda: messagebox.showinfo("Тест завершен", 
                    "Тест расширенного поиска завершен.\nПроверьте логи для подробной информации о извлеченных характеристиках."))
                
            except Exception as e:
                logger.error(f"❌ Ошибка выполнения теста: {e}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка теста", f"Ошибка: {str(e)}"))
        
        # Запускаем тест в отдельном потоке
        test_thread = threading.Thread(target=run_enhanced_test)
        test_thread.daemon = True
        test_thread.start()
    
    def install_packages(self):
        """Установка необходимых пакетов."""
        def install():
            try:
                self.update_status("⚙️ Установка пакетов...")
                self.install_button.configure(state="disabled", text="Установка...")
                
                required_packages = [
                    'cloudscraper',
                    'beautifulsoup4',
                    'lxml',
                    'requests'
                ]
                
                logger.info("📦 Установка необходимых пакетов...")
                for package in required_packages:
                    try:
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                        logger.info(f"✅ {package} установлен успешно")
                    except subprocess.CalledProcessError as e:
                        logger.error(f"❌ Ошибка установки {package}: {e}")
                
                self.root.after(0, lambda: [
                    self.update_status("✅ Пакеты установлены"),
                    self.install_button.configure(state="normal", text="⚙️ Установить пакеты"),
                    messagebox.showinfo("Успех", "Все необходимые пакеты установлены")
                ])
            except Exception as e:
                error_msg = f"Ошибка установки: {str(e)}"
                self.root.after(0, lambda: [
                    self.update_status("❌ Ошибка установки"),
                    self.install_button.configure(state="normal", text="⚙️ Установить пакеты"),
                    messagebox.showerror("Ошибка", error_msg)
                ])
        
        install_thread = threading.Thread(target=install)
        install_thread.daemon = True
        install_thread.start()
    
    def run(self):
        """Запуск приложения."""
        self.root.mainloop()


def main():
    """Главная функция для запуска расширенного приложения."""
    try:
        print("🚀 Запуск Enhanced Universal Product Scraper с расширенным извлечением данных...")
        print("✅ Rozetka: исправлены селекторы + расширенное извлечение характеристик")
        print("✅ Allo: исправлены селекторы + расширенное извлечение характеристик")
        print("⚙️ Epicentr и Comfy: базовые селекторы + расширенное извлечение")
        print("📋 Извлекаемые данные: артикул, цены, материал, бренд, цвет, тип, количество, размер и др.")
        app = EnhancedScraperUI()
        app.run()
    except Exception as e:
        print(f"❌ Ошибка запуска приложения: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()