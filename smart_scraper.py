import csv
import time
import streamlit as st
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import re

# --- Site Config ---
SITES = {
    "purina_switzerland": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.ch/fr/chien/alimentation-chien",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.ch/fr/chien/alimentation-chien?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.ch/fr/chat/alimentation-chat",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.ch/fr/chat/alimentation-chat?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_czec_republic": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.cz/pes/krmivo-pro-psy",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "a[class*=adimo]",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.cz/pes/krmivo-pro-psy?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.cz/kocka/krmivo-pro-kocky",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "a[class*=adimo]",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.cz/kocka/krmivo-pro-kocky?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_denmark": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.dk/hund/hundemad",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.dk/hund/hundemad?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.dk/kat/kattemad",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.dk/kat/kattemad?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_slovenia": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.si/pes/hrana-za-pse",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "div.adimoWidget",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.si/pes/hrana-za-pse?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.si/pes/hrana-za-pse",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "div.adimoWidget",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.si/pes/hrana-za-pse?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_finland": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.fi/koira/koiranruoka",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.fi/koira/koiranruoka?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.fi/koira/koiranruoka",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.fi/koira/koiranruoka?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_romania": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.ro/caine/hrana-caini",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "div.adimoWidget",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.ro/caine/hrana-caini?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.ro/pisica/hrana-pisici",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "div.adimoWidget",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.ro/pisica/hrana-pisici?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_sweden": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.se/hund/hundmat",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.se/hund/hundmat?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.se/katt/kattmat",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.se/katt/kattmat?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_bulgaria": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.bg/kucheta/hrana-za-kucheta",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.bg/kucheta/hrana-za-kucheta?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.bg/kotki/hrana-za-kotki",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.bg/kotki/hrana-za-kotki?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_croatia": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.hr/pas/hrana-za-pse",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.hr/pas/hrana-za-pse?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.hr/macke/hrana-za-macke",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.hr/macke/hrana-za-macke?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_israel": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.co.il/dog/dog-food",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint, div.adimoWidget, a[class*=adimo]",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.co.il/dog/dog-food?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.co.il/cat/cat-food",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint, div.adimoWidget, a[class*=adimo]",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.co.il/cat/cat-food?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_serbia": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.rs/pas/hrana-za-pse",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.rs/pas/hrana-za-pse?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.rs/macke/hrana-za-macke",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.rs/macke/hrana-za-macke?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_norway": {
        "categories": {
            "dogs": {
                "url": "https://www.purina.no/hund/hundemat",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.no/hund/hundemat?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina.no/katt/kattemat",
                "type": "listing",
                "product_container_selector": "div.col-12.col-md-6.col-lg-4.col-xl-3",
                "title_selector": ".dsu-product__title > h3",
                "buy_button_selector": "button.adimo-multi-touchpoint",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina.no/katt/kattemat?page={page}",
                "pagination_start_page": 0
            }
        }
    },
    "purina_mena": {
        "categories": {
            "dogs": {
                "url": "https://www.purina-arabia.com/dog/dog-food",
                "type": "listing",
                "product_container_selector": ".views-view-bs4-grid > .row > *",
                "title_selector": "h3",
                "buy_button_selector": "div.adimoWidget",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina-arabia.com/dog/dog-food?page={page}",
                "pagination_start_page": 0
            },
            "cats": {
                "url": "https://www.purina-arabia.com/cat/cat-food",
                "type": "listing",
                "product_container_selector": ".views-view-bs4-grid > .row > *",
                "title_selector": "h3",
                "buy_button_selector": "div.adimoWidget",
                "pagination_last_selector": ".view-header li.pager__item--last",
                "pagination_url_template": "https://www.purina-arabia.com/cat/cat-food?page={page}",
                "pagination_start_page": 0
            }
        }
    }
}

def extract_listing(page, config, debug=False):
    results = []
    product_containers = page.locator(config['product_container_selector'])
    count = product_containers.count()
    if debug:
        st.write(f"Found {count} containers on page")

    for i in range(count):
        container = product_containers.nth(i)
        title = container.locator(config['title_selector']).inner_text().strip()
        has_button = container.locator(config['buy_button_selector']).count() > 0
        results.append({"title": title, "buy_button": has_button})
    return results

def save_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "buy_button"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def get_last_page_number(page, selector, debug=False):
    try:
        page.wait_for_selector(selector, timeout=5000)
        element = page.locator(selector).first
        href = element.locator("a").get_attribute("href")
        match = re.search(r"page=(\d+)", href)
        return int(match.group(1)) if match else 1
    except Exception as e:
        print("Pagination detection failed:", e)
        return 1  # fallback to 1 if fails

def run_scraper(site_key, subcategory_key=None, debug=False):
    site_config = SITES.get(site_key)
    if not site_config:
        return [], "Invalid site key"

    config = (
        site_config["categories"][subcategory_key]
        if subcategory_key and "categories" in site_config
        else site_config
    )

    all_results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(config['url'])
        time.sleep(2)

        last_page = 1
        if "pagination_last_selector" in config:
            last_page = get_last_page_number(page, config['pagination_last_selector'], debug)
        start_page = config.get("pagination_start_page", 0)

        for page_num in range(start_page, last_page + 1):
            # url = (
            #     config['url'] if page_num == 0
            #     else config['pagination_url_template'].format(page=page_num)
            # )
            # page.goto(url)
            if page_num == 0:
                url = config['url']  # first page has no ?page param
            else:
                url = config['pagination_url_template'].format(page=page_num)
            page.goto(url)
            if debug:
                st.write(f"Visiting: {url}")
            time.sleep(1.5)

            results = extract_listing(page, config, debug)
            all_results.extend(results)

        filename = f"results_{site_key}"
        if subcategory_key:
            filename += f"_{subcategory_key}"
        filename += ".csv"

        save_to_csv(all_results, filename)
        return all_results, filename

# --- Streamlit UI ---
st.set_page_config(page_title="Smart Scraper MVP", layout="centered")
st.title("🕷️ Smart Product Scraper")

site_choice = st.selectbox("Choose a site to scrape:", list(SITES.keys()))

subcategory_choice = None
if "categories" in SITES[site_choice]:
    subcategory_choice = st.selectbox("Choose a category:", list(SITES[site_choice]["categories"].keys()))

debug_mode = st.checkbox("Show debug info")

if st.button("Run Scraper"):
    with st.spinner("Scraping data..."):
        results, file = run_scraper(site_choice, subcategory_choice, debug=debug_mode)

    if results:
        st.success(f"✅ Scraped {len(results)} products. See results below:")
        df = pd.DataFrame(results)
        st.dataframe(df)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", data=csv_data, file_name=file, mime="text/csv")
    else:
        st.error("❌ No results found or an error occurred.")
