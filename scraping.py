import requests
import pandas as pd
import time
import sys
import signal

appid = 570
language = 'english'
output_file = 'steam_reviews_labeled.csv'
max_pages = 150  # 150 halaman × 25 review = 3750 review
all_reviews = []
cursor = '*'

# Daftar kata positif dan negatif sederhana untuk labeling teks
positive_words = set(['good', 'great', 'love', 'enjoy', 'fun', 'best', 'awesome', 'nice', 'like'])
negative_words = set(['bad', 'worst', 'bug', 'hate', 'boring', 'terrible', 'dislike', 'slow'])

def labeling_text(review):
    if not isinstance(review, str):
        return 'neutral'
    review = review.lower()
    pos_count = sum(word in review for word in positive_words)
    neg_count = sum(word in review for word in negative_words)
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'

def signal_handler(sig, frame):
    print("\n[⚠️] Scraping dihentikan manual. Menyimpan data...")
    save_to_csv()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def save_to_csv():
    df = pd.DataFrame(all_reviews)
    df.to_csv(output_file, index=False)
    print(f"[💾] {len(all_reviews)} review disimpan ke '{output_file}'")

def get_reviews_page(appid, cursor, language='english'):
    url = f"https://store.steampowered.com/appreviews/{appid}"
    params = {
        'json': 1,
        'filter': 'recent',
        'language': language,
        'cursor': cursor,
        'purchase_type': 'all',
        'num_per_page': 25
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"[❌] Request gagal: {r.status_code}")
        return None

print(f"[📥] Mulai scraping review AppID: {appid}")
print(f"[🎯] Target: {max_pages * 25} review (estimasi)\n")

for page in range(max_pages):
    print(f"[🔄] Mengambil halaman {page + 1}...")

    result = get_reviews_page(appid, cursor, language)
    if result is None or 'reviews' not in result:
        print("[⚠️] Tidak ada review ditemukan atau error.")
        break

    for r in result['reviews']:
        review_text = r['review']
        sentiment_label = labeling_text(review_text)
        all_reviews.append({
            'review': review_text,
            'sentiment': sentiment_label
        })

    cursor = result['cursor']
    print(f"[✅] Total review terkumpul: {len(all_reviews)}")

    if len(result['reviews']) == 0:
        print("[ℹ️] Review habis, scraping dihentikan.")
        break

    time.sleep(1)

save_to_csv()
print("\n[🏁] Scraping selesai.")
