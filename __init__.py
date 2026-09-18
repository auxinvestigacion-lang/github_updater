import os
import shutil
import logging
import aiohttp
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "github_updater"
SERVICE_UPDATE = "update_component"

# Configura aquí tus datos de GitHub
GITHUB_USER = "auxinvestigacion-lang"
GITHUB_REPO = "github_updater"
GITHUB_BRANCH = "main"

SERVICE_SCHEMA = vol.Schema({
    vol.Required("folder_name"): cv.string,
})

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Inicializa la integración y registra el servicio."""

    async def handle_update_component(call: ServiceCall):
        folder_name = call.data.get("folder_name").strip()

        if not folder_name or "/" in folder_name or "\\" in folder_name or folder_name in [".", ".."]:
            _LOGGER.error("Nombre de carpeta no válido: '%s'", folder_name)
            return

        custom_components_dir = hass.config.path("custom_components")
        target_component_dir = os.path.join(custom_components_dir, folder_name)

        # 1. Borra SOLAMENTE la carpeta del componente seleccionado
        if os.path.exists(target_component_dir):
            if os.path.isdir(target_component_dir):
                _LOGGER.info("Eliminando la carpeta previa del componente: %s", target_component_dir)
                await hass.async_add_executor_job(shutil.rmtree, target_component_dir)
            else:
                _LOGGER.warning("La ruta %s existe pero no es una carpeta.", target_component_dir)
                return

        os.makedirs(target_component_dir, exist_ok=True)

        # 2. Descarga desde GitHub
        api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{folder_name}?ref={GITHUB_BRANCH}"
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "HomeAssistant-GitHubUpdater"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.error("No se encontró la carpeta '%s' en GitHub. Status: %s", folder_name, response.status)
                    return

                files = await response.json()

            if not isinstance(files, list):
                _LOGGER.error("La ruta especificada en GitHub ('%s') no es una carpeta.", folder_name)
                return

            # 3. Guardar archivos
            for item in files:
                if item.get("type") == "file":
                    download_url = item.get("download_url")
                    file_name = item.get("name")
                    dest_file_path = os.path.join(target_component_dir, file_name)

                    async with session.get(download_url) as file_resp:
                        if file_resp.status == 200:
                            content = await file_resp.read()

                            def write_file():
                                with open(dest_file_path, "wb") as f:
                                    f.write(content)

                            await hass.async_add_executor_job(write_file)
                            _LOGGER.info("Archivo descargado: %s", file_name)
                        else:
                            _LOGGER.error("Error descargando archivo: %s", file_name)

        _LOGGER.info("Actualización completada exitosamente para la carpeta '%s'.", folder_name)

    # CORRECCIÓN AQUÍ: Usar async_register en lugar de register
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE,
        handle_update_component,
        schema=SERVICE_SCHEMA
    )

    return True