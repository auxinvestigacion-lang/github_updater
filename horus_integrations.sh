#!/bin/bash

set -e

echo "=== Instalación de Custom Components ==="
mkdir -p /home/cat/config/custom_components

# URLs de los componentes en GitHub
URLS=(
    "https://raw.githubusercontent.com/auxinvestigacion-lang/update_ha_zwave/main/Horus_Integrations.zip"
)

# Directorio de destino de Home Assistant
DESTINO="/home/cat/config/custom_components/"

for url in "${URLS[@]}"; do
    echo "Procesando: $url..."
    curl -sSL "$url" -o /tmp/componente.zip

    if unzip -t /tmp/componente.zip >/dev/null 2>&1; then
        unzip -o /tmp/componente.zip -d "$DESTINO"
        rm -f /tmp/componente.zip
        echo " -> Instalado exitosamente."
    else
        echo " -> ERROR: No se pudo descargar un ZIP válido desde $url"
        rm -f /tmp/componente.zip
        exit 1
    fi
done

echo "Todos los componentes se instalaron correctamente."

docker restart homeassistant || true
