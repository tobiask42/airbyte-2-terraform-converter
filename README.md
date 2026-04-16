# Airbyte → Terraform Converter

Tool zur automatisierten Überführung bestehender Airbyte-Konfigurationen in deklarative Terraform-Strukturen.

## Hintergrund

Dieses Projekt entstand im beruflichen Kontext. Die Veröffentlichung erfolgt mit Genehmigung. Es wurden keine vertraulichen oder unternehmensspezifischen Informationen übernommen.

---

## Features

- Extraktion von Airbyte-Konfigurationen über die API
- Generierung von Terraform-Ressourcen (Sources, Destinations, Connections)
- Template-basierte Code-Erzeugung (Jinja2)
- Mapping-System für unterschiedliche Connector-Typen
- Behandlung von Legacy- und inkompatiblen Feldern
- Generierung von **Terraform Import-Blöcken**
- Deterministische Erstellung reproduzierbarer `.tf`-Dateien

---

## Quick Start

```bash
uv sync
uv run python main.py --all
````

---

## Voraussetzungen

* Python 3.13+
* Zugang zu einer Airbyte API
* `uv` (Dependency Management)

---

## Konfiguration

Die Steuerung erfolgt über Dateien im `configs/`-Verzeichnis.

### 1. Umgebungsvariablen

Beispiel (`.env`):

```
ENDPOINT_AB1=https://api.airbyte.local/api/public/v1/
ENDPOINT_AB2=https://api.airbyte-v2.local/api/public/v1/
CLIENT_ID_AB1=<client_id>
CLIENT_SECRET_AB1=<client_secret>
```

---

### 2. API-Konfiguration (`api_config.yml`)

Definiert die abzurufenden Endpunkte:

```yaml
- name: sources
  endpoint: ${ENDPOINT_AB1}sources
  items_key: data
  filename: sources

- name: token
  endpoint: ${ENDPOINT_AB1}applications/token
```

---

### 3. Auswahl der Endpunkte (`api_selection.json`)

```json
{
  "tokens": {
    "source": "token"
  },
  "data": [
    "sources",
    "destinations",
    "connections"
  ]
}
```

---

## CLI Usage

```bash
uv run python main.py [OPTIONS]
```

### Optionen

* `--download` → Daten aus Airbyte laden
* `--airbyte2terraform_src` → Sources konvertieren
* `--airbyte2terraform_dest` → Destinations konvertieren
* `--airbyte2terraform_conn` → Connections konvertieren
* `--create-imports` → Import-Blöcke generieren
* `--all` → führt alle Schritte aus

---

## Output

* Terraform-Dateien (`.tf`)
* Import-Blöcke für bestehende Ressourcen
* JSON-Rohdaten
* Log-Dateien

---

## Funktionsweise (vereinfacht)

1. **Download**
   Abruf von Airbyte-Daten über API

2. **Transformation**
   Mapping und Normalisierung der Daten

3. **Terraform-Generierung**
   Erstellung von `.tf`-Dateien via Templates

4. **Import-Generierung**
   Erstellung von Terraform-Import-Blöcken

---

## Technische Details

* Python 3.13
* Jinja2 Templates
* Konfigurationsbasiertes Mapping-System
* Pipeline: Download → Transform → Generate

---

## Hinweis

Dieses Projekt ist als generisches Beispiel für IaC-Automatisierung gedacht und wurde von konkreten Umgebungen abstrahiert.