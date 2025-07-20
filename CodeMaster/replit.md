# Product Scraper Pro - Replit Configuration

## Overview

Product Scraper Pro is a modernized, universal product scraper application built with Python. The application features a sophisticated GUI built with CustomTkinter and provides multiple scraping methods to extract product information from various e-commerce websites. The system uses a hybrid approach combining CloudScraper and Selenium WebDriver for maximum compatibility and reliability.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **GUI Framework**: CustomTkinter (modern tkinter alternative)
- **UI Components**: Modular component system with reusable widgets
- **Theme Management**: Dark/light theme support with multiple color schemes
- **Layout**: Multi-panel interface with:
  - Main control panel for input and settings
  - Progress tracking and logging area
  - Results display with export capabilities
  - Status bar with real-time updates

### Backend Architecture
- **Core Pattern**: Modular scraper architecture with base classes
- **Scraping Methods**: 
  - CloudScraper for Cloudflare bypass
  - Selenium WebDriver for JavaScript-heavy sites
  - Hybrid approach with intelligent fallback
- **Multi-threading**: Concurrent scraping with thread pool management
- **Error Handling**: Comprehensive exception handling with retry mechanisms

## Key Components

### Scraper Engine (`scraper/`)
- **BaseScraper**: Abstract base class defining common interface
- **CloudScraperScraper**: Fast scraper for simple pages using cloudscraper library
- **SeleniumScraper**: Browser automation for complex JavaScript sites
- **HybridScraper**: Intelligent dispatcher that chooses optimal method

### User Interface (`ui/`)
- **MainWindow**: Primary application window with CustomTkinter
- **Components**: Reusable UI components (frames, progress bars, status indicators)
- **Dialogs**: Settings, export, and configuration dialogs
- **Themes**: Theme management system with color customization

### Utilities (`utils/`)
- **Config**: Configuration management with INI file persistence
- **Logger**: Advanced logging system with colored output and thread safety
- **Export**: Multi-format export (CSV, JSON, Excel) with customizable options

### Data Models
- **ProductInfo**: Structured product data with comprehensive fields
- **ScrapingResult**: Wrapper for scraping operations with status tracking
- **ScrapingStatus**: Enumeration for operation states

## Data Flow

1. **Input Processing**: User provides product IDs and selects target sites
2. **Method Selection**: System chooses optimal scraping method based on site requirements
3. **Concurrent Execution**: Multiple products scraped simultaneously using thread pools
4. **Data Extraction**: Product information extracted using site-specific selectors
5. **Result Aggregation**: Results collected and displayed in real-time
6. **Export Generation**: Final results exported to various formats (CSV, JSON, Excel)

### Error Handling Flow
- Primary method attempts scraping
- On failure, fallback to alternative method (if enabled)
- Retry mechanism with exponential backoff
- Comprehensive error logging and user notification

## External Dependencies

### Core Libraries
- **customtkinter**: Modern GUI framework
- **cloudscraper**: Cloudflare bypass functionality
- **selenium**: Browser automation
- **undetected-chromedriver**: Anti-detection Chrome driver
- **beautifulsoup4**: HTML parsing
- **trafilatura**: Text extraction from web pages

### Optional Dependencies
- **openpyxl**: Excel export functionality
- **pandas**: Advanced data manipulation
- **webdriver-manager**: Automatic WebDriver management

### System Dependencies
- Chrome/Chromium browser (for Selenium)
- ChromeDriver (automatically managed)

## Deployment Strategy

### Local Development
- Python 3.8+ environment
- Virtual environment with requirements.txt
- Configuration through config.ini file
- Logging to both console and file

### Distribution
- Standalone executable using PyInstaller
- All dependencies bundled
- Portable configuration system
- Cross-platform compatibility (Windows, macOS, Linux)

### File Structure
```
├── main.py                 # Application entry point
├── scraper/               # Core scraping engine
│   ├── base_scraper.py    # Abstract base classes
│   ├── cloudscraper_scraper.py
│   ├── selenium_scraper.py
│   └── site_scrapers.py   # Hybrid scraper
├── ui/                    # User interface
│   ├── main_window.py     # Main application window
│   ├── components.py      # Reusable UI components
│   ├── dialogs.py         # Settings and export dialogs
│   └── themes.py          # Theme management
├── utils/                 # Utility modules
│   ├── config.py          # Configuration management
│   ├── logger.py          # Logging system
│   └── export.py          # Export functionality
├── assets/                # Resources and icons
└── attached_assets/       # Sample data and debugging files
```

### Configuration Management
- INI-based configuration with sensible defaults
- Runtime settings modification through GUI
- Automatic backup and recovery of user preferences
- Environment-specific overrides support