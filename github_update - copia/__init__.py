"""Componente de prueba descargado desde GitHub Updater."""
import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "mi_componente_prueba"

async def async_setup(hass, config):
    _LOGGER.info("¡El componente de prueba se ha cargado correctamente!")
    return True