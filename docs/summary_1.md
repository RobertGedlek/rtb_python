# 📊 RTB Python — Podsumowanie projektu

## 🎯 Cel projektu

Projekt **rtb_python** to **symulator ekosystemu Real-Time Bidding (RTB)** — systemu aukcji reklamowych w czasie rzeczywistym. Symuluje przepływ zapytań bidowych od wydawców stron internetowych do platformy SSP (Supply-Side Platform).

---

## 🏗️ Architektura

Projekt składa się z dwóch głównych komponentów:

```
Publisher(TechBlog)    ─┐
Publisher(SportPortal) ─┼──► HTTP POST /bid/request ──► SSP Server (FastAPI)
Publisher(NewsSite)    ─┘         (JSON BidRequest)        (loguje i potwierdza)
```

---

## 📦 Struktura katalogów

```
src/
├── logging_config.py          # Centralna konfiguracja logowania
├── run_simulation.py          # Punkt startowy symulacji
├── publisher/
│   ├── config.py              # Konfiguracja wydawcy (PublisherConfig)
│   ├── engine.py              # Silnik generujący ruch (Publisher)
│   └── models.py              # Model danych (BidRequest)
└── ssp/
    └── server.py              # Serwer SSP odbierający zapytania (FastAPI)
```

---

## 📤 Publisher (Wydawca) — `src/publisher/`

### `PublisherConfig` (`config.py`)
Niezmienialny dataclass przechowujący konfigurację wydawcy:
- **name** — nazwa wydawcy
- **domain** — domena strony
- **category** — kategoria treści (np. technology, sports, news)
- **min_floor / max_floor** — zakres minimalnej ceny za wyświetlenie reklamy
- **target_url** — adres endpointu SSP (domyślnie `http://127.0.0.1:8000/bid/request`)

Zawiera walidację danych w `__post_init__`.

### `BidRequest` (`models.py`)
Niezmienialny dataclass reprezentujący zapytanie bidowe:
- **id** — unikalny identyfikator (UUID)
- **domain** — domena wydawcy
- **category** — kategoria treści
- **bid_floor** — minimalna cena (nie może być ujemna)

Posiada metodę `to_dict()` do serializacji na JSON.

### `Publisher` (`engine.py`)
Silnik symulacji dla pojedynczego wydawcy:
- `generate_single_request()` — tworzy losowy `BidRequest` z ceną z zakresu `[min_floor, max_floor]`
- `run_simulation(interval)` — w nieskończonej pętli generuje i wysyła zapytania HTTP POST do SSP z określonym interwałem (domyślnie 1s)

---

## 📥 SSP Server — `src/ssp/`

### `server.py`
Serwer **FastAPI** nasłuchujący na `127.0.0.1:8000`:
- Endpoint `POST /bid/request` — odbiera zapytania bidowe w formacie JSON
- Loguje otrzymane zapytania
- Zwraca `{"status": "received"}`
- Na razie pełni rolę prostego odbiornika — **nie podejmuje jeszcze decyzji o licytacji**

---

## ▶️ Uruchomienie — `run_simulation.py`

Punkt startowy całej symulacji:
1. Inicjalizuje centralny system logowania
2. Definiuje **3 wydawców** z różnymi konfiguracjami:

| Wydawca       | Domena          | Kategoria    | Cena min–max ($) |
|---------------|-----------------|--------------|-------------------|
| TechBlog      | tech-world.com  | technology   | 1.50 – 4.00      |
| SportPortal   | fast-sports.pl  | sports       | 0.50 – 1.20      |
| NewsSite      | daily-news.com  | news         | 0.10 – 0.80      |

3. Uruchamia wszystkich wydawców **równolegle** w osobnych wątkach (`ThreadPoolExecutor`) z interwałem 2 sekund

---

## 🔧 Logowanie — `logging_config.py`

Centralna konfiguracja logów dla całej aplikacji:
- Format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- Domyślny poziom: `INFO`
- Funkcja `get_logger(name)` zwraca instancję loggera o podanej nazwie

---

## 🛠️ Technologie

- **Python 3.13**
- **FastAPI** + **Uvicorn** — serwer HTTP
- **requests** — wysyłanie zapytań HTTP
- **dataclasses** — modele danych
- **concurrent.futures** — wielowątkowość
- **logging** — system logowania



