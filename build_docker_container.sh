#!/bin/bash
IMAGE_NAME="glimmervoid"

cleanup_on_interrupt() {
    echo ""
    echo ">>> Build interrotta (Ctrl+C)"
    scegli_pulizia
    exit 130
}

# esecuzione di `cleanup_on_interrupt` in caso di SIGINT SIGTERM durante la build dell'immagine docker
trap cleanup_on_interrupt SIGINT SIGTERM

scegli_pulizia() {
    echo ""
    echo "Scegli il tipo di pulizia da eseguire:"
    echo "  1) docker builder prune -f          (solo cache non più referenziata)"
    echo "  2) docker builder prune -a -f        (tutta la cache di build, anche quella attiva)"
    echo "  3) systemctl restart docker          (riavvia il daemon, dopo aver pulito)"
    echo "  4) docker system prune -a --volumes -f  (pulizia totale: immagini, container, volumi)"
    echo "  5) Nessuna pulizia"
    read -rp "Numero opzione [1-5]: " scelta

    case "$scelta" in
        1)
            sudo docker builder prune -f
            ;;
        2)
            sudo docker builder prune -a -f
            ;;
        3)
            sudo docker builder prune -a -f
            sudo systemctl restart docker
            ;;
        4)
            echo "Attenzione: rimuove anche immagini, container fermi e volumi non referenziati."
            read -rp "Confermi? [y/N]: " conferma
            if [[ "$conferma" =~ ^[Yy]$ ]]; then
                sudo docker system prune -a --volumes -f
            else
                echo "Pulizia annullata."
            fi
            ;;
        5)
            echo "Nessuna pulizia eseguita."
            ;;
        *)
            echo "Opzione non valida, nessuna pulizia eseguita."
            ;;
    esac
}

output=$(sudo docker build -t "$IMAGE_NAME" . 2>&1)
status=$?

echo "$output"

# esecuzione preventiva di pluzia dell'immagine docker in caso di errore
if [ $status -ne 0 ] && echo "$output" | grep -q "does not exist: not found"; then
    echo ">>> Rilevata cache corrotta."
    scegli_pulizia
    echo ">>> Riprovo la build..."
    sudo docker build -t "$IMAGE_NAME" .
fi