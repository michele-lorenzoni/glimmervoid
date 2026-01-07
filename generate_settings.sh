#!/bin/bash

# Script per generare settings.yml con domini bloccati da file esterno
# Uso: ./generate_settings.sh

set -e

# === CONFIGURAZIONE ===
# Rileva se siamo in Docker o in ambiente locale
if [ -f "/tmp/settings.yml.template" ]; then
    # Ambiente Docker
    DOMAINS_FILE="/tmp/blocked_domains.txt"
    SETTINGS_TEMPLATE="/tmp/settings.yml.template"
    SETTINGS_OUTPUT="/tmp/settings.yml"
    BACKUP_DIR="/tmp/backups"
else
    # Ambiente locale
    DOMAINS_FILE="blocked_domains.txt"
    SETTINGS_TEMPLATE="settings.yml.template"
    SETTINGS_OUTPUT="settings.yml"
    BACKUP_DIR="backups"
fi
SEARXNG_DIR="/etc/searxng"  # Modifica se necessario

# === FUNZIONI ===
log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
    exit 1
}

check_files() {
    if [ ! -f "$DOMAINS_FILE" ]; then
        log_error "File $DOMAINS_FILE non trovato!"
    fi
    
    if [ ! -f "$SETTINGS_TEMPLATE" ]; then
        log_error "File $SETTINGS_TEMPLATE non trovato!"
    fi
}

backup_existing() {
    if [ -f "$SETTINGS_OUTPUT" ]; then
        mkdir -p "$BACKUP_DIR"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="$BACKUP_DIR/settings.yml.$TIMESTAMP"
        cp "$SETTINGS_OUTPUT" "$BACKUP_FILE"
        log_info "Backup creato: $BACKUP_FILE"
    fi
}

generate_domains_yaml() {
    local output=""
    while IFS= read -r domain || [ -n "$domain" ]; do
        # Ignora righe vuote e commenti
        domain=$(echo "$domain" | sed 's/#.*$//' | xargs)
        if [ -n "$domain" ]; then
            output="${output}      - ${domain}\n"
        fi
    done < "$DOMAINS_FILE"
    echo -e "$output"
}

# === MAIN ===
log_info "Inizio generazione settings.yml"

check_files
backup_existing

# Genera la lista di domini formattata
DOMAINS_YAML=$(generate_domains_yaml)

# Crea il settings.yml sostituendo il placeholder
if grep -q "{{BLOCKED_DOMAINS}}" "$SETTINGS_TEMPLATE"; then
    # Usa perl per sostituzioni multilinea più affidabili
    perl -pe "s/\{\{BLOCKED_DOMAINS\}\}/${DOMAINS_YAML}/g" "$SETTINGS_TEMPLATE" > "$SETTINGS_OUTPUT"
    log_info "File $SETTINGS_OUTPUT generato con successo!"
    
    # Conta domini aggiunti
    DOMAIN_COUNT=$(grep -c "^[^#]" "$DOMAINS_FILE" || true)
    log_info "Domini bloccati inseriti: $DOMAIN_COUNT"
else
    log_error "Placeholder {{BLOCKED_DOMAINS}} non trovato in $SETTINGS_TEMPLATE"
fi

log_info "Completato!"

# Opzionale: copia in /etc/searxng se richiesto
if [ "$1" == "--install" ]; then
    if [ -w "$SEARXNG_DIR" ]; then
        cp "$SETTINGS_OUTPUT" "$SEARXNG_DIR/settings.yml"
        log_info "File copiato in $SEARXNG_DIR/settings.yml"
        log_info "Riavvia SearXNG per applicare le modifiche"
    else
        log_error "Permessi insufficienti per scrivere in $SEARXNG_DIR"
    fi
fi
