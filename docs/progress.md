# Zapasio — raport z postępów projektu

**Data:** 03.11.2026  
**Projekt:** Zapasio — Twoje zapasy pod kontrolą  
**Rodzaj:** Praca inżynierska  
**Etap:** Projektowanie bazy danych i konfiguracja backendu

## 1. Cel projektu

Celem projektu jest stworzenie aplikacji mobilnej wspomagającej zarządzanie domowymi zapasami żywności i ograniczanie marnowania jedzenia.

Planowane funkcjonalności:
- Rejestracja i logowanie użytkowników.
- Tworzenie wspólnych gospodarstw domowych.
- Zarządzanie produktami i ich ilościami.
- Definiowanie własnych miejsc przechowywania.
- Monitorowanie terminów ważności.
- Skanowanie kodów kreskowych i integracja z Open Food Facts.
- Powiadomienia o zbliżających się terminach ważności.
- Propozycje przepisów wykorzystujących dostępne produkty.

## 2. Wybrane technologie

| Warstwa | Technologia |
|---|---|
| Aplikacja mobilna | Flutter / Dart |
| Backend | Python / Django |
| REST API | Django REST Framework |
| Baza danych — rozwój | SQLite |
| Baza danych — docelowa | PostgreSQL |
| Środowisko programistyczne | PyCharm / macOS |
| Kontrola wersji | Git / GitHub |

## 3. Struktura projektu

```text
zapasio-projekt/
├── backend/
│   ├── .venv/
│   ├── config/
│   ├── households/
│   ├── inventory/
│   ├── manage.py
│   └── requirements.txt
├── docs/
└── .gitignore
```

## 4. Modele danych

### Aplikacja households

**Household**
- `name` — nazwa gospodarstwa.
- `owner` — właściciel.
- `members` — użytkownicy gospodarstwa.
- `created_at` — data utworzenia.

**Membership**
- `user` — użytkownik.
- `household` — gospodarstwo.
- `role` — rola owner/member.
- `joined_at` — data dołączenia.

Model Membership realizuje relację wiele-do-wielu pomiędzy użytkownikami a gospodarstwami. Zastosowano `through='Membership'`, aby przechowywać dodatkowe informacje o członkostwie.

### Aplikacja inventory

**Product**
- Nazwa produktu.
- Kod kreskowy.
- Marka.
- Kategoria.

**StorageLocation**
- Gospodarstwo.
- Nazwa miejsca przechowywania.

**PantryItem**
- Gospodarstwo.
- Produkt.
- Ilość.
- Data ważności.
- Miejsce przechowywania.
- Data dodania.

## 5. Najważniejsze decyzje projektowe

1. Oddzielono katalog produktów (`Product`) od konkretnych zapasów (`PantryItem`), umożliwiając przechowywanie tego samego produktu w wielu gospodarstwach.
2. Wprowadzono model `Household`, aby umożliwić wspólne zarządzanie zapasami.
3. Wykorzystano model pośredni `Membership` do obsługi członkostwa i ról.
4. Zastąpiono statyczne `STORAGE_CHOICES` osobnym modelem `StorageLocation`, umożliwiając użytkownikom definiowanie własnych miejsc przechowywania.
5. Zastosowano `ForeignKey`, `ManyToManyField`, `related_name` oraz `UniqueConstraint`.
6. Zastosowano `CASCADE` i `PROTECT` zależnie od charakteru relacji.
7. Przyjęto architekturę klient–serwer, w której aplikacja mobilna komunikuje się z Django poprzez REST API.

## 6. Stan realizacji

**Wykonane lub potwierdzone:**
- Utworzenie projektu Django i środowiska wirtualnego.
- Uruchomienie serwera developerskiego.
- Otwarcie projektu w PyCharm.
- Zaprojektowanie pięciu modeli.
- Omówienie relacji i ograniczeń bazy danych.
- Konfiguracja `INSTALLED_APPS`.
- Potwierdzenie widoczności modeli w Django Admin.

**Do sprawdzenia lub dokończenia:**
- Poprawność wszystkich migracji.
- Utworzenie danych testowych.
- Sprawdzenie relacji przez Django ORM.
- Walidacja zgodności gospodarstwa i miejsca przechowywania.
- Zapewnienie spójności właściciela gospodarstwa i jego członkostwa.

## 7. Kolejne zadania

- [ ] Przetestować dodawanie gospodarstw, członków, produktów i zapasów w Django Admin.
- [ ] Sprawdzić zapytania ORM i relacje odwrotne.
- [ ] Utworzyć pierwsze serializery Django REST Framework.
- [ ] Przygotować endpoint `GET /api/products/`.
- [ ] Przetestować API.
- [ ] Rozpocząć implementację uwierzytelniania i uprawnień.
- [ ] Przygotować pierwsze widoki aplikacji Flutter.

## 8. Podsumowanie

Zaprojektowano podstawową strukturę backendu Zapasio oraz model danych umożliwiający obsługę produktów, zapasów i współdzielonych gospodarstw domowych.

Kolejnym etapem będzie przetestowanie poprawności modeli, a następnie implementacja interfejsu REST API, który umożliwi komunikację aplikacji mobilnej z serwerem Django.
